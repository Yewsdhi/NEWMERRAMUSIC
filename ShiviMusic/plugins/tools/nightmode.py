# -----------------------------------------------
# 🔸 CharviMusic Project
# 🔹 Developed & Maintained by: Charvi Bots (https://github.com/CharviBots)
# 📅 Copyright © 2022 – All Rights Reserved
#
# 📖 License:
# This source code is open for educational and non-commercial use ONLY.
# You are required to retain this credit in all copies or substantial portions of this file.
# Commercial use, redistribution, or removal of this notice is strictly prohibited
# without prior written permission from the author.
#
# ❤️ Made with dedication and love by CharviBots
# -----------------------------------------------
import random 
from pyrogram import filters, Client, enums
from ShiviMusic import app
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery 
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram.types import ChatPermissions
from ShiviMusic.core.nightmodedb import nightdb, nightmode_on, nightmode_off, get_nightchats 


CLOSE_CHAT = ChatPermissions(
    can_send_messages=False,
    can_send_media_messages=False,
    can_send_polls=False,
    can_change_info=False,
    can_add_web_page_previews=False,
    can_pin_messages=False,
    can_invite_users=False
)

OPEN_CHAT = ChatPermissions(
    can_send_messages=True,
    can_send_media_messages=True,
    can_send_polls=True,
    can_change_info=True,
    can_add_web_page_previews=True,
    can_pin_messages=True,
    can_invite_users=True
)

#  1. Nightmode Setup 
buttons = InlineKeyboardMarkup(
    [[
        InlineKeyboardButton("๏ ᴇɴᴀʙʟᴇ ๏", callback_data="add_night"),
        InlineKeyboardButton("๏ ᴅɪsᴀʙʟᴇ ๏", callback_data="rm_night")
    ]]
)

#  2. Inline Support & Update 
NIGHT_MSG_BUTTONS = InlineKeyboardMarkup(
    [[
        InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ", url="https://t.me/annu_support"), 
        InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇs", url="https://t.me/annu_updates") 
    ]]
)


@app.on_message(filters.command("nightmode") & filters.group)
async def _nightmode(_, message):
    return await message.reply_photo(
        photo="https://n.uguu.se/PbzKsnAJ.jpg", 
        caption="**⚙️ ɴɪɢʜᴛᴍᴏᴅᴇ sᴇᴛᴛɪɴɢs**\n\n**ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ᴛᴏ ᴄᴏɴᴛʀᴏʟ ɴɪɢʜᴛᴍᴏᴅᴇ sᴇᴛᴛɪɴɢs ғᴏʀ ᴛʜɪs ᴄʜᴀᴛ.**",
        parse_mode=enums.ParseMode.MARKDOWN,
        reply_markup=buttons
    )


