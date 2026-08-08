from html import escape

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

async def get_bot_info():
    me = await app.get_me()

    bot_name = escape(me.first_name or "Shivi Music")
    bot_username = (me.username or "").lstrip("@")

    if not bot_username:
        raise RuntimeError("Bot username is not available.")

    bot_link = f"https://t.me/{bot_username}"
    add_group_link = f"{bot_link}?startgroup=true"

    return bot_name, bot_username, bot_link, add_group_link


# ==========================================
# PROMO TEXT
# ==========================================

def make_promo_text(bot_name, bot_link):
    return (
        f'❖ <a href="{bot_link}">˹{bot_name}˼ ♪</a> — '
        "𝖸𝗈𝗎𝗋 𝖯𝗋𝖾𝗆𝗂𝗎𝗆 𝖬𝗎𝗌𝗂𝖼 𝖲𝗍𝗋𝖾𝖺𝗆𝖾𝗋 𝖡𝗈𝗍 🎶\n\n"
        "▸ 𝖥𝖺𝗌𝗍 • 𝖫𝖺𝗀 𝖥𝗋𝖾𝖾 • 𝖭𝗈 𝖠𝖽𝗌 🍃\n"
        "▸ 𝖠𝗎𝗍𝗈-𝖯𝗅𝖺𝗒 • 𝖠𝗎𝖽𝗂𝗈 • 𝖵𝗂𝖽𝖾𝗈 🎥\n\n"
        f'➜ 𝖠𝖽𝖽 <a href="{bot_link}">˹{bot_name}˼ ♪</a> '
        "𝖳𝗈 𝖸𝗈𝗎𝗋 𝖦𝗋𝗈𝗎𝗉 & 𝖤𝗇𝗃𝗈𝗒 𝖧𝗂𝗀𝗁 𝖰𝗎𝖺𝗅𝗂𝗍𝗒 𝖲𝗈𝗇𝗀𝗌 🎶"
    )


# ==========================================
# INLINE BUTTON
# ==========================================

def add_me_markup(bot_name, add_group_link):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=f"➕ Add {bot_name} To Your Group",
                    url=add_group_link,
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
        # Get bot information safely
        bot_name, bot_username, bot_link, add_group_link = (
            await get_bot_info()
        )

        # Promo message
        promo_text = make_promo_text(
            bot_name,
            bot_link,
        )

        # Inline article
        article = InlineQueryResultArticle(
            id="shivi_music_promo",
            title=f"❖ {bot_name} ♪",
            description=f"Tap to send {bot_name} card 🎶",
            thumb_url="https://files.catbox.moe/qv2ob4.jpg",
            input_message_content=InputTextMessageContent(
                message_text=promo_text,
                parse_mode="html",
            ),
            reply_markup=add_me_markup(
                bot_name,
                add_group_link,
            ),
        )

        # Answer guest query
        await client.answer_guest_query(
            guest_query_id,
            results=[article],
        )

        print(
            f"Guest query answered successfully for @{bot_username}"
        )

    except Exception as e:
        print(f"Guest query error: {type(e).__name__}: {e}")
