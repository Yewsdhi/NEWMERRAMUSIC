

from ShiviMusic import app
from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


START_IMG = "https://files.catbox.moe/qv2ob4.jpg"


@app.on_message(
    filters.command("start") & filters.private
)
async def start_handler(_, message):

    # Telegram se bot ki information
    me = await app.get_me()

    bot_name = me.first_name or "Music Bot"
    username = me.username or ""

    user_name = (
        message.from_user.first_name
        if message.from_user
        else "User"
    )

    text = (
        f"🎶 <b>{bot_name} for {user_name}</b>\n\n"
        f"Thanks for the shout-out, {user_name}! "
        "I'm a music bot for Telegram — stream from "
        "YouTube, Spotify, Apple Music, SoundCloud, "
        "Deezer, JioSaavn and more, right inside any group voice chat.\n\n"
        "👇 Tap below to add me to your group."
    )

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "➕ Add Me To Your Group",
                    url=f"https://t.me/{username}?startgroup=true"
                )
            ]
        ]
    )

    await message.reply_photo(
        photo=START_IMG,
        caption=text,
        reply_markup=buttons
    )
