from pyrogram.enums import ParseMode
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
)

from ShiviMusic import app


# ==========================================================
# BOT USERNAME
# ==========================================================

BOT_USERNAME = "Queenhoneybot"
BOT_NAME = "QUEEN"


# ==========================================================
# GUEST MESSAGE
# ==========================================================

ADD_ME_PROMO_TEXT = (
    f'❖ <a href="https://t.me/{BOT_USERNAME}">˹{BOT_NAME}˼ ♪</a> — '
    '<b>𝐘ᴏᴜʀ 𝐏ʀᴇᴍɪᴜᴍ 𝐌ᴜsɪᴄ 𝐒ᴛʀᴇᴀᴍᴇʀ 𝐁ᴏᴛ 🍂</b>\n\n'

    '<blockquote>'
    '<b>▸ 𝐅ᴀsᴛ • 𝐋ᴀɢ 𝐅ʀᴇᴇ • 𝐍ᴏ 𝐀ᴅs 🍂</b>\n'
    '<b>▸ 𝐀ᴜᴛᴏ-𝐏ʟᴀʏ • 𝐀ᴜᴅɪᴏ • 𝐕ɪᴅᴇᴏ 🎥</b>'
    '</blockquote>\n\n'

    f'<b>◼️ 𝐀ᴅᴅ</b> '
    f'<a href="https://t.me/{BOT_USERNAME}">˹{BOT_NAME}˼ ♪</a> '
    '<b>𝐓ᴏ 𝐘ᴏᴜʀ 𝐆ʀᴏᴜᴘ & 𝐄ɴᴊᴏʏ 𝐇ɪɢʜ 𝐐ᴜᴀʟɪᴛʏ 𝐒ᴏɴɢ ❄️</b>'
)


# ==========================================================
# ADD ME BUTTON
# ==========================================================

def _add_me_markup():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="✙ ʌᴅᴅ ϻє ɪη ʏσυʀ ɢʀσυᴘ ✙",
                    url=f"https://t.me/{BOT_USERNAME}?startgroup=true",
                )
            ]
        ]
    )


# ==========================================================
# GUEST MODE
# ==========================================================

@app.on_guest_message()
async def guest_username_mention(_, message: Message):

    guest_query_id = getattr(
        message,
        "guest_query_id",
        None,
    )

    if not guest_query_id:
        print("Guest Mode: guest_query_id not found")
        return

    try:

        # --------------------------------------------------
        # KEYBOARD
        # --------------------------------------------------

        keyboard = _add_me_markup()

        # --------------------------------------------------
        # INLINE RESULT
        # --------------------------------------------------

        result = InlineQueryResultArticle(
            id="guest_music_bot",

            title=f"❖ {BOT_NAME} ♪",

            description=(
                f"@{BOT_USERNAME} • "
                "Add Me In Your Group 🎶"
            ),

            thumb_url="https://files.catbox.moe/qv2ob4.jpg",

            input_message_content=InputTextMessageContent(
                message_text=ADD_ME_PROMO_TEXT,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            ),

            reply_markup=keyboard,
        )

        # --------------------------------------------------
        # ANSWER GUEST QUERY
        # --------------------------------------------------

        await app.answer_guest_query(
            guest_query_id,
            result=result,
        )

        print(
            f"Guest Mode: Successfully answered "
            f"@{BOT_USERNAME}"
        )

    except Exception as e:

        print(
            f"Guest Mode Error: "
            f"{type(e).__name__}: {e}"
        )
