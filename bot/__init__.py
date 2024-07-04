from apscheduler.schedulers.asyncio import AsyncIOScheduler
from asyncio import get_event_loop
from dotenv import dotenv_values
from logging import (
    getLogger,
    FileHandler,
    StreamHandler,
    INFO,
    basicConfig,
    error as log_error,
    info as log_info,
    ERROR,
)
from os import environ
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pyrogram import Client as tgClient, enums
from socket import setdefaulttimeout
from time import time
from tzlocal import get_localzone
from uvloop import install

# Set up uvloop and default socket timeout
install()
setdefaulttimeout(600)
user_data = {}
rss_dict = {}

# Configure logging
basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[FileHandler("log.txt"), StreamHandler()],
    level=INFO,
)

LOGGER = getLogger(__name__)
getLogger("requests").setLevel(INFO)
getLogger("urllib3").setLevel(INFO)
getLogger("pyrogram").setLevel(ERROR)
getLogger("httpx").setLevel(ERROR)
getLogger("pymongo").setLevel(ERROR)

botStartTime = time()
bot_loop = get_event_loop()

# Load environment variables
BOT_TOKEN = environ.get("BOT_TOKEN", "")
if not BOT_TOKEN:
    log_error("BOT_TOKEN variable is missing! Exiting now")
    exit(1)
bot_id = BOT_TOKEN.split(":", 1)[0]

DATABASE_URL = environ.get("DATABASE_URL", "")
config_dict = {}
if DATABASE_URL:
    try:
        conn = MongoClient(DATABASE_URL, server_api=ServerApi("1"))
        db = conn.rss
        current_config = dict(dotenv_values("config.env"))
        old_config = db.settings.deployConfig.find_one({"_id": bot_id})
        if old_config:
            del old_config["_id"]
        if old_config and old_config != current_config:
            db.settings.deployConfig.replace_one(
                {"_id": bot_id}, current_config, upsert=True
            )
        else:
            db.settings.deployConfig.replace_one(
                {"_id": bot_id}, current_config, upsert=True
            )
        if config_data := db.settings.config.find_one({"_id": bot_id}):
            del config_data["_id"]
            for key, value in config_data.items():
                environ[key] = str(value)
        if file_data := db.settings.files.find_one({"_id": bot_id}):
            del file_data["_id"]
            for key, value in file_data.items():
                if value:
                    file_path = key.replace("__", ".")
                    with open(file_path, "wb+") as f:
                        f.write(value)
        conn.close()
    except Exception as e:
        LOGGER.error(f"Database ERROR: {e}")

OWNER_ID = environ.get("OWNER_ID", "")
if not OWNER_ID:
    log_error("OWNER_ID variable is missing! Exiting now")
    exit(1)
OWNER_ID = int(OWNER_ID)

TELEGRAM_API = environ.get("TELEGRAM_API", "")
if not TELEGRAM_API:
    log_error("TELEGRAM_API variable is missing! Exiting now")
    exit(1)
TELEGRAM_API = int(TELEGRAM_API)

TELEGRAM_HASH = environ.get("TELEGRAM_HASH", "")
if not TELEGRAM_HASH:
    log_error("TELEGRAM_HASH variable is missing! Exiting now")
    exit(1)

RSS_CHAT = environ.get("RSS_CHAT", "")
RSS_CHAT = int(RSS_CHAT) if RSS_CHAT and (RSS_CHAT.isdigit() or RSS_CHAT.startswith("-")) else ""

RSS_DELAY = int(environ.get("RSS_DELAY", 600))

UPSTREAM_REPO = environ.get("UPSTREAM_REPO", "")
UPSTREAM_BRANCH = environ.get("UPSTREAM_BRANCH", "master")

config_dict.update({
    "BOT_TOKEN": BOT_TOKEN,
    "DATABASE_URL": DATABASE_URL,
    "RSS_CHAT": RSS_CHAT,
    "RSS_DELAY": RSS_DELAY,
    "TELEGRAM_API": TELEGRAM_API,
    "TELEGRAM_HASH": TELEGRAM_HASH,
    "UPSTREAM_REPO": UPSTREAM_REPO,
    "UPSTREAM_BRANCH": UPSTREAM_BRANCH,
    "OWNER_ID": OWNER_ID
})

log_info("Creating client from BOT_TOKEN")
bot = tgClient(
    "bot",
    TELEGRAM_API,
    TELEGRAM_HASH,
    bot_token=BOT_TOKEN,
    workers=1000,
    parse_mode=enums.ParseMode.HTML,
    max_concurrent_transmissions=10,
).start()
bot_name = bot.me.username

scheduler = AsyncIOScheduler(timezone=str(get_localzone()), event_loop=bot_loop)
