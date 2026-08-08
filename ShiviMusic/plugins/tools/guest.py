# ShiviMusic/plugins/guest.py

from ShiviMusic import app
from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


START_IMG = "https://files.catbox.moe/qv2ob4.jpg"


@app.on_message(filters.command("start") & filters.private)
async def guest_start(client, message):

    try:
        me = await client.get_me()

        bot_name = me.first_name or "Music Bot"
        bot_username = me.username

        user_name = "User"

        if message.from_user:
            user_name = (
                message.from_user.first_name
                or "User"
            )

        text = (
            f"🎶 <b>{bot_name} for {user_name}</b>\n\n"
            f"Thanks for the shout-out, "
            f"{user_name}! I'm a music bot for Telegram — "
            "stream from YouTube, Spotify, Apple Music, "
            "SoundCloud, Deezer, JioSaavn and more, "
            "right inside any group voice chat.\n\n"
            "👇 Tap below to add me to your group."
        )

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "➕ Add Me To Your Group",
                        url=(
                            f"https://t.me/"
                            f"{bot_username}"
                            f"?startgroup=true"
                        ),
                    )
                ]
            ]
        )

        await message.reply_photo(
            photo=START_IMG,
            caption=text,
            reply_markup=buttons,
        )

    except Exception as e:
        print(f"[Guest Start Error] {e}")
