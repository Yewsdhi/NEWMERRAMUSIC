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

me = await app.get_me()

ADD_ME_PROMO_TEXT = (
    '❖ <a href="https://t.me/{username}">{name}</a> ♪ — '
    '𝖸𝗈𝗎𝗋 𝖯𝗋𝖾𝗆𝗂𝗎𝗆 𝖬𝗎𝗌𝗂𝖼 𝖲𝗍𝗋𝖾𝖺𝗆𝖾𝗋 𝖡𝗈𝗍 🎶\n\n'

    '<blockquote>'
    '▸ 𝖥𝖺𝗌𝗍 • 𝖫𝖺𝗀 𝖥𝗋𝖾𝖾 • 𝖭𝗈 𝖠𝖽𝗌 🍃\n'
    '▸ 𝖠𝗎𝗍𝗈-𝖯𝗅𝖺𝗒 • 𝖠𝗎𝖽𝗂𝗈 • 𝖵𝗂𝖽𝖾𝗈 🎥'
    '</blockquote>\n'

    '➜ <a href="https://t.me/{username}">{name}</a> 𝖳𝗈 𝖸𝗈𝗎𝗋 𝖦𝗋𝗈𝗎𝗉 & '
    '𝖤𝗇𝗃𝗈𝗒 𝖧𝗂𝗀𝗁 𝖰𝗎𝖺𝗅𝗂𝗍𝗒 𝖲𝗈𝗇𝗀𝗌 🎶'
).format(
    username=me.username,
    name=me.first_name
)


def _add_me_markup() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="➕ 𝗔𝗱𝗱 𝗠𝗲 𝗧𝗼 𝗬𝗼𝘂𝗿 𝗚𝗿𝗼𝘂𝗽 ➕",
                    url=f"https://t.me/{app.username}?startgroup=true",
                    style=ButtonStyle.SUCCESS,
                )
            ]
        ]
    )


@app.on_guest_message()
async def guest_username_mention(_, message: Message):
    # message.guest_query_id is the id you must answer with, exactly once.
    if not message.guest_query_id:
        return

    result = InlineQueryResultArticle(
        title="❖ 𝗗𝗼𝗼𝗺 𝗠𝘂𝘀𝗶𝗰",
        description="Tap to send the Add Me card in this chat 🎵",
        thumb_url="https://files.catbox.moe/qv2ob4.jpg",
        input_message_content=InputTextMessageContent(ADD_ME_PROMO_TEXT),
        reply_markup=_add_me_markup(),
    )

    try:
        await app.answer_guest_query(message.guest_query_id, result=result)
    except Exception:
        pass
