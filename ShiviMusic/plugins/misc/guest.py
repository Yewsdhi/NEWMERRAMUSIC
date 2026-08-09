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
#   GUEST BOTS (@username MENTION ANYWHERE)
# ==========================================

ADD_ME_PROMO_TEXT = (
    '❖ <a href="https://t.me/{username}">{name}</a> ♪ — '
    '𝖸𝗈𝗎𝗋 𝖯𝗋𝖾𝗆𝗂𝗎𝗆 𝖬𝗎𝗌𝗂𝖼 𝖲𝗍𝗋𝖾𝖺𝗆𝖾𝗋 𝖡𝗈𝗍 🎶\n\n'

    '<blockquote>'
    '▸ 𝖥𝖺𝗌𝗍 • 𝖫𝖺𝗀 𝖥𝗋𝖾𝖾 • 𝖭𝗈 𝖠𝖽𝗌 🍃\n'
    '▸ 𝖠𝗎𝗍𝗈-𝖯𝗅𝖺𝗒 • 𝖠𝗎𝖽𝗂𝗈 • 𝖵𝗂𝖽𝖾𝗈 🎥'
    '</blockquote>\n'

    '➜ <a href="https://t.me/{username}">{name}</a> 𝖳𝗈 𝖸𝗈𝗎𝗋 𝖦𝗋𝗈𝗎𝗉 & '
    '𝖤𝗇𝗃𝗈𝗒 𝖧𝗂𝗀𝗁 𝖰𝗎𝖺𝗅𝗂𝗍𝗒 𝖲𝗈𝗇𝗀𝗌 🎶'
)


def _add_me_markup(username: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="➕ Add me in your Group",
                    url=f"https://t.me/{username}?startgroup=true",
                    style=ButtonStyle.SUCCESS,
                )
            ]
        ]
    )


@app.on_guest_message()
async def guest_username_mention(_, message: Message):
    # Guest query ID is required to answer the guest request.
    guest_query_id = getattr(message, "guest_query_id", None)

    if not guest_query_id:
        return

    try:
        # Get bot information inside async handler.
        me = await app.get_me()

        username = me.username or ""
        name = me.first_name or "Music Bot"

        promo_text = ADD_ME_PROMO_TEXT.format(
            username=username,
            name=name,
        )

        result = InlineQueryResultArticle(
            title=f"❖ {name}",
            description="Tap to send the Add Me card in this chat 🎵",
            thumb_url="https://files.catbox.moe/qv2ob4.jpg",
            input_message_content=InputTextMessageContent(
                promo_text
            ),
            reply_markup=_add_me_markup(username),
        )

        await app.answer_guest_query(
            guest_query_id,
            result=result,
        )

    except Exception as e:
        print(f"Guest message error: {e}")
