import os
from dotenv import load_dotenv, dotenv_values
from logging import (
    FileHandler,
    StreamHandler,
    INFO,
    basicConfig,
    error,
    info,
    getLogger,
    ERROR,
)
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from subprocess import run

getLogger("pymongo").setLevel(ERROR)

basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[FileHandler("log.txt"), StreamHandler()],
    level=INFO,
)

if os.path.exists("log.txt"):
    with open("log.txt", "r+") as f:
        f.truncate(0)

load_dotenv("config.env", override=True)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
bot_id = BOT_TOKEN.split(":", 1)[0]

DATABASE_URL = os.environ.get("DATABASE_URL", "")

config_dict = {}

if DATABASE_URL:
    try:
        conn = MongoClient(DATABASE_URL, server_api=ServerApi("1"))
        db = conn.mltb
        old_config = db.settings.deployConfig.find_one({"_id": bot_id})
        config_dict = db.settings.config.find_one({"_id": bot_id})

        if old_config:
            del old_config["_id"]

        if old_config is None or old_config == dict(dotenv_values("config.env")):
            if config_dict:
                os.environ["UPSTREAM_BRANCH"] = config_dict.get("UPSTREAM_BRANCH", "")

        conn.close()
    except Exception as e:
        error(f"Database ERROR: {e}")

UPSTREAM_REPO = "https://github.com/5hojib/RSS-Feed"
UPSTREAM_BRANCH = os.environ.get("UPSTREAM_BRANCH", "")

if os.path.exists(".git"):
    run(["rm", "-rf", ".git"])

update = run(
    [
        f"git init -q "
        f"&& git config --global user.email yesiamshojib@gmail.com "
        f"&& git config --global user.name 5hojib "
        f"&& git add . "
        f"&& git commit -sm update -q "
        f"&& git remote add origin {UPSTREAM_REPO} "
        f"&& git fetch origin -q "
        f"&& git reset --hard origin/{UPSTREAM_BRANCH} -q"
    ],
    shell=True,
)

if update.returncode == 0:
    info("Successfully updated with the latest commit from UPSTREAM_REPO")
else:
    error("Something went wrong while updating. Check if UPSTREAM_REPO is valid.")