from aiofiles import open as aiopen
from aiofiles.os import path as aiopath, makedirs
from dotenv import dotenv_values
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from pymongo.errors import PyMongoError

from bot import (
    DATABASE_URL,
    rss_dict,
    LOGGER,
    bot_id,
    config_dict,
)


class DbManager:
    def __init__(self):
        self._err = False
        self._db = None
        self._conn = None
        self._connect()

    def _connect(self):
        try:
            self._conn = AsyncIOMotorClient(DATABASE_URL, server_api=ServerApi("1"))
            self._db = self._conn.rss
        except PyMongoError as e:
            LOGGER.error(f"Error in DB connection: {e}")
            self._err = True

    async def db_load(self):
        if self._err:
            return
        # Save bot settings
        try:
            await self._db.settings.config.replace_one(
                {"_id": bot_id}, config_dict, upsert=True
            )
        except Exception as e:
            LOGGER.error(f"DataBase Collection Error: {e}")
            self._conn.close
            return
        # Rss Data
        if await self._db.rss[bot_id].find_one():
            # return a dict ==> {_id, title: {link, last_feed, last_name, inf, exf, command, paused}
            rows = self._db.rss[bot_id].find({})
            async for row in rows:
                user_id = row["_id"]
                del row["_id"]
                rss_dict[user_id] = row
            LOGGER.info("Rss data has been imported from Database.")
        self._conn.close

    async def update_deploy_config(self):
        if self._err:
            return
        current_config = dict(dotenv_values("config.env"))
        await self._db.settings.deployConfig.replace_one(
            {"_id": bot_id}, current_config, upsert=True
        )
        self._conn.close

    async def update_config(self, dict_):
        if self._err:
            return
        await self._db.settings.config.update_one(
            {"_id": bot_id}, {"$set": dict_}, upsert=True
        )
        self._conn.close

    async def rss_update_all(self):
        if self._err:
            return
        for user_id in list(rss_dict.keys()):
            await self._db.rss[bot_id].replace_one(
                {"_id": user_id}, rss_dict[user_id], upsert=True
            )
        self._conn.close

    async def rss_update(self, user_id):
        if self._err:
            return
        await self._db.rss[bot_id].replace_one(
            {"_id": user_id}, rss_dict[user_id], upsert=True
        )
        self._conn.close

    async def rss_delete(self, user_id):
        if self._err:
            return
        await self._db.rss[bot_id].delete_one({"_id": user_id})
        self._conn.close

    async def trunc_table(self, name):
        if self._err:
            return
        await self._db[name][bot_id].drop()
        self._conn.close
