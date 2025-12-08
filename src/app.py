import asyncio
import logging
from telethon import TelegramClient

from config.settings import (
    API_HASH,
    API_ID,
    ALLOWED_USER_IDS,
    DB_CONFIG,
    GROUP_ID,
    MEDIA_DIR,
    MESSAGES_JSON,
    SESSION_NAME,
)
from handlers.commands import register_command_handler
from handlers.mentions import register_mention_handler
from handlers.messages import register_message_handler
from services.storage import load_messages


async def run():
    messages = await load_messages(MESSAGES_JSON)
    pending_responses = {}

    async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        await client.start()

        bot_user = await client.get_me()
        bot_username = bot_user.username
        bot_id = bot_user.id

        try:
            logging.info("Getting group entity with ID: %s", GROUP_ID)
            group = await client.get_entity(GROUP_ID)
            logging.info("Group entity obtained: %s", group)
        except ValueError as exc:
            logging.error("Error getting group entity: %s", exc)
            return

        register_message_handler(client, group, messages, MESSAGES_JSON, DB_CONFIG, bot_username, MEDIA_DIR)
        register_mention_handler(client, group, bot_username, bot_id, pending_responses)
        register_command_handler(client, ALLOWED_USER_IDS)

        logging.info("Listening for new messages and mentions...")
        await client.run_until_disconnected()


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()

