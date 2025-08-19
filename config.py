import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

BOT_API = os.environ.get("BOT_API")
BOT_AUTH_TOKEN = os.environ.get("BOT_AUTH_TOKEN")
CHAT_LINK = os.environ.get("CHAT_LINK")
ADMIN_IDS = os.environ.get("ADMIN_IDS")
DOMAIN = os.environ.get("DOMAIN")
