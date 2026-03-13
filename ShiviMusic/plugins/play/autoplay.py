import random
from pyrogram import filters
from pyrogram.types import Message
from youtubesearchpython import VideosSearch

from ShiviMusic import app
from ShiviMusic.core.call import call Shivi
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
        await message.reply_text("❌ **Autoplay Disabled**")
    else:
        await set_autoplay(chat_id, True)
        await message.reply_text("✅ **Autoplay Enabled**")


# -------------------- STREAM END EVENT -------------------- #

@call_py.on_stream_end()
async def stream_end_handler(_, update):
    chat_id = update.chat_id

    try:
        queue = await get_queue(chat_id)

        # अगर queue में song है → next song play
        if queue:
            return

        autoplay = await get_autoplay(chat_id)

        if not autoplay:
            return

        # YouTube random search
        search = VideosSearch("popular music", limit=20)
        results = search.result()["result"]

        if not results:
            return

        data = random.choice(results)

        title = data["title"]
        url = data["link"]

        await stream(
            chat_id,
            url,
            title
        )

        await app.send_message(
            chat_id,
            f"⏯ **Autoplay Started**\n\n🎵 **{title}**"
        )

    except Exception as e:
        print(f"Autoplay Error: {e}")
