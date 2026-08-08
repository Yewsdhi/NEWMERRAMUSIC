from pyrogram.enums import ButtonStyle
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
)

from ShiviMusic import app


# ================================
#        BOT INFORMATION
# ================================

BOT_NAME = app.me.first_name
BOT_USERNAME = app.username.lstrip("@")

BOT_LINK = f"https://t.me/{BOT_USERNAME}"
ADD_GROUP_LINK = f"{BOT_LINK}?startgroup=true"


# ================================
#        PROMO MESSAGE
# ================================

ADD_ME_PROMO_TEXT = (
    f'❖ <a href="{BOT_LINK}">˹{BOT_NAME}˼ ♪</a> — '
    "𝖸𝗈𝗎𝗋 𝖯𝗋𝖾𝗆𝗂𝗎𝗆 𝖬𝗎𝗌𝗂𝖼 𝖲𝗍𝗋𝖾𝖺𝗆𝖾𝗋 𝖡𝗈𝗍 🎶\n\n"

    "▸ 𝖥𝖺𝗌𝗍 • 𝖫𝖺𝗀 𝖥𝗋𝖾𝖾 • 𝖭𝗈 𝖠𝖽𝗌 🍃\n"
    "▸ 𝖠𝗎𝗍𝗈-𝖯𝗅𝖺𝗒 • 𝖠𝗎𝖽𝗂𝗈 • 𝖵𝗂𝖽𝖾𝗈 🎥\n\n"

    f'➜ 𝖠𝖽𝖽 <a href="{BOT_LINK}">˹{BOT_NAME}˼ ♪</a> '
    "𝖳𝗈 𝖸𝗈𝗎𝗋 𝖦𝗋𝗈𝗎𝗉 & 𝖤𝗇𝗃𝗈𝗒 𝖧𝗂𝗀𝗁 𝖰𝗎𝖺𝗅𝗂𝗍𝗒 𝖲𝗈𝗇𝗀𝗌 🎶"
)


# ================================
#        ADD BUTTON
# ================================

def _add_me_markup() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=f"➕ 𝖠𝖽𝖽 {BOT_NAME} 𝖳𝗈 𝖸𝗈𝗎𝗋 𝖦𝗋𝗈𝗎𝗉 ➕",
                    url=ADD_GROUP_LINK,
                    style=ButtonStyle.SUCCESS,
                )
            ]
        ]
    )


# ================================
#        GUEST MESSAGE
# ================================

@app.on_guest_message()
async def guest_username_mention(_, message: Message):

    guest_query_id = getattr(message, "guest_query_id", None)

    if not guest_query_id:
        return

    result = InlineQueryResultArticle(
        title=f"❖ {BOT_NAME} ♪",
        description=f"𝖳𝖺𝗉 𝗍𝗈 𝖲𝖾𝗇𝖽 𝖳𝗁𝖾 {BOT_NAME} 𝖢𝖺𝗋𝖽 🎶",
        thumb_url="https://files.catbox.moe/qv2ob4.jpg",
        input_message_content=InputTextMessageContent(
            ADD_ME_PROMO_TEXT,
            parse_mode="html",
        ),
        reply_markup=_add_me_markup(),
    )

    try:
        await app.answer_guest_query(
            guest_query_id,
            result=result,
        )
    except Exception:
        pass
