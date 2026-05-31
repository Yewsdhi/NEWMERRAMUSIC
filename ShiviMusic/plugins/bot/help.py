import random
from typing import Union
from pyrogram import filters, types
from pyrogram.types import InlineKeyboardMarkup, Message
from ShiviMusic import app
from ShiviMusic.utils import first_page, second_page
from ShiviMusic.utils.database import get_lang
from ShiviMusic.utils.decorators.language import LanguageStart, languageCB
from ShiviMusic.utils.inline.help import help_back_markup, private_help_panel
from config import BANNED_USERS, START_IMG_URL, SUPPORT_CHAT
from strings import get_string, helpers

# Images list (cleaned spaces)
AARUMI_PIC = [
    "https://files.catbox.moe/fh7vw7.jpg",
    "https://files.catbox.moe/lckxh6.jpg",
    "https://files.catbox.moe/smteo6.jpg",
    "https://files.catbox.moe/7enu2i.jpg",
    "https://files.catbox.moe/n6hkvd.jpg",
    "https://files.catbox.moe/ej1p7t.jpg",
    "https://files.catbox.moe/fh7vw7.jpg",
    "https://files.catbox.moe/lckxh6.jpg",
    "https://files.catbox.moe/smteo6.jpg",
    "https://files.catbox.moe/7enu2i.jpg",
    "https://files.catbox.moe/n6hkvd.jpg",
    "https://files.catbox.moe/ej1p7t.jpg"
]

# -------------------- Private Help Command --------------------
@app.on_message(filters.command(["help"]) & filters.private & ~BANNED_USERS)
@app.on_callback_query(filters.regex("settings_back_helper") & ~BANNED_USERS)
async def helper_private_command(client, update: Union[types.Message, types.CallbackQuery]):
    is_callback = isinstance(update, types.CallbackQuery)
    if is_callback:
        try:
            await update.answer()
        except:
            pass
        chat_id = update.message.chat.id
        language = await get_lang(chat_id)
        _ = get_string(language)
        keyboard = first_page(_)
        await update.edit_message_text(
            _["help_1"].format(SUPPORT_CHAT), reply_markup=keyboard
        )
    else:
        try:
            await update.delete()
        except:
            pass
        language = await get_lang(update.chat.id)
        _ = get_string(language)
        keyboard = first_page(_)
        await update.reply_photo(
            random.choice(AARUMI_PIC),
            caption=_["help_1"].format(SUPPORT_CHAT),
            reply_markup=keyboard,
        )

# -------------------- Fixed Callback Help --------------------
@app.on_callback_query(filters.regex("settings_back_helper_fixed") & ~BANNED_USERS)
async def helper_private_fixed(client, update: Union[types.Message, types.CallbackQuery]):
    is_callback = isinstance(update, types.CallbackQuery)
    if is_callback:
        try:
            await update.answer()
        except:
            pass
        chat_id = update.message.chat.id
        language = await get_lang(chat_id)
        _ = get_string(language)
        keyboard = first_page(_)
        await update.edit_message_text(
            _["help_1"].format(SUPPORT_CHAT),
            reply_markup=keyboard
        )
    else:
        try:
            await update.delete()
        except:
            pass
        language = await get_lang(update.chat.id)
        _ = get_string(language)
        keyboard = first_page(_)
        await update.reply_photo(
            random.choice(AARUMI_PIC),
            caption=_["help_1"].format(SUPPORT_CHAT),
            reply_markup=keyboard
        )

# -------------------- Group Help Command --------------------
@app.on_message(filters.command(["help"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def help_com_group(client, message: Message, _):
    keyboard = private_help_panel(_)
    await message.reply_text(_["help_2"], reply_markup=InlineKeyboardMarkup(keyboard))

# -------------------- Help Callback --------------------
@app.on_callback_query(filters.regex("help_callback") & ~BANNED_USERS)
@languageCB
async def helper_cb(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    cb = callback_data.split(None, 1)[1]
    keyboard = help_back_markup(_)
    helpers_map = {
        "hb1": helpers.HELP_1,
        "hb2": helpers.HELP_2,
        "hb3": helpers.HELP_3,
        "hb4": helpers.HELP_4,
        "hb5": helpers.HELP_5,
        "hb6": helpers.HELP_6,
        "hb7": helpers.HELP_7,
        "hb8": helpers.HELP_8,
        "hb9": helpers.HELP_9,
        "hb10": helpers.HELP_10,
        "hb11": helpers.HELP_11,
        "hb12": helpers.HELP_12,
        "hb13": helpers.HELP_13,
        "hb14": helpers.HELP_14,
        "hb15": helpers.HELP_15,
        "hb16": helpers.HELP_16,
    }
    if cb in helpers_map:
        await CallbackQuery.edit_message_text(helpers_map[cb], reply_markup=keyboard)

# -------------------- Shivi Menu --------------------
Shivi_Text = (
    "ᴄʜᴏᴏsᴇ ᴛʜᴇ ᴄᴧᴛᴇɢᴏʀʏ ғᴏʀ ᴡʜɪᴄʜ ʏᴏᴜ ᴡᴧɴɴᴧ ɢᴇᴛ ʜᴇʟᴩ.\n"
    "ᴧsᴋ ʏᴏᴜʀ ᴅᴏᴜʙᴛs ᴧᴛ <a href={0}>sᴜᴘᴘᴏʀᴛ ᴄʜᴧᴛ</a>\n\n"
    "ᴧʟʟ ᴄᴏᴍᴍᴀɴᴅs ᴄᴧɴ ʙᴇ ᴜsᴇᴅ ᴡɪᴛʜ: <code>/</code>"
)

@app.on_callback_query(filters.regex("shivXaarumi") & ~BANNED_USERS)
@languageCB
async def first_pagexx(client, CallbackQuery, _):
    menu_next = second_page(_)
    try:
        await CallbackQuery.message.edit_text(
            Shiv_Text.format(SUPPORT_CHAT),
            reply_markup=menu_next
        )
    except:
        return

@app.on_callback_query(filters.regex("Aarumi") & ~BANNED_USERS)
@languageCB
async def first_pagee(client, CallbackQuery, _):
    menu_next = second_page(_)
    try:
        await CallbackQuery.message.edit_text(
            Shiv_Text.format(SUPPORT_CHAT),
            reply_markup=menu_next
        )
    except:
        return

# -------------------- End --------------------
# Do not try to change whole code, just add or remove what you want.
# Credited To Aarumi
