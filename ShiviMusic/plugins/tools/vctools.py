from pyrogram import filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from ShiviMusic import ShiviMusic as app


@app.on_message(filters.video_chat_started)
async def vc_started(_, message: Message):
    chat_name = message.chat.title or "this group"

    text = (
        f"**❖ ᴠɪᴅᴇᴏ ᴄʜᴀᴛ sᴛᴀʀᴛᴇᴅ ɪɴ {chat_name}**\n\n"
        f"**⏤͟͟͞͞★ ᴊᴏɪɴ ғᴀsᴛ ᴀɴᴅ sᴛᴀʀᴛ ɢᴏssɪᴘ 🙊**"
    )

    add_link = f"https://t.me/{app.username}?startgroup=true"

    await message.reply(
        text,
        reply_markup=InlineKeyboardMarkup(
            [[
                InlineKeyboardButton(
                    text="✙ ʌᴅᴅ ϻє ɪη ʏσυʀ ɢʀσυᴘ ✙",
                    url=add_link
                )
            ]]
        )
    )


@app.on_message(filters.video_chat_ended)
async def vc_ended(_, message: Message):
    chat_name = message.chat.title or "this group"

    text = (
        f"**❖ ᴠɪᴅᴇᴏ ᴄʜᴀᴛ ᴇɴᴅᴇᴅ ɪɴ {chat_name}**\n\n"
        f"**⏤͟͟͞͞★ ʙʏᴇ ʙʏᴇ ғʀɪᴇɴᴅs sᴇᴇ ʏᴏᴜ sᴏᴏɴ 💔**"
    )

    add_link = f"https://t.me/{app.username}?startgroup=true"

    await message.reply(
        text,
        reply_markup=InlineKeyboardMarkup(
            [[
                InlineKeyboardButton(
                    text="✙ ʌᴅᴅ ϻє ɪη ʏσυʀ ɢʀσυᴘ ✙",
                    url=add_link
                )
            ]]
        )
    )

@app.on_message(filters.video_chat_members_invited)
async def vc_invited(client, message: Message):

    if not message.from_user:
        return

    inviter = f"[{message.from_user.first_name.lower()}](tg://user?id={message.from_user.id})"

    users = message.video_chat_members_invited.users
    if not users:
        return

    invited_list = []
    for user in users:
        if user.first_name:
            invited_list.append(
                f"[{user.first_name.lower()}](tg://user?id={user.id})"
            )

    names = ", ".join(invited_list)

    text = (
        f"**❖ {inviter} ɪɴᴠɪᴛᴇᴅ {names} ᴏɴ ᴠᴄ.⚡️~!**\n\n"
        f"**⏤͟͟͞͞★ ᴊᴏɪɴ ғᴀsᴛ ʙᴀʙʏ 🙊**"
    )

    add_link = f"https://t.me/{client.username}?startgroup=true"

    await message.reply(
        text,
        reply_markup=InlineKeyboardMarkup(
            [[
                InlineKeyboardButton(
                    text="✙ ʌᴅᴅ ϻє ɪη ʏσυʀ ɢʀσυᴘ ✙",
                    url=add_link
                )
            ]]
        ),
        disable_web_page_preview=True
    )
