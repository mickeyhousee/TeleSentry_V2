import logging
import os
from typing import Awaitable, Callable

from tenacity import retry, stop_after_attempt, wait_exponential
from telethon import events, types
from telethon.tl.types import Channel, Chat, MessageMediaDocument, MessageMediaPhoto, MessageService, User

from config.settings import UPLOAD_API_URL
from services.database import insert_data_to_db, insert_score_to_db
from services.scoring import calculate_message_score, get_high_risk_users
from services.storage import save_messages
from services.uploader import upload_file_to_api
from utils.files import calculate_file_hash
from utils.text import translate_to_english


def _extract_urls(message):
    urls = []
    if message.entities:
        for entity in message.entities:
            if isinstance(entity, types.MessageEntityUrl):
                url_start = entity.offset
                url_end = entity.offset + entity.length
                url = message.message[url_start:url_end]
                urls.append(url)
    return urls


def _build_sender_details(user_obj):
    sender_name = "Unknown"
    sender_username = "Unknown"
    sender_type = "Unknown"

    if isinstance(user_obj, User):
        sender_name = f"{user_obj.first_name or ''} {user_obj.last_name or ''}".strip()
        sender_username = user_obj.username if user_obj.username else "Unknown"
        sender_type = "Person"
    elif isinstance(user_obj, (Chat, Channel)):
        sender_name = user_obj.title
        sender_username = user_obj.username if user_obj.username else "Unknown"
        sender_type = "Group/Channel"

    return sender_name, sender_username, sender_type


async def _download_photo(client, message, media_dir):
    file_path = os.path.join(media_dir, f"{message.id}.jpg")
    await client.download_media(message.media, file=file_path)
    return {
        "type": "Photo",
        "file": file_path,
        "mime_type": "image/jpeg",
        "hash": calculate_file_hash(file_path),
        "size": os.path.getsize(file_path),
    }


async def _download_document(client, message, media_dir):
    document = message.media.document
    file_name = None
    for attribute in document.attributes:
        if isinstance(attribute, types.DocumentAttributeFilename):
            file_name = attribute.file_name
            break
    if not file_name:
        file_name = f"{message.id}"

    file_path = os.path.join(media_dir, file_name)
    await client.download_media(message.media, file=file_path)
    return {
        "type": "Document",
        "file": file_path,
        "mime_type": document.mime_type,
        "hash": calculate_file_hash(file_path),
        "size": os.path.getsize(file_path),
    }


@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=10))
async def fetch_message_details(
    client,
    message,
    group,
    media_dir,
    uploader: Callable[[str, str], Awaitable[None]],
):
    if isinstance(message, MessageService):
        return None

    if not (message.message or message.media):
        return None

    sender_name = "Unknown"
    sender_username = "Unknown"
    sender_type = "Unknown"
    group_name = group.title if hasattr(group, "title") else "N/A"
    content = message.message or ""
    translated_content = translate_to_english(content) if content else ""
    urls = _extract_urls(message)
    attached_files = []

    if message.sender_id:
        try:
            user_obj = await client.get_entity(message.sender_id)
            sender_name, sender_username, sender_type = _build_sender_details(user_obj)
            logging.info("Sender details - Name: %s, Username: %s, Type: %s", sender_name, sender_username, sender_type)
        except Exception as exc:
            logging.error("Error getting user entity for user_id %s: %s", message.sender_id, exc)

    link = f"https://t.me/{group.username}/{message.id}" if hasattr(group, "username") and group.username else "N/A"

    if message.media:
        if isinstance(message.media, MessageMediaPhoto):
            try:
                photo_info = await _download_photo(client, message, media_dir)
                attached_files.append(photo_info)
            except Exception as exc:
                logging.error("Error downloading image: %s", exc)
        elif isinstance(message.media, MessageMediaDocument):
            try:
                document_info = await _download_document(client, message, media_dir)
                attached_files.append(document_info)
                if document_info["file"]:
                    await uploader(document_info["file"], UPLOAD_API_URL)
            except Exception as exc:
                logging.error("Error downloading document: %s", exc)

    return {
        "message_id": message.id,
        "date": str(message.date),
        "group_name": group_name,
        "sender": sender_name,
        "sender_username": sender_username,
        "sender_type": sender_type,
        "content": content,
        "translated_content": translated_content,
        "in_message_urls": urls,
        "attached_files": attached_files,
        "post_url": link,
    }


async def handle_new_message(event, client, group, messages, storage_path, db_config, bot_username, media_dir):
    message_data = await fetch_message_details(client, event.message, group, media_dir, upload_file_to_api)
    if not message_data:
        return

    messages.append(message_data)
    await save_messages(storage_path, messages)
    await insert_data_to_db(message_data, bot_username, db_config)
    
    # Calculate and store the message score (always insert, even if score is 0)
    try:
        high_risk_users = get_high_risk_users(db_config)
        score_details = calculate_message_score(message_data, db_config, high_risk_users)
        # Always insert score, even if it's 0, so messages can be evaluated in the ranking system
        await insert_score_to_db(message_data["message_id"], score_details, db_config)
        logging.info(
            f"Message {message_data['message_id']} scored: {score_details['total_score']} points "
            f"(sensitive terms: {score_details['sensitive_terms_count']}, "
            f"suspicious links: {score_details['suspicious_links_count']}, "
            f"repeated sharing: {score_details['repeated_sharing']}, "
            f"high-risk user: {score_details['high_risk_user']})"
        )
    except Exception as exc:
        logging.error(f"Error calculating message score: {exc}")


def register_message_handler(client, group, messages, storage_path, db_config, bot_username, media_dir):
    async def on_new_message(event):
        await handle_new_message(event, client, group, messages, storage_path, db_config, bot_username, media_dir)

    client.add_event_handler(on_new_message, events.NewMessage(chats=group))

