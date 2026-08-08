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
#   GUEST BOTS (@-mention anywhere)
# ================================
# Telegram's "Guest Mode" lets a bot be summoned by tagging its
# @username in ANY chat — a group, a channel, or even a private DM
# between two other people — without the bot being a member of that
# chat at all. Telegram delivers this as a "guest message" and the
# bot gets exactly ONE reply via answer_guest_query().
#
# IMPORTANT (one-time setup, cannot be done from code):
#   Open @BotFather's Mini App (blue "Open" button, NOT /mybots text
#   menu) -> your bot -> Bot Settings -> Guest Mode -> Enable.
#   Without this toggle ON, Telegram will never send guest messages
#   to your bot, no matter what code is running.

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
