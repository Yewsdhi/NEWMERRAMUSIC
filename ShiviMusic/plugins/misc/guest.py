from pyrogram.enums import ButtonStyle, ParseMode
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
    "❖ ˹{name}˼ ♪ — <b>Your Premium Music Streamer Bot 🎶</b>\n\n"
    
    "<blockquote>▸ Fast • Lag Free • No Ads 🍃\n"
    "▸ Auto-Play • Audio • Video 🎥</blockquote>\n\n"
    
    "<b>➜ Add ˹{name}˼ ♪ To Your Group & Enjoy High Quality Songs 🎶</b>"
)


# ==========================================================
# BUTTONS
# ==========================================================

def _add_me_markup(username: str):

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="➕ Add Me In Your Group",
                    url=f"https://t.me/{username}?startgroup=true",
                    style=ButtonStyle.SUCCESS,
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎶 Open Music Bot",
                    url=f"https://t.me/{username}",
                    style=ButtonStyle.PRIMARY,
                )
            ],
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
        
