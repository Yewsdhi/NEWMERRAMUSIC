import random
from pyrogram import filters
from pyrogram.types import Message
from py_yt import VideosSearch

from ShiviMusic import app
from ShiviMusic.core.call import Shivi
from ShiviMusic.utils.database import get_autoplay, set_autoplay
from ShiviMusic.utils.queue import get_queue
from ShiviMusic.utils.stream import stream


# -------------------- AUTOPLAY COMMAND -------------------- #

@app.on_message(filters.command("autoplay"))
async def autoplay_toggle(_, message: Message):
    chat_id = message.chat.id

    status = await get_autoplay(chat_id)

    if status:
        await set_autoplay(chat_id, False)
        return await message.reply_text(
            "❌ **AutoPlay Disabled**"
        )

    else:
        await set_autoplay(chat_id, True)
        return await message.reply_text(
            "✅ **AutoPlay Enabled**"
        )


# -------------------- AUTOPLAY FUNCTION -------------------- #

async def auto_play(chat_id):

    queue = await get_queue(chat_id)

    if queue:
        return

    autoplay = await get_autoplay(chat_id)

    if not autoplay:
        return

    try:
        results = VideosSearch("hindi songs", limit=50)
        data = results.result()["result"]

        video = random.choice(data)
        url = video["link"]

        stream_url = await stream(url)

        await Shivi.join_call(chat_id, stream_url)

    except Exception as e:
        print(f"Autoplay Error: {e}")
