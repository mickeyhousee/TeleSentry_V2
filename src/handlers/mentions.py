from telethon import events
from telethon.tl.types import MessageEntityMention, MessageEntityMentionName


async def send_notification(client, bot_id, sender, group_name, content, event):
    message = (
        f"You were mentioned or sent a private message by {sender} in the group {group_name} "
        f"with the message: {content}\nWould you like to respond? (yes/no)"
    )
    await client.send_message(bot_id, message)


async def handle_mention_or_pm(event, client, bot_id, sender, group_name, content, pending_responses):
    await send_notification(client, bot_id, sender, group_name, content, event)
    pending_responses[bot_id] = event

    @client.on(events.NewMessage(from_users=bot_id))
    async def response_handler(response_event):
        response_text = response_event.message.message.strip().lower()
        if response_text == "yes":
            await client.send_message(bot_id, "Type here what you would like to respond")
        elif response_text == "no":
            await client.send_message(bot_id, "No response will be sent.")
            client.remove_event_handler(response_handler)
        else:
            if bot_id in pending_responses:
                original_event = pending_responses[bot_id]
                await original_event.reply(response_event.message.message)
                del pending_responses[bot_id]
                client.remove_event_handler(response_handler)


async def handle_mentions(event, client, bot_username, bot_id, pending_responses):
    if not event.message.entities:
        return

    for entity in event.message.entities:
        if isinstance(entity, MessageEntityMentionName):
            mentioned_user = await client.get_entity(entity.user_id)
            if mentioned_user.username == bot_username:
                sender = mentioned_user.username
                group_name = event.chat.title if event.is_group else "Private"
                await handle_mention_or_pm(event, client, bot_id, sender, group_name, event.message.message, pending_responses)
                break
        elif isinstance(entity, MessageEntityMention):
            mention_text = event.message.message[entity.offset : entity.offset + entity.length]
            if mention_text == f"@{bot_username}":
                sender = event.sender_id
                group_name = event.chat.title if event.is_group else "Private"
                await handle_mention_or_pm(event, client, bot_id, sender, group_name, event.message.message, pending_responses)
                break


def register_mention_handler(client, group, bot_username, bot_id, pending_responses):
    async def on_mention(event):
        await handle_mentions(event, client, bot_username, bot_id, pending_responses)

    client.add_event_handler(on_mention, events.NewMessage(chats=group))

