import asyncio
from pyrogram import filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from ShiviMusic import app

DELETE_TIME = 10  # seconds


def add_bot_button(username: str):
    return InlineKeyboardMarkup(
        [[
            InlineKeyboardButton(
                text="✙ Add Me To Your Group ✙",
                url=f"https://t.me/{username}?startgroup=true"
            )
        ]]
    )


# 🔹 Video Chat Started
@app.on_message(filters.video_chat_started)
async def vc_started(client, message: Message):
    chat_name = message.chat.title or "this group"

    text = f"❖ **Video Chat Started in {chat_name}**\n\n★ Join fast 🙊"

    bot_username = (await client.get_me()).username

    msg = await message.reply(
        text,
        reply_markup=add_bot_button(bot_username)
    )

    await asyncio.sleep(DELETE_TIME)
    await msg.delete()


# 🔹 Video Chat Ended
@app.on_message(filters.video_chat_ended)
async def vc_ended(client, message: Message):
    chat_name = message.chat.title or "this group"

    text = f"❖ **Video Chat Ended in {chat_name}**\n\n★ Bye bye 💔"

    bot_username = (await client.get_me()).username

    msg = await message.reply(
        text,
        reply_markup=add_bot_button(bot_username)
    )

    await asyncio.sleep(DELETE_TIME)
    await msg.delete()


# 🔹 Members Invited
@app.on_message(filters.video_chat_members_invited)
async def vc_invited(client, message: Message):

    if not message.from_user:
        return

    inviter = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"

    users = message.video_chat_members_invited.users
    if not users:
        return

    invited_list = [
        f"[{user.first_name}](tg://user?id={user.id})"
        for user in users if user.first_name
    ]

    names = ", ".join(invited_list)

    text = f"❖ {inviter} invited {names} on VC ⚡️\n\n★ Join fast 🙊"

    bot_username = (await client.get_me()).username

    msg = await message.reply(
        text,
        reply_markup=add_bot_button(bot_username),
        disable_web_page_preview=True
    )

    await asyncio.sleep(DELETE_TIME)
    await msg.delete()
