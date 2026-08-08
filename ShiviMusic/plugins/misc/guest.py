from html import escape

from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from ShiviMusic import app


# ==========================================
# INLINE PROMO
# ==========================================

@app.on_inline_query()
async def shivi_inline_promo(client, inline_query):

    try:
        # Get bot information
        me = await client.get_me()

        bot_name = escape(me.first_name or "Shivi Music")
        bot_username = me.username

        if not bot_username:
            return

        bot_link = f"https://t.me/{bot_username}"
        add_group_link = f"{bot_link}?startgroup=true"

        # ==================================
        # PROMO TEXT
        # ==================================

        promo_text = (
            f'❖ <a href="{bot_link}">˹{bot_name}˼ ♪</a> — '
            "𝖸𝗈𝗎𝗋 𝖯𝗋𝖾𝗆𝗂𝗎𝗆 𝖬𝗎𝗌𝗂𝖼 𝖲𝗍𝗋𝖾𝖺𝗆𝖾𝗋 𝖡𝗈𝗍 🎶\n\n"
            "▸ 𝖥𝖺𝗌𝗍 • 𝖫𝖺𝗀 𝖥𝗋𝖾𝖾 • 𝖭𝗈 𝖠𝖽𝗌 🍃\n"
            "▸ 𝖠𝗎𝗍𝗈-𝖯𝗅𝖺𝗒 • 𝖠𝗎𝖽𝗂𝗈 • 𝖵𝗂𝖽𝖾𝗈 🎥\n\n"
            f'➜ 𝖠𝖽𝖽 <a href="{bot_link}">˹{bot_name}˼ ♪</a> '
            "𝖳𝗈 𝖸𝗈𝗎𝗋 𝖦𝗋𝗈𝗎𝗉 & 𝖤𝗇𝗃𝗈𝗒 "
            "𝖧𝗂𝗀𝗁 𝖰𝗎𝖺𝗅𝗂𝗍𝗒 𝖲𝗈𝗇𝗀𝗌 🎶"
        )

        # ==================================
        # BUTTON
        # ==================================

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        f"➕ Add {bot_name} To Your Group",
                        url=add_group_link,
                    )
                ]
            ]
        )

        # ==================================
        # INLINE RESULT
        # ==================================

        result = InlineQueryResultArticle(
            id="shivi_music_promo",
            title=f"❖ {bot_name} ♪",
            description=f"Tap to send {bot_name} card 🎶",
            thumb_url="https://files.catbox.moe/qv2ob4.jpg",
            input_message_content=InputTextMessageContent(
                promo_text,
                parse_mode="html",
            ),
            reply_markup=keyboard,
        )

        await inline_query.answer(
            results=[result],
            cache_time=1,
            is_personal=True,
        )

    except Exception as e:
        print(f"Shivi inline error: {type(e).__name__}: {e}")
