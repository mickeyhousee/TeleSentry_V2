import logging
import os
from dotenv import load_dotenv

# Load environment variables once for the entire application
load_dotenv()

# Basic logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Telegram client configuration
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME", "session_name")

# Target group/channel to monitor
GROUP_ID = int(os.getenv("GROUP_ID", "0"))

# Files and persistence
MEDIA_DIR = os.getenv("MEDIA_DIR", "files")
MESSAGES_JSON = os.getenv("MESSAGES_JSON", "messages.json")
UPLOAD_API_URL = os.getenv("UPLOAD_API_URL", "http://127.0.0.1:8000/uploadfile/")

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

# Allowed users for bot commands
ALLOWED_USER_IDS = [5863587369, 5726800402]

# Ensure required directories exist
os.makedirs(MEDIA_DIR, exist_ok=True)

