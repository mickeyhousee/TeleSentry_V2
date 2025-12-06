import os
import json
import asyncio
import logging
import hashlib
from datetime import datetime
from deep_translator import GoogleTranslator
from telethon import TelegramClient, events, types
from telethon.tl.types import Channel, Chat, User, MessageService, MessageMediaPhoto, MessageMediaDocument, MessageEntityMention, MessageEntityMentionName
from telethon.errors.rpcerrorlist import UserNotMutualContactError, UserPrivacyRestrictedError
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv
import mysql.connector
import aiofiles
import aiohttp # for requests

# Load environment variables from .env file
load_dotenv()

# Configure logging for debugging and monitoring
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Read API ID and hash from environment variables
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')

# Group ID to listen to messages
group_id = int(os.getenv('GROUP_ID'))

# List to store messages
messages = []

# Directory to save the images and files
media_dir = 'files'
os.makedirs(media_dir, exist_ok=True)

# Database connection details from environment variables
db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

# Function to translate text to English
def translate_to_english(text):
    try:
        translator = GoogleTranslator(source='auto', target='en')
        translation = translator.translate(text)
        logging.debug(f"Original: {text} | Translated: {translation}")
        return translation
    except Exception as e:
        logging.error(f"Error translating text: {e}")
        return text

# Function to calculate the hash of a file for integrity and uniqueness
def calculate_file_hash(file_path):
    hash_algo = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_algo.update(chunk)
        return hash_algo.hexdigest()
    except Exception as e:
        logging.error(f"Error calculating hash: {e}")
        return None

# Retry to handle potential failures in fetching message details
@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=10))
async def fetch_message_details(client, message, group):
    # Ignore service messages
    if isinstance(message, MessageService):
        return None

    # Process only if the message has content or media
    if message.message or message.media:
        sender_name = 'Unknown'
        sender_username = 'Unknown'
        sender_type = 'Unknown'
        group_name = group.title if hasattr(group, 'title') else 'N/A'
        content = message.message if message.message else ''
        translated_content = translate_to_english(content) if content else ''
        urls = []

        # Get sender details
        if message.sender_id:
            try:
                user = await client.get_entity(message.sender_id)
                if isinstance(user, User):
                    sender_name = f'{user.first_name or ""} {user.last_name or ""}'.strip()
                    sender_username = user.username if user.username else 'Unknown'
                    sender_type = 'Person'
                elif isinstance(user, (Chat, Channel)):
                    sender_name = user.title
                    sender_username = user.username if user.username else 'Unknown'
                    sender_type = 'Group/Channel'
                logging.info(f"Sender details - Name: {sender_name}, Username: {sender_username}, Type: {sender_type}")
            except UserNotMutualContactError:
                logging.error(f"UserNotMutualContactError: Cannot get entity for user_id {message.sender_id}. User is not a mutual contact.")
            except UserPrivacyRestrictedError:
                logging.error(f"UserPrivacyRestrictedError: Cannot get entity for user_id {message.sender_id}. User's privacy settings restrict this.")
            except Exception as e:
                logging.error(f"Error getting user entity for user_id {message.sender_id}: {e}")

        # Extract URLs from message
        if message.entities:
            for entity in message.entities:
                if isinstance(entity, types.MessageEntityUrl):
                    url_start = entity.offset
                    url_end = entity.offset + entity.length
                    url = message.message[url_start:url_end]
                    urls.append(url)

        # Generate message link if group has a username
        link = f'https://t.me/{group.username}/{message.id}' if hasattr(group, 'username') and group.username else 'N/A'

        attached_files = []

        # Handle media attached to the message
        if message.media:
            if isinstance(message.media, MessageMediaPhoto):
                try:
                    file_path = os.path.join(media_dir, f"{message.id}.jpg")
                    await client.download_media(message.media, file=file_path)
                    file_hash = calculate_file_hash(file_path)
                    attached_files.append({
                        'type': 'Photo',
                        'file': file_path,
                        'mime_type': 'image/jpeg',
                        'hash': file_hash,
                        'size': os.path.getsize(file_path)
                    })
                except Exception as e:
                    logging.error(f"Error downloading image: {e}")
            elif isinstance(message.media, MessageMediaDocument):
                try:
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
                    file_hash = calculate_file_hash(file_path)
                    attached_files.append({
                        'type': 'Document',
                        'file': file_path,
                        'mime_type': document.mime_type,
                        'hash': file_hash,
                        'size': os.path.getsize(file_path)
                    })
                    await upload_file_to_api(file_path)
                except Exception as e:
                    logging.error(f"Error downloading document: {e}")

        # Compile message data into a dictionary
        message_data = {
            'message_id': message.id,
            'date': str(message.date),
            'group_name': group_name,
            'sender': sender_name,
            'sender_username': sender_username,
            'sender_type': sender_type,
            'content': content,
            'translated_content': translated_content,
            'in_message_urls': urls,
            'attached_files': attached_files,
            'post_url': link,
        }

        return message_data
    return None