@app.on_callback_query(filters.regex("^(add_night|rm_night)$"))
async def nightcb(_, query: CallbackQuery):
    data = query.data 
    chat_id = query.message.chat.id
    user_id = query.from_user.id

    check_night = await nightdb.find_one({"chat_id": chat_id})

    administrators = []
    async for m in app.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
        administrators.append(m.user.id)

    if user_id not in administrators:
        return await query.answer("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ!", show_alert=True)

    if data == "add_night":
        if check_night:
            await query.message.edit_caption(
                caption="**🌕 ɴɪɢʜᴛᴍᴏᴅᴇ ɪs ᴀʟʀᴇᴀᴅʏ ᴇɴᴀʙʟᴇᴅ ɪɴ ᴛʜɪs ᴄʜᴀᴛ.**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await nightmode_on(chat_id)
            await query.message.edit_caption(
                caption=(
                    "**✅ ɴɪɢʜᴛᴍᴏᴅᴇ ᴀᴄᴛɪᴠᴀᴛᴇᴅ!**\n\n"
                    "**ᴛʜɪs ɢʀᴏᴜᴘ ᴡɪʟʟ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ʟᴏᴄᴋ ᴀᴛ 12:00 ᴀᴍ & ᴜɴʟᴏᴄᴋ ᴀᴛ 06:00 ᴀᴍ [ɪsᴛ] ᴛᴏ ᴍᴀɪɴᴛᴀɪɴ ᴘᴇᴀᴄᴇ.**"
                ),
                parse_mode=enums.ParseMode.MARKDOWN
            )

    elif data == "rm_night":
        if check_night:
            await nightmode_off(chat_id)
            await query.message.edit_caption(
                caption="**❌ ɴɪɢʜᴛᴍᴏᴅᴇ ᴅᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ!**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_caption(
                caption="**🌑 ɴɪɢʜᴛᴍᴏᴅᴇ ɪs ᴀʟʀᴇᴀᴅʏ ᴛᴜʀɴᴇᴅ ᴏғғ.**",
                parse_mode=enums.ParseMode.MARKDOWN
            )


async def start_nightmode():
    schats = await get_nightchats()
    for chat in schats:
        chat_id = int(chat["chat_id"])
        try:
            await app.send_photo(
                chat_id,
                photo="https://d.uguu.se/agsYnJwN.jpg", 
                caption=(
                    "**🌌 ɢᴏᴏᴅ ɴɪɢʜᴛ ᴇᴠᴇʀʏᴏɴᴇ!**\n"
                    "**━─────────────────━**\n\n"
                    "**✨ ᴛɪᴍᴇ ᴛᴏ ᴛᴜʀɴ ᴏғғ ʏᴏᴜʀ sᴄʀᴇᴇɴs ᴀɴᴅ ᴄᴀᴛᴄʜ sᴏᴍᴇ ᴘᴇᴀᴄᴇғᴜʟ ᴅʀᴇᴀᴍs. ᴍᴀʏ ʏᴏᴜʀ sʟᴇᴇᴘ ʙᴇ sᴡᴇᴇᴛ ᴀɴᴅ ʀᴇsᴛғᴜʟ.**\n\n"
                    "**🔒 ɢʀᴏᴜᴘ ɪs ɴᴏᴡ ᴄʟᴏsᴇᴅ.**\n"
                    "**• ɴᴏ ᴍᴇssᴀɢᴇs ᴄᴀɴ ʙᴇ sᴇɴᴛ ᴜɴᴛɪʟ ᴍᴏʀɴɪɴɢ. sᴇᴇ ʏᴏᴜ ᴀʟʟ ᴛᴏᴍᴏʀʀᴏᴡ!**"
                ),
                parse_mode=enums.ParseMode.MARKDOWN,
                reply_markup=NIGHT_MSG_BUTTONS
            )
            await app.set_chat_permissions(chat_id, CLOSE_CHAT)
        except Exception as e:
            print(f"Unable to close group {chat_id}: {e}")


async def close_nightmode():
    schats = await get_nightchats()
    for chat in schats:
        chat_id = int(chat["chat_id"])
        try:
            await app.send_photo(
                chat_id,
                photo="https://d.uguu.se/CPlUJSEp.jpg", 
                caption=(
                    "**🌅 ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ ᴇᴠᴇʀʏᴏɴᴇ..!**\n"
                    "**━─────────────────━**\n\n"
                    "**✨ ᴀ ʙᴇᴀᴜᴛɪғᴜʟ ɴᴇᴡ ᴅᴀʏ ʜᴀs ᴀʀʀɪᴠᴇᴅ. ᴍᴀʏ ᴛʜɪs ᴅᴀʏ ʙʀɪɴɢ ᴇɴᴅʟᴇss ᴏᴘᴘᴏʀᴛᴜɴɪᴛɪᴇs, ᴊᴏʏ, ᴀɴᴅ sᴜᴄᴄᴇss ᴛᴏ ʏᴏᴜʀ ʟɪғᴇ.**\n\n"
                    "**🔓 ɢʀᴏᴜᴘ ɪs ɴᴏᴡ ᴏᴘᴇɴ.**\n"
                    "**• ғᴇᴇʟ ғʀᴇᴇ ᴛᴏ ᴄʜᴀᴛ, sʜᴀʀᴇ, ᴀɴᴅ sᴛᴀʏ ᴘᴏsɪᴛɪᴠᴇ!**"
                ),
                parse_mode=enums.ParseMode.MARKDOWN,
                reply_markup=NIGHT_MSG_BUTTONS
            )
            await app.set_chat_permissions(chat_id, OPEN_CHAT)
        except Exception as e:
            print(f"Unable to open group {chat_id}: {e}")


scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
scheduler.add_job(start_nightmode, trigger="cron", hour=23, minute=59)
scheduler.add_job(close_nightmode, trigger="cron", hour=6, minute=1)
scheduler.start()
                       
