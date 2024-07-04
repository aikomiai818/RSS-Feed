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

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
bot_id = BOT_TOKEN.split(":", 1)[0]

config_dict = {}

UPSTREAM_REPO = "https://github.com/5hojib/RSS-Feed"
UPSTREAM_BRANCH = "master"

if os.path.exists(".git"):
    run(["rm", "-rf", ".git"])

update = run([
    f"git init -q && "
    f"git config --global user.email yesiamshojib@gmail.com && "
    f"git config --global user.name 5hojib && "
    f"git add . && "
    f"git commit -sm update -q && "
    f"git remote add origin {UPSTREAM_REPO} && "
    f"git fetch origin -q && "
    f"git reset --hard origin/{UPSTREAM_BRANCH} -q"
], shell=True)

if update.returncode == 0:
    info("Successfully updated with the latest commit from UPSTREAM_REPO")
else:
    error("Something went wrong while updating. Check if UPSTREAM_REPO is valid.")