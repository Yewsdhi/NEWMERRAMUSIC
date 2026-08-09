from pyrogram.enums import ButtonStyle
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
)

from ShiviMusic import app


# ==========================================
#        GUEST BOT MENTION CARD
# ==========================================

PROMO_TEXT = (
    "❖ <b>{name}</b> ♪ — Your Premium Music Streamer Bot 🎶\n\n"

    "<blockquote>"
    "▸ <b>Fast • Lag Free • No Ads</b> 🍃\n"
    "▸ <b>Auto-Play • Audio • Video</b> 🎥"
    "</blockquote>\n"

    "➜ <b>Add {name} To Your Group & "
    "Enjoy High Quality Songs 🎶</b>"
)


def add_me_button(username: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="➕ Add Me In Your Group",
                    url=f"https://t.me/{username}?startgroup=true",
                    style=ButtonStyle.SUCCESS,
                )
            ]
        ]
    )


@app.on_guest_message()
async def guest_username_mention(_, message: Message):

    guest_query_id = getattr(message, "guest_query_id", None)

    if not guest_query_id:
        return

    try:
        me = await app.get_me()

        username = me.username or ""
        name = me.first_name or "Shivi Music"

        promo_text = PROMO_TEXT.format(
            name=name,
        )

        result = InlineQueryResultArticle(
            title=f"❖ {name} ♪",
            description="Your Premium Music Streamer Bot 🎶",
            thumb_url="https://files.catbox.moe/qv2ob4.jpg",
            input_message_content=InputTextMessageContent(
                promo_text
            ),
            reply_markup=add_me_button(username),
        )

        await app.answer_guest_query(
            guest_query_id,
            result=result,
        )

    except Exception as e:
        print(f"Guest Mention Error: {e}")
