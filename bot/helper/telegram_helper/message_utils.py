from asyncio import sleep
from pyrogram.errors import FloodWait

from bot import config_dict, LOGGER, bot
from bot.helper.telegram_helper.button_build import ButtonMaker

async def sendMessage(message, text, buttons=None, block=True):
    try:
        return await message.reply(
            text=text,
            quote=True,
            disable_web_page_preview=True,
            disable_notification=True,
            reply_markup=buttons,
        )
    except FloodWait as f:
        LOGGER.warning(str(f))
        if block:
            await sleep(f.value * 1.2)
            return await sendMessage(message, text, buttons)
        return str(f)
    except Exception as e:
        LOGGER.error(str(e))
        return str(e)

async def editMessage(message, text, buttons=None, block=True):
    try:
        await message.edit(
            text=text, disable_web_page_preview=True, reply_markup=buttons
        )
    except FloodWait as f:
        LOGGER.warning(str(f))
        if block:
            await sleep(f.value * 1.2)
            return await editMessage(message, text, buttons)
        return str(f)
    except Exception as e:
        LOGGER.error(str(e))
        return str(e)

async def sendFile(message, file, caption=""):
    try:
        return await message.reply_document(
            document=file, quote=True, caption=caption, disable_notification=True
        )
    except FloodWait as f:
        LOGGER.warning(str(f))
        await sleep(f.value * 1.2)
        return await sendFile(message, file, caption)
    except Exception as e:
        LOGGER.error(str(e))
        return str(e)

async def sendRss(text, thumb, url):
    button = ButtonMaker()
    button.iButton("Enrol now", url)
    button = button.build_menu(1)
    try:
        return await bot.send_photo(
            chat_id=config_dict["RSS_CHAT"],
            photo=url,
            caption=text,
            reply_markup=button,
            disable_web_page_preview=True,
            disable_notification=True,
        )
    except FloodWait as f:
        LOGGER.warning(str(f))
        await sleep(f.value * 1.2)
        return await sendRss(text, thumb, url)
    except Exception as e:
        LOGGER.error(str(e))
        return str(e)

async def deleteMessage(message):
    try:
        await message.delete()
    except Exception as e:
        LOGGER.error(str(e))