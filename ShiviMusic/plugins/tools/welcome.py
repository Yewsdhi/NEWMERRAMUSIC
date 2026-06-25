# =======================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 🚀

# This source code is under MIT License 📜 Unauthorized forking, importing, or using this code without giving proper credit will result in legal action ⚠️
 
# 📩 DM for permission : @TheSigmaCoder
# =======================================================


from ShiviMusic import app

from pyrogram import filters, enums
from pyrogram.types import (
    ChatMemberUpdated,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
)

from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DB_URI

import asyncio
from logging import getLogger

LOGGER = getLogger(__name__)

mongo = AsyncIOMotorClient(MONGO_DB_URI)
db = mongo["Wel_DB"]
welcomedb = db["welcome_toggle_system"]

async def get_welcome(chat_id: int):
    data = await welcomedb.find_one({"chat_id": chat_id})
    if not data:
        return True
    return data.get("welcome", True)

async def enable_welcome(chat_id: int):
    await welcomedb.update_one(
        {"chat_id": chat_id},
        {"$set": {"welcome": True}},
        upsert=True
    )

async def disable_welcome(chat_id: int):
    await welcomedb.update_one(
        {"chat_id": chat_id},
        {"$set": {"welcome": False}},
        upsert=True
    )

class temp:
    MELCOW = {}

def circle(pfp, size=(720, 720), brightness_factor=1.4):
    pfp = pfp.resize(size).convert("RGBA")
    pfp = ImageEnhance.Brightness(pfp).enhance(brightness_factor)

    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)

    pfp.putalpha(mask)
    return pfp

def welcomepic(pic, user, chatname, id, uname, brightness_factor=1.3):
    background = Image.open("ShiviMusic/assets/wel2.png").convert("RGBA")

    pfp = Image.open(pic).convert("RGBA")
    pfp = circle(pfp, size=(720, 720), brightness_factor=brightness_factor)

    background.paste(pfp, (520, 420), pfp)

    draw = ImageDraw.Draw(background)

    font_path = "ShiviMusic/assets/font2.ttf"

    font_id = ImageFont.truetype(font_path, 100)
    font_username = ImageFont.truetype(font_path, 100)

    username_text = f"@{uname}" if uname else "Not Set"


    draw.text((1920, 1340), str(id), font=font_id, fill="#ffffff")
    draw.text((1920, 1480), username_text, font=font_username, fill="#ffffff")

    output_path = f"downloads/welcome_{id}.png"
    background.save(output_path)

    return output_path



@app.on_message(filters.command("welcome") & filters.group)
async def welcome_cmd(_, message: Message):

    chat = message.chat
    chat_id = chat.id

    user = await app.get_chat_member(chat_id, message.from_user.id)
    if user.status not in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
        return await message.reply_text("**» ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ʜᴀɴᴅʟᴇ ᴡᴇʟᴄᴏᴍᴇ ꜱʏꜱᴛᴇᴍ**")

    state = await get_welcome(chat_id)   
    status = "ᴇɴᴀʙʟᴇᴅ" if state else "ᴅɪꜱᴀʙʟᴇᴅ"

    btn = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("ᴇɴᴀʙʟᴇ", callback_data=f"wlc_on_{chat_id}"),
            InlineKeyboardButton("ᴅɪꜱᴀʙʟᴇ", callback_data=f"wlc_off_{chat_id}")
        ]
    ])

    await message.reply_text(
        f"» ᴄᴜʀʀᴇɴᴛʟʏ ᴡᴇʟᴄᴏᴍᴇ ꜱᴛᴀᴛᴜꜱ **{status}** ɪɴ **{chat.title}**",
        reply_markup=btn
    )

@app.on_chat_member_updated(filters.group, group=-3)
async def greet_new_member(_, member: ChatMemberUpdated):

    chat_id = member.chat.id
    is_enabled = await get_welcome(chat_id)
    if not is_enabled:
        return

    user = member.new_chat_member.user if member.new_chat_member else None
    if not user:
        return

    if member.new_chat_member and member.new_chat_member.status != "kicked":

        try:
            pic = await app.download_media(
                user.photo.big_file_id,
                file_name=f"pp{user.id}.png"
            )
        except:
            pic = "ShiviMusic/assets/upic.png"

        if temp.MELCOW.get(f"welcome-{chat_id}") is not None:
            try:
                await temp.MELCOW[f"welcome-{chat_id}"].delete()
            except Exception as e:
                LOGGER.error(e)

        try:
            welcomeimg = welcomepic(
                pic,
                user.first_name,
                member.chat.title,
                user.id,
                user.username,
            )

            # FIX
            count = await app.get_chat_members_count(chat_id)

            button_text = "๏ ᴠɪᴇᴡ ɴᴇᴡ ᴍᴇᴍʙᴇʀ ๏"
            add_button_text = "✙ ᴋɪᴅɴᴀᴘ ᴍᴇ ✙"

            deep_link = f"tg://openmessage?user_id={user.id}"
            add_link = f"https://t.me/{app.username}?startgroup=true"

            msg = await app.send_photo(
                chat_id,
                photo=welcomeimg,
                caption=f"""
**⎊─────☵ ᴡᴇʟᴄᴏᴍᴇ ☵─────⎊**

**▬▭▬▭▬▭▬▭▬▭▬▭▬▭▬**

**☉ ɴᴀᴍᴇ ⧽** {user.mention}
**☉ ɪᴅ ⧽** `{user.id}`
**☉ ᴜ_ɴᴀᴍᴇ ⧽** @{user.username if user.username else 'None'}
**☉ ᴛᴏᴛᴀʟ ᴍᴇᴍʙᴇʀs ⧽** {count}

**▬▭▬▭▬▭▬▭▬▭▬▭▬▭▬**

**⎉──────▢✭ 侖 ✭▢──────⎉**
""",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton(button_text, url=deep_link)],
                        [InlineKeyboardButton(add_button_text, url=add_link)],
                    ]
                ),
            )

            temp.MELCOW[f"welcome-{chat_id}"] = msg

            await asyncio.sleep(300)

            try:
                await msg.delete()
            except:
                pass

        except Exception as e:
            LOGGER.error(e)
