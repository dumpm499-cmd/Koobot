import os
from dotenv import load_dotenv

load_dotenv()

# Telegram API credentials (get from https://my.telegram.org)
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")

# Bot token from @BotFather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# MongoDB connection string
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "filesearchbot")

# The channel where all files are stored (use integer ID, e.g., -1001234567890)
DB_CHANNEL_ID = int(os.environ.get("DB_CHANNEL_ID", "0"))

# Force join: channel username WITHOUT @, e.g., "mychannel"
# Leave empty to disable force join
FORCE_JOIN_CHANNEL = os.environ.get("FORCE_JOIN_CHANNEL", "")

# Admin user IDs (comma-separated telegram user IDs)
ADMINS = [int(x.strip()) for x in os.environ.get("ADMINS", "").split(",") if x.strip()]

# How many results to show per page
RESULTS_PER_PAGE = int(os.environ.get("RESULTS_PER_PAGE", "10"))
