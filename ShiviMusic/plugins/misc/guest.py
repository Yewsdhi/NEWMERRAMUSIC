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
# BOT INFO
# ==========================================

BOT_NAME = app.me.first_name or "Shivi Music"
BOT_USERNAME = (app.me.username or "").lstrip("@")

if not BOT_USERNAME:
    raise RuntimeError("Bot username is not available.")

BOT_LINK = f"https://t.me/{BOT_USERNAME}"
ADD_GROUP_LINK = f"{BOT_LINK}?startgroup=true"


# ==========================================
# PROMO TEXT
# ==========================================

ADD_ME_PROMO_TEXT = (
    f'❖ <a href="{BOT_LINK}">˹{BOT_NAME}˼ ♪</a> — '
    "𝖸𝗈𝗎𝗋 𝖯𝗋𝖾𝗆𝗂𝗎𝗆 𝖬𝗎𝗌𝗂𝖼 𝖲𝗍𝗋𝖾𝖺𝗆𝖾𝗋 𝖡𝗈𝗍 🎶\n\n"
    "▸ 𝖥𝖺𝗌𝗍 • 𝖫𝖺𝗀 𝖥𝗋𝖾𝖾 • 𝖭𝗈 𝖠𝖽𝗌 🍃\n"
    "▸ 𝖠𝗎𝗍𝗈-𝖯𝗅𝖺𝗒 • 𝖠𝗎𝖽𝗂𝗈 • 𝖵𝗂𝖽𝖾𝗈 🎥\n\n"
    f'➜ 𝖠𝖽𝖽 <a href="{BOT_LINK}">˹{BOT_NAME}˼ ♪</a> '
    "𝖳𝗈 𝖸𝗈𝗎𝗋 𝖦𝗋𝗈𝗎𝗉 & 𝖤𝗇𝗃𝗈𝗒 𝖧𝗂𝗀𝗁 𝖰𝗎𝖺𝗅𝗂𝗍𝗒 𝖲𝗈𝗇𝗀𝗌 🎶"
)


# ==========================================
# INLINE BUTTON
# ==========================================

def add_me_markup():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=f"➕ Add {BOT_NAME} To Your Group",
                    url=ADD_GROUP_LINK,
                    style=ButtonStyle.SUCCESS,
                )
            ]
        ]
    )


# ==========================================
# GUEST MESSAGE
# ==========================================

@app.on_guest_message()
async def guest_username_mention(client, message: Message):

    guest_query_id = getattr(message, "guest_query_id", None)

    if not guest_query_id:
        print("Guest query ID not found.")
        return

    try:
        article = InlineQueryResultArticle(
            id="shivi_music_promo",
            title=f"❖ {BOT_NAME} ♪",
            description=f"Tap to send {BOT_NAME} card 🎶",
            thumb_url="https://files.catbox.moe/qv2ob4.jpg",
            input_message_content=InputTextMessageContent(
                message_text=ADD_ME_PROMO_TEXT,
                parse_mode="html",
            ),
            reply_markup=add_me_markup(),
        )

        await client.answer_guest_query(
            guest_query_id,
            results=[article],
        )

        print("Guest query answered successfully.")

    except Exception as e:
        print(f"Guest query error: {e}")
