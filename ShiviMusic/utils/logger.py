from pyrogram.enums import ParseMode, ChatMemberStatus
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from ShiviMusic import app
from ShiviMusic.utils.database import is_on_off
from config import LOGGER_ID


async def play_logs(message, streamtype, thumbnail=None):
    if await is_on_off(2):

        owner_id = "Unknown"
        owner_username = None
        group_link = None

        # Group Link
        try:
            if message.chat.username:
                group_link = f"https://t.me/{message.chat.username}"
            else:
                group_link = await app.export_chat_invite_link(
                    message.chat.id
                )
        except:
            pass

        # Owner Details
        try:
            async for member in app.get_chat_members(
                message.chat.id,
                filter="administrators"
            ):
                if member.status == ChatMemberStatus.OWNER:
                    owner_id = member.user.id
                    owner_username = member.user.username
                    break
        except:
            pass

        logger_text = f"""
<b>❖ {app.mention} ᴘʟᴀʏ ʟᴏɢ</b>

<b>● ᴄʜᴀᴛ ɪᴅ ➠</b> <code>{message.chat.id}</code>
<b>● ᴄʜᴀᴛ ɴᴀᴍᴇ ➠</b> {message.chat.title}

<b>● ᴄʜᴀᴛ ᴜsᴇʀɴᴀᴍᴇ ➠</b> @{message.chat.username if message.chat.username else 'Private'}

<b>● ᴏᴡɴᴇʀ ɪᴅ ➠</b> <code>{owner_id}</code>
<b>● ᴏᴡɴᴇʀ ➠</b> @{owner_username if owner_username else 'No Username'}

<b>● ᴜsᴇʀ ɪᴅ ➠</b> <code>{message.from_user.id}</code>
<b>● ɴᴀᴍᴇ ➠</b> {message.from_user.mention}

<b>● ᴜsᴇʀɴᴀᴍᴇ ➠</b> @{message.from_user.username if message.from_user.username else 'None'}

<b>● ǫᴜᴇʀʏ ➠</b> {message.text.split(None, 1)[1]}
<b>● sᴛʀᴇᴀᴍᴛʏᴘᴇ ➠</b> {streamtype}
"""

        buttons = []

        # Group Button
        if group_link:
            buttons.append(
                InlineKeyboardButton(
                    "ᴄʜᴀᴛ ʟɪɴᴋ",
                    url=group_link
                )
            )

        # Owner Button
        if owner_username:
            buttons.append(
                InlineKeyboardButton(
                    "ᴏᴡɴᴇʀ",
                    url=f"https://t.me/{owner_username}"
                )
            )

        markup = None
        if buttons:
            markup = InlineKeyboardMarkup(
                [buttons]
            )

        if message.chat.id != LOGGER_ID:
            try:
                if thumbnail:
                    await app.send_photo(
                        chat_id=LOGGER_ID,
                        photo=thumbnail,
                        caption=logger_text,
                        parse_mode=ParseMode.HTML,
                        disable_notification=True,
                        reply_markup=markup,
                    )
                else:
                    await app.send_message(
                        chat_id=LOGGER_ID,
                        text=logger_text,
                        parse_mode=ParseMode.HTML,
                        disable_notification=True,
                        reply_markup=markup,
                    )

            except Exception:
                pass
