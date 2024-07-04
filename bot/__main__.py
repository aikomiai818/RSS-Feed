import asyncio
from aiofiles import open as aiopen
from aiofiles.os import path as aiopath, remove as aioremove
from asyncio import gather, create_subprocess_exec
from os import execl as osexecl
from sys import executable
from time import time

from bot import bot, botStartTime, LOGGER, DATABASE_URL, scheduler
from .helper.ext_utils.bot_utils import cmd_exec
from .helper.ext_utils.db_handler import DbManager
from .helper.telegram_helper.filters import CustomFilters
from .helper.telegram_helper.message_utils import sendMessage, editMessage, sendFile
from .modules import exec, rss, shell, bot_settings
from pyrogram.filters import command
from pyrogram.handlers import MessageHandler

async def start(client, message):
    if await CustomFilters.authorized(client, message):
        await sendMessage(message, "Hello")

async def restart(_, message):
    restart_message = await sendMessage(message, "Restarting...")
    if scheduler.running:
        scheduler.shutdown(wait=False)
    proc1 = await create_subprocess_exec("python3", "update.py")
    await gather(proc1.wait())
    async with aiopen(".restartmsg", "w") as f:
        await f.write(f"{restart_message.chat.id}\n{restart_message.id}\n")
    osexecl(executable, executable, "-m", "bot")

async def ping(_, message):
    start_time = int(round(time() * 1000))
    reply = await sendMessage(message, "Starting Ping")
    end_time = int(round(time() * 1000))
    await editMessage(reply, f"{end_time - start_time} ms")

async def log(_, message):
    await sendFile(message, "log.txt")

async def restart_notification():
    if await aiopath.isfile(".restartmsg"):
        cmd = """remote_url=$(git config --get remote.origin.url) &&
            if echo "$remote_url" | grep -qE "github\\.com[:/](.*)/(.*?)(\\.git)?$"; then
                last_commit=$(git log -1 --pretty=format:'%h') &&
                commit_link="https://github.com/5hojib/RSS-Feed/commit/$last_commit" &&
                echo $commit_link;
            else
                echo "Failed to extract repository name and owner name from the remote URL.";
            fi"""
        
        result = await cmd_exec(cmd, True)
        commit_link = result[0]
        
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        try:
            await bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=f'<a href="{commit_link}">Restarted Successfully!</a>')
        except Exception as e:
            LOGGER.error(f"Failed to edit message: {e}")
        await aioremove(".restartmsg")

async def main():
    if DATABASE_URL:
        await DbManager().db_load()
    await restart_notification()
   
    bot.add_handler(MessageHandler(start, filters=command("start")))
    bot.add_handler(MessageHandler(log, filters=command("log") & CustomFilters.sudo))
    bot.add_handler(MessageHandler(restart, filters=command("restart") & CustomFilters.sudo))
    bot.add_handler(MessageHandler(ping, filters=command("ping") & CustomFilters.authorized))

    LOGGER.info("Bot Started!")

bot.loop.run_until_complete(main())
bot.loop.run_forever()
