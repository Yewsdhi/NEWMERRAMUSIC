import random

from pyrogram import filters
from pyrogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from config import LOGGER_ID as LOG_GROUP_ID
from ShiviMusic import app
from pyrogram.errors import RPCError


photo = [
    "https://files.catbox.moe/y2briy.jpg",
    "https://files.catbox.moe/1evnbn.jpg",
]


@app.on_message(filters.new_chat_members, group=2)
async def join_watcher(_, message):
    chat = message.chat

    # Check whether the bot itself was added
    for member in message.new_chat_members:
        if member.id != app.id:
            continue

        # Get member count safely
        try:
            count = await app.get_chat_members_count(chat.id)
        except RPCError:
            count = "Unknown"

        # Get group link safely
        link = None

        # Public username = direct Telegram link
        if chat.username:
            link = f"https://t.me/{chat.username}"
        else:
            # Private group: exporting invite link requires admin permission
            try:
                link = await app.export_chat_invite_link(chat.id)
            except RPCError:
                link = None

        # Display link
        if link:
            chat_link_text = f"[ᴄʟɪᴄᴋ]({link})"
        else:
            chat_link_text = "ᴘʀɪᴠᴀᴛᴇ ɢʀᴏᴜᴘ"

        added_by = (
            message.from_user.mention
            if message.from_user
            else "𝐔ɴᴋɴᴏᴡɴ 𝐔sᴇʀ"
        )

        username = (
            f"@{chat.username}"
            if chat.username
            else "𝐏ʀɪᴠᴀᴛᴇ 𝐂ʜᴀᴛ"
        )

        msg = (
            f"#𝗕𝗢𝗧_𝗔𝗗𝗗𝗘𝗗_𝗡𝗘𝗪_𝗚𝗥𝗢𝗨𝗣\n\n"
            f"⦿───────────────────⦿\n\n"
            f"◎ ᴄʜᴀᴛ ɴᴀᴍᴇ ▸ {chat.title}\n"
            f"◎ ᴄʜᴀᴛ ɪᴅ ▸ {chat.id}\n"
            f"◎ ᴄʜᴀᴛ ᴜsᴇʀɴᴀᴍᴇ ▸ {username}\n"
            f"◎ ᴄʜᴀᴛ ʟɪɴᴋ ▸ {chat_link_text}\n"
            f"◎ ɢʀᴏᴜᴘ ᴍᴇᴍʙᴇʀs ▸ {count}\n"
            f"◎ ᴀᴅᴅᴇᴅ ʙʏ ▸ {added_by}\n"
            f"⦿───────────────────⦿"
        )

        # Add link button only when a link exists
        reply_markup = None

        if link:
            reply_markup = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "#𝗚𝗥𝗢𝗨𝗣 #𝗟𝗜𝗡𝗞",
                        url=link
                    )
                ]
            ])

        try:
            await app.send_photo(
                LOG_GROUP_ID,
                photo=random.choice(photo),
                caption=msg,
                reply_markup=reply_markup,
            )
        except RPCError as e:
            print(f"Failed to send group log: {e}")


@app.on_message(filters.left_chat_member)
async def on_left_chat_member(_, message: Message):
    me = await app.get_me()

    if message.left_chat_member.id == me.id:
        remove_by = (
            message.from_user.mention
            if message.from_user
            else "𝐔ɴᴋɴᴏᴡɴ 𝐔sᴇʀ"
        )

        title = message.chat.title

        username = (
            f"@{message.chat.username}"
            if message.chat.username
            else "𝐏ʀɪᴠᴀᴛᴇ 𝐂ʜᴀᴛ"
        )

        chat_id = message.chat.id

        left = (
            f"✫ <b><u>#𝗟𝗘𝗙𝗧_𝗚𝗥𝗢𝗨𝗣</u></b> ✫\n\n"
            f"ᴄʜᴀᴛ ᴛɪᴛʟᴇ : {title}\n\n"
            f"ᴄʜᴀᴛ ɪᴅ : {chat_id}\n\n"
            f"ᴄʜᴀᴛ ᴜsᴇʀɴᴀᴍᴇ : {username}\n\n"
            f"ʀᴇᴍᴏᴠᴇᴅ ʙʏ : {remove_by}\n\n"
            f"ʙᴏᴛ : @{me.username}"
        )

        try:
            await app.send_photo(
                LOG_GROUP_ID,
                photo=random.choice(photo),
                caption=left,
            )
        except RPCError as e:
            print(f"Failed to send leave log: {e}")
