import asyncio
import random
import time
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from py_yt import VideosSearch

import config
from ShiviMusic import app
from ShiviMusic.misc import _boot_
from ShiviMusic.plugins.sudo.sudoers import sudoers_list
from ShiviMusic.utils import bot_sys_stats
from ShiviMusic.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    get_served_chats,
    get_served_users,
    is_banned_user,
    is_on_off,
)
from ShiviMusic.utils.decorators.language import LanguageStart
from ShiviMusic.utils.formatters import get_readable_time
from ShiviMusic.utils.inline import help_pannel, private_panel, start_panel
from strings import get_string
from config import BANNED_USERS

# ================= IMAGE CONFIG ================= #

SHIVI_IMG = [
    "https://files.catbox.moe/8l8n9g.jpg",
    "https://files.catbox.moe/3b4h2k.jpg",
    "https://files.catbox.moe/7x2p1q.jpg",
]

BADNAM_IMG = [
    "https://files.catbox.moe/2k1h3j.jpg",
    "https://files.catbox.moe/9p8l7m.jpg",
]

EFFECT_IDS = [
    5046509860389126442,
    5107584321108051014,
    5104841245755180586,
    5159385139981059251,
]

# ================= SAFE IMAGE ================= #

def get_img(img_list):
    try:
        return random.choice(img_list)
    except:
        return "https://files.catbox.moe/8l8n9g.jpg"


# ================= START PM ================= #

@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    await add_served_user(message.from_user.id)

    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]

        # HELP PANEL
        if name.startswith("help"):
            keyboard = help_pannel(_)
            await message.reply_photo(
                get_img(SHIVI_IMG),
                caption=_['help_1'].format(config.SUPPORT_CHAT),
                reply_markup=keyboard,
                message_effect_id=random.choice(EFFECT_IDS),
            )

        # SUDO LIST
        elif name.startswith("sud"):
            await sudoers_list(client=client, message=message, _=_)

        # SONG INFO
        elif name.startswith("inf"):
            try:
                query = name.replace("info_", "", 1)

                results = VideosSearch(query, limit=1)
                data = await results.next()

                if not data["result"]:
                    return await message.reply_text("❌ No results found")

                result = data["result"][0]

                title = result.get("title", "Unknown")
                duration = result.get("duration", "Unknown")
                views = result.get("viewCount", {}).get("short", "0")
                thumbnail = result.get("thumbnails", [{}])[0].get("url", "")
                link = result.get("link", "")
                channel = result.get("channel", {}).get("name", "Unknown")

                text = f"""
🎧 **{title}**
⏱ Duration: {duration}
👁 Views: {views}
📺 Channel: {channel}
"""

                buttons = InlineKeyboardMarkup([
                    [InlineKeyboardButton("▶️ Watch", url=link)]
                ])

                await message.reply_photo(
                    thumbnail or get_img(SHIVI_IMG),
                    caption=text,
                    reply_markup=buttons
                )

            except Exception as e:
                await message.reply_text(f"Error: {e}")

    else:
        out = private_panel(_)

        served_chats = len(await get_served_chats())
        served_users = len(await get_served_users())
        UP, CPU, RAM, DISK = await bot_sys_stats()

        await message.reply_photo(
            get_img(BADNAM_IMG),
            caption=_["start_2"].format(
                message.from_user.mention,
                app.mention,
                UP, DISK, CPU, RAM,
                served_users,
                served_chats
            ),
            reply_markup=InlineKeyboardMarkup(out),
            message_effect_id=random.choice(EFFECT_IDS),
        )


# ================= START GROUP ================= #

@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    out = start_panel(_)
    uptime = int(time.time() - _boot_)

    await message.reply_photo(
        get_img(SHIVI_IMG),
        caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
        reply_markup=InlineKeyboardMarkup(out),
    )

    return await add_served_chat(message.chat.id)


# ================= WELCOME ================= #

@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)

            # BAN CHECK
            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except:
                    pass

            # BOT ADDED
            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)

                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(_["start_5"])
                    return await app.leave_chat(message.chat.id)

                out = start_panel(_)

                await message.reply_photo(
                    get_img(SHIVI_IMG),
                    caption=_["start_3"].format(
                        message.from_user.mention,
                        app.mention,
                        message.chat.title,
                        app.mention,
                    ),
                    reply_markup=InlineKeyboardMarkup(out),
                )

                await add_served_chat(message.chat.id)
                await message.stop_propagation()

        except Exception as e:
            print(e)