# Function to save messages to a JSON file
async def save_messages_to_file(messages):
    async with aiofiles.open('messages.json', 'w', encoding='utf-8') as f:
        await f.write(json.dumps(messages, ensure_ascii=False, indent=4))
        logging.info("Messages saved in messages.json")

# Handle new messages by fetching details and saving to file and database
async def handle_new_message(event, client, group):
    message_data = await fetch_message_details(client, event.message, group)
    if message_data:
        messages.append(message_data)
        await save_messages_to_file(messages)
        await insert_data_to_db(message_data)

# Insert message data into the database with necessary checks
async def insert_data_to_db(message_data):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        # Queries to insert or update records in the database
        group_query = "INSERT INTO `group` (group_name) VALUES (%s) ON DUPLICATE KEY UPDATE group_name = VALUES(group_name)"
        user_query = "INSERT INTO `user` (username, name) VALUES (%s, %s) ON DUPLICATE KEY UPDATE name = VALUES(name)"
        file_query = "INSERT INTO files (file_name, file_type, hash) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE file_name = VALUES(file_name), file_type = VALUES(file_type)"
        content_query = """INSERT INTO content (id_message, date_message, content, translated_content, file_id, id_user, id_group, id_bot) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        link_query = "INSERT INTO links (link, message_id) VALUES (%s, %s)"
        bot_query = "INSERT INTO bot (name) VALUES (%s) ON DUPLICATE KEY UPDATE name = VALUES(name)"

        # Insert or update bot details
        cursor.execute(bot_query, (bot_username,))
        cursor.execute("SELECT id FROM bot WHERE name = %s", (bot_username,))
        result = cursor.fetchone()
        bot_id = result[0] if result else None

        # Insert or update group details
        cursor.execute(group_query, (message_data["group_name"],))
        cursor.execute("SELECT group_id FROM `group` WHERE group_name = %s", (message_data["group_name"],))
        result = cursor.fetchone()
        group_id = result[0] if result else None

        # Insert or update user details
        cursor.execute(user_query, (message_data["sender_username"], message_data["sender"]))
        cursor.execute("SELECT id_user FROM `user` WHERE username = %s", (message_data["sender_username"],))
        result = cursor.fetchone()
        user_id = result[0] if result else None

        # Insert or update file details
        file_id = None
        for attached_file in message_data["attached_files"]:
            file_name = attached_file["file"]
            file_type = attached_file["mime_type"]
            file_hash = attached_file["hash"]
            cursor.execute(file_query, (file_name, file_type, file_hash))
            cursor.execute("SELECT file_id FROM files WHERE hash = %s", (file_hash,))
            result = cursor.fetchone()
            if result:
                file_id = result[0]

        # Insert content details
        cursor.execute(content_query, (message_data["message_id"], message_data["date"], message_data["content"], 
                                       message_data["translated_content"], file_id, user_id, group_id, bot_id))

        # Insert link details
        for link in message_data["in_message_urls"]:
            cursor.execute(link_query, (link, message_data["message_id"]))

        # Commit all the changes to the database
        conn.commit()
    except mysql.connector.Error as err:
        logging.error(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

# Notification function when mentioned or PM
async def send_notification(client, bot_id, sender, group_name, content, event):
    message = f"You were mentioned or sent a private message by {sender} in the group {group_name} with the message: {content}\nWould you like to respond? (yes/no)"
    await client.send_message(bot_id, message)

# State to manage the interaction
pending_responses = {}

# Function to handle mentions or private messages
async def handle_mention_or_pm(event, client, bot_id, sender, group_name, content):
    global pending_responses
    await send_notification(client, bot_id, sender, group_name, content, event)
    pending_responses[bot_id] = event

    @client.on(events.NewMessage(from_users=bot_id))
    async def response_handler(response_event):
        global pending_responses
        response_text = response_event.message.message.strip().lower()
        if response_text == 'yes':
            await client.send_message(bot_id, "Type here what you would like to respond")
        elif response_text == 'no':
            await client.send_message(bot_id, "No response will be sent.")
            client.remove_event_handler(response_handler)
        else:
            if bot_id in pending_responses:
                original_event = pending_responses[bot_id]
                await original_event.reply(response_event.message.message)
                del pending_responses[bot_id]
                client.remove_event_handler(response_handler)

# Handle mentions of the bot in messages and respond
async def handle_mentions(event, client, bot_username, bot_id):
    if event.message.entities:
        for entity in event.message.entities:
            if isinstance(entity, MessageEntityMentionName):
                mentioned_user = await client.get_entity(entity.user_id)
                if mentioned_user.username == bot_username:
                    sender = mentioned_user.username
                    group_name = event.chat.title if event.is_group else 'Private'
                    await handle_mention_or_pm(event, client, bot_id, sender, group_name, event.message.message)
                    break
            elif isinstance(entity, MessageEntityMention):
                mention_text = event.message.message[entity.offset:entity.offset + entity.length]
                if mention_text == f"@{bot_username}":
                    sender = event.sender_id
                    group_name = event.chat.title if event.is_group else 'Private'
                    await handle_mention_or_pm(event, client, bot_id, sender, group_name, event.message.message)
                    break

# List of user IDs allowed to send messages through the bot
ALLOWED_USER_IDS = [5863587369, 5726800402]  

# Function to handle the send message command
async def handle_send_message_command(event, client):
    if event.sender_id not in ALLOWED_USER_IDS:
        return

    if event.message.message.startswith("@jonnyyy envia mensagem para"):
        try:
            command_parts = event.message.message.split(" ")
            group_id = int(command_parts[4])
            message_content_index = event.message.message.index("com a mensagem") + len("com a mensagem ")
            message_content = event.message.message[message_content_index:]

            await client.send_message(group_id, message_content)
            await event.respond(f"Mensagem enviada para o grupo {group_id}")
        except Exception as e:
            logging.error(f"Erro ao processar comando de envio de mensagem: {e}")
            await event.respond("Erro ao tentar enviar a mensagem. Verifique o comando e tente novamente.")

# Function to register the command handler
def register_command_handler(client):
    client.add_event_handler(lambda event: handle_send_message_command(event, client), events.NewMessage())


# Function to send files through api leakanalizer
async def upload_file_to_api(file_path):
    # Using async to handle varios ficheiros 
    api_url = 'http://127.0.0.1:8000/uploadfile/'
    try:
        async with aiohttp.ClientSession() as session: #http request
            # 'rb' = Read Binary mode
            with open(file_path, 'rb') as f:
                files = {'file', f}
                async with session.post(api_url, data=files) as response:
                    if response.status == 200:
                        logging.info(f"Files {file_path} upload successfully")
                    else:
                        logging.error(f"Failed to upload {file_path}. Status code: {response.status}")
    except Exception as e:
        logging.error(f"Error uploading file {file_path} to API: {e}")

# Main function to run the Telegram client
async def run():
    global group, messages, bot_username

    async with TelegramClient('session_name', api_id, api_hash) as client:
        await client.start()

        # Get bot username for identification
        bot_user = await client.get_me()
        bot_username = bot_user.username
        bot_id = bot_user.id

        try:
            logging.info(f"Getting group entity with ID: {group_id}")
            group = await client.get_entity(group_id)
            logging.info(f"Group entity obtained: {group}")
        except ValueError as e:
            logging.error(f"Error getting group entity: {e}")
            return

        # Add event handler for new messages
        client.add_event_handler(
            lambda event: handle_new_message(event, client, group),
            events.NewMessage(chats=group)
        )

        # Add event handler for mentions
        client.add_event_handler(
            lambda event: handle_mentions(event, client, bot_username, bot_id),
            events.NewMessage(chats=group)
        )

        # Register the command handler
        register_command_handler(client)

        # Load previous messages from JSON file
        logging.info("Loading previous messages from messages.json...")
        try:
            async with aiofiles.open('messages.json', 'r', encoding='utf-8') as f:
                messages = json.loads(await f.read())
        except FileNotFoundError:
            logging.info("messages.json not found, starting fresh.")
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON from messages.json: {e}")
            messages = []

        # Start listening for new messages and mentions
        logging.info("Listening for new messages and mentions...")
        await client.run_until_disconnected()

# Run the main function
if __name__ == '__main__':
    asyncio.run(run())
