import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
MONGO_DB_URL = os.getenv("MONGO_DB_URL")
DEV_ID = os.getenv("DEV_ID")
