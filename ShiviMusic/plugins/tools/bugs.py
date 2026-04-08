# ======================================================
# ©️ 2025-26 All Rights Reserved by Kirti 😎
# ======================================================

from datetime import datetime
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from config import OWNER_ID as owner_id, BUG_LOG_CHAT, BOT_USERNAME
from ShiviMusic import app


# ================== GET BUG TEXT ==================
def content(msg: Message):
    if not msg.text:
        return None
    parts = msg.text.split(maxsplit=1)
    return parts[1] if len(parts) > 1 else None


# ================== BUG COMMAND ==================
@app.on_message(filters.command("bug"))
async def bugs(_, msg: Message):

    # ❌ Private block
    if msg.chat.type == "private":
        return await msg.reply_text(
            "❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴡᴏʀᴋs ᴏɴʟʏ ɪɴ ɢʀᴏᴜᴘs."
        )

    bugs = content(msg)

    # ❌ No bug text
    if not bugs:
        return await msg.reply_text(
            "❌ ɴᴏ ʙᴜɢ ғᴏᴜɴᴅ.\n\n➜ ᴛʀʏ : `/bug music not playing`"
        )

    # 👤 User info
    user = msg.from_user
    user_id = user.id
    mention = f"[{user.first_name}](tg://user?id={user_id})"

    # 💬 Chat info
    chat_name = f"@{msg.chat.username}" if msg.chat.username else "ᴘʀɪᴠᴀᴛᴇ ɢʀᴏᴜᴘ"
    chat_id = msg.chat.id

    # 📅 Date
    date = datetime.utcnow().strftime("%d-%m-%Y")

    # 🐞 Bug Report Text
    bug_report = f"""
╭━〔 🐞 ʙᴜɢ ʀᴇᴘᴏʀᴛ 〕━╮

➤ ᴜsᴇʀ : {mention}
➤ ɪᴅ : `{user_id}`

➤ ᴄʜᴀᴛ : {chat_name}
➤ ᴄʜᴀᴛ ɪᴅ : `{chat_id}`

➤ ʙᴜɢ : `{bugs}`

➤ ᴅᴀᴛᴇ : {date}

╰━━━━━━━━━━━━━━━╯
"""

    # ================== USER REPLY ==================
    await msg.reply_text(
        f"""
╭⎯⎯⎯⎯⎯⎯⎯⎯⎯
│  ✦ ʙᴜɢ sᴜʙᴍɪᴛᴛᴇᴅ ✦
│
│  🐞 ʙᴜɢ : `{bugs}`
│
│  ⚡ ʏᴏᴜʀ ʀᴇᴘᴏʀᴛ ʜᴀs ʙᴇᴇɴ
│  sᴇɴᴛ ᴛᴏ ᴅᴇᴠᴇʟᴏᴘᴇʀ
│
╰⎯⎯⎯⎯⎯⎯⎯⎯⎯
""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "➕ ᴀᴅᴅ ᴍᴇ ʙᴀʙʏ",
                        url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "❌ ᴄʟᴏsᴇ",
                        callback_data="close_data"
                    )
                ],
            ]
        ),
        disable_web_page_preview=True
    )

    # ================== SAFE VIEW BUG BUTTON ==================
    view_url = msg.link if msg.chat.username else "https://t.me"

    # ================== SEND TO LOG ==================
    await app.send_photo(
        BUG_LOG_CHAT,-1003804980753,
        photo="https://files.catbox.moe/s8lc80.jpg",
        caption=bug_report,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🔍 ᴠɪᴇᴡ ʙᴜɢ", url=view_url),
                    InlineKeyboardButton(
                        "➕ ᴀᴅᴅ ᴍᴇ ʙᴀʙʏ",
                        url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "❌ ᴄʟᴏsᴇ",
                        callback_data="close_send_photo"
                    )
                ],
            ]
        ),
    )


# ================== CLOSE BUTTON ==================
@app.on_callback_query(filters.regex("close_send_photo"))
async def close_send_photo(_, query: CallbackQuery):
    member = await app.get_chat_member(query.message.chat.id, query.from_user.id)

    if member.status not in ["administrator", "creator"]:
        return await query.answer(
            "❌ ʏᴏᴜ ᴄᴀɴ'ᴛ ᴄʟᴏsᴇ ᴛʜɪs.",
            show_alert=True
        )

    await query.message.delete()


# ======================================================
# 🔥 Powered by Kirti Bots 😎
# ======================================================
