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
# GUEST MESSAGE
# ==========================================================

ADD_ME_PROMO_TEXT = (
    "❖ <a href=\"https://t.me/{@Queenhoneybot}\">˹{QUEEN}˼ ♪</a> — <b>𝐘ᴏᴜʀ 𝐏ʀᴇᴍɪᴜᴍ 𝐌ᴜsɪᴄ 𝐒ᴛʀᴇᴍᴀʀ 𝐁ᴏᴛ 🍂</b>\n\n"
    
    "<blockquote><b>▸ 𝐅ᴀsᴛ • 𝐋ᴀɢ 𝐅ʀᴇᴇ • 𝐍ᴏ 𝐀ᴅs 🍂</b>\n"
    "<b>▸ 𝐀ᴜᴛᴏ-𝐏ʟᴀʏ • 𝐀ᴜᴅɪᴏ • 𝐕ɪᴅᴇᴏ 🎥</b></blockquote>\n\n"
    
    "<b>◼️ 𝐀ᴅᴅ</b> <a href=\"https://t.me/{@Queenhoneybot}\">˹{QUEEN}˼ ♪</a> <b>𝐓ᴏ 𝐘ᴏᴜʀ 𝐆ʀᴏᴜᴘ & 𝐄ɴᴊᴏʏ 𝐇ɪɢʜ 𝐐ᴜᴀʟɪᴛʏ 𝐒ᴏɴɢ ❄️</b>"
)


# ==========================================================
# BUTTONS
# ==========================================================

def _add_me_markup(username: str):

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="✙ ʌᴅᴅ ϻє ɪη ʏσυʀ ɢʀσυᴘ ✙",
                    url=f"https://t.me/{username}?startgroup=true",
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
        return

    try:

        # --------------------------------------------------
        # GET BOT INFORMATION 
        # --------------------------------------------------

        me = await app.get_me()

        # Full bot name 
        name = me.first_name or "Music Bot"

        if me.last_name:
            name = f"{name} {me.last_name}"

        # Bot username
        username = me.username

        if not username:
            return

        # --------------------------------------------------
        # CREATE MESSAGE
        # --------------------------------------------------

        promo_text = ADD_ME_PROMO_TEXT.format(
            name=name,
            username=username,
        )

        # --------------------------------------------------
        # KEYBOARD
        # --------------------------------------------------

        keyboard = _add_me_markup(username)

        # --------------------------------------------------
        # INLINE RESULT
        # --------------------------------------------------

        result = InlineQueryResultArticle(
            title=f"❖ {name} ♪",
            description=f"@{username} • Add Me In Your Group 🎶",
            thumb_url="https://files.catbox.moe/qv2ob4.jpg",

            input_message_content=InputTextMessageContent(
                message_text=promo_text,
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

    except Exception as e:

        print(
            f"Guest Mode Error: {type(e).__name__}: {e}"
        )
        
