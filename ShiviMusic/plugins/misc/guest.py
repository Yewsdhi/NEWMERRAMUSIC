from pyrogram.enums import ButtonStyle
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
)

from ShiviMusic import app


PROMO_TEXT = (
    "❖ <b>{name}</b> ♪ — Your Premium Music Streamer Bot 🎶\n\n"
    "<blockquote>"
    "▸ Fast • Lag Free • No Ads 🍃\n"
    "▸ Auto-Play • Audio • Video 🎥"
    "</blockquote>\n\n"
    "➜ <b>{name}</b> "
    "<code>@{username}</code> "
    "To Your Group & Enjoy High Quality Songs 🎶"
)


def add_me_markup(username: str) -> InlineKeyboardMarkup:
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

        name = me.first_name or "Music Bot"
        username = me.username

        if not username:
            return

        promo_text = PROMO_TEXT.format(
            name=name,
            username=username,
        )

        result = InlineQueryResultArticle(
            title=f"❖ {name}",
            description="Add Me In Your Group 🎶",
            thumb_url="https://files.catbox.moe/qv2ob4.jpg",
            input_message_content=InputTextMessageContent(
                promo_text
            ),
            reply_markup=add_me_markup(username),
        )

        await app.answer_guest_query(
            guest_query_id,
            result=result,
        )

    except Exception as e:
        print(f"Guest Mode Error: {e}")
