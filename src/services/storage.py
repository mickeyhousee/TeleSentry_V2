import json
import logging
import aiofiles


async def load_messages(path: str) -> list:
    """
    Load previously saved messages from disk. Returns an empty list if the file does not exist
    or cannot be decoded.
    """
    try:
        async with aiofiles.open(path, "r", encoding="utf-8") as file_handle:
            return json.loads(await file_handle.read())
    except FileNotFoundError:
        logging.info("%s not found, starting fresh.", path)
        return []
    except json.JSONDecodeError as exc:
        logging.error("Error decoding JSON from %s: %s", path, exc)
        return []


async def save_messages(path: str, messages: list) -> None:
    """Persist messages to disk in a readable JSON format."""
    async with aiofiles.open(path, "w", encoding="utf-8") as file_handle:
        await file_handle.write(json.dumps(messages, ensure_ascii=False, indent=4))
    logging.info("Messages saved to %s", path)

