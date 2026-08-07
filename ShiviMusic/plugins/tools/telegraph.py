import os
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ShiviMusic import app
import requests


def upload_file(file_path):
    url = "https://uguu.se/upload.php"
    try:
        with open(file_path, "rb") as f:
            files = {"files[]": f}
            response = requests.post(url, files=files)

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                file_url = data["files"][0]["url"]
                return True, file_url
            else:
                return False, "Upload failed on Uguu.se"
        else:
            return False, f"❖ ᴇʀʀᴏʀ : {response.status_code}"
    except Exception as e:
        return False, str(e)


@app.on_message(filters.command(["tgm", "tgt", "telegraph", "tl"]))
async def get_link_group(client, message):
    if not message.reply_to_message:
        return await message.reply_text(
            "❖ ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇᴅɪᴀ ᴛᴏ ᴜᴘʟᴏᴀᴅ."
        )

    media = message.reply_to_message
    file_size = 0
    file_name = "media_file"

    # Get File Size and File Name dynamically
    if media.photo:
        file_size = media.photo.file_size
        file_name = "photo.jpg"
    elif media.video:
        file_size = media.video.file_size
        file_name = getattr(media.video, 'file_name', "video.mp4")
    elif media.document:
        file_size = media.document.file_size
        file_name = getattr(media.document, 'file_name', "document.file")
    elif media.animation:
        file_size = media.animation.file_size
        file_name = getattr(media.animation, 'file_name', "animation.gif")
    elif media.audio:
        file_size = media.audio.file_size
        file_name = getattr(media.audio, 'file_name', "audio.mp3")

    if file_size > 200 * 1024 * 1024:
        return await message.reply_text("ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴍᴇᴅɪᴀ ғɪʟᴇ ᴜɴᴅᴇʀ 200 MB")

    # Calculate size in MB for the message
    size_mb = round(file_size / (1024 * 1024), 2)

    try:
        text = await message.reply("❍ ᴘʀᴏᴄᴇssɪɴɢ...")

        async def progress(current, total):
            try:
                await text.edit_text(f"❍ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ... {current * 100 / total:.1f}%")
            except Exception:
                pass

        try:
            local_path = await media.download(progress=progress)
            await text.edit_text("❍ ᴜᴘʟᴏᴀᴅɪɴɢ ᴛᴏ Uguu.se...")

            success, upload_path = upload_file(local_path)

            if success:
                # Formatting the text exactly as the screenshot
                caption = (
                    f"<b>𝐔ᴘʟᴏᴀᴅᴇᴅ 𝐒ᴜᴄᴄᴇssғᴜʟʟʏ!</b>\n\n"
                    f"➤ <b>𝐅ɪʟᴇ:</b> {file_name}\n"
                    f"➤ <b>𝐒ɪᴢᴇ:</b> {size_mb} 𝐌𝐁\n"
                    f"➤ <b>𝐒ᴇʀᴠɪᴄᴇ:</b> Uguu.se\n\n"
                    f"🔗 <a href='{upload_path}'>{upload_path}</a>"
                )

                await text.edit_text(
                    text=caption,
                    disable_web_page_preview=False, # This will show the image preview!
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "• 𝐔ɢᴜᴜ 𝐋ɪɴᴋ •",
                                    url=upload_path,
                                )
                            ]
                        ]
                    ),
                )
            else:
                await text.edit_text(
                    f"❖ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ ᴜᴘʟᴏᴀᴅɪɴɢ ʏᴏᴜʀ ғɪʟᴇ\n{upload_path}"
                )

            # Cleanup
            try:
                os.remove(local_path)
            except Exception:
                pass

        except Exception as e:
            await text.edit_text(f"❖ | ғɪʟᴇ ᴜᴘʟᴏᴀᴅ ғᴀɪʟᴇᴅ\n\n<i>❍ ʀᴇᴀsᴏɴ : {e}</i>")
            try:
                os.remove(local_path)
            except Exception:
                pass
            return
    except Exception:
        pass
