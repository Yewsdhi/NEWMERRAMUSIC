# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 🚀
# 
# This source code is under MIT License 📜
# ❌ Unauthorized forking, importing, or using this code
#    without giving proper credit will result in legal action ⚠️
# 
# 📩 DM for permission : @TheSigmaCoder
# ===========================================================

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram import Client, filters, enums 
from pyrogram.enums import ButtonStyle
import config

class BUTTONS(object):
    ABUTTON = [
    [
        InlineKeyboardButton("• sυᴘᴘσʀᴛ •", url="https://t.me/kirti_supprot_group", style=ButtonStyle.PRIMARY),
        InlineKeyboardButton("• υᴘᴅᴧᴛєs •", url="https://t.me/Kirti_update", style=ButtonStyle.SUCCESS)
    ],
    [
        InlineKeyboardButton("• ❍ᴡηєʀ •", user_id=config.OWNER_ID, style=ButtonStyle.PRIMARY),
        InlineKeyboardButton("• ʙᴧᴄᴋ •", callback_data="settingsback_helper", style=ButtonStyle.DANGER)
    ]
]

    INFO_BUTTON = [
    [
        InlineKeyboardButton("• ʀєᴘσ •", callback_data="gib_source", style=ButtonStyle.PRIMARY),
        InlineKeyboardButton("ʏᴛ-ᴀᴘɪ 🎟️", callback_data="bot_info_data", style=ButtonStyle.SUCCESS),
        InlineKeyboardButton("• ʟᴧηɢᴜᴧɢє •", callback_data="LG", style=ButtonStyle.PRIMARY),
    ],
    [
        
        InlineKeyboardButton("• ᴘʀɪᴠᴧᴄʏ •", url="https://telegra.ph/Privacy-Policy--Shivi-Bots-by-BADNAM-BABY-08-06", style=ButtonStyle.PRIMARY),
        InlineKeyboardButton("• ʙᴧᴄᴋ •", callback_data="settingsback_helper", style=ButtonStyle.DANGER),
    ]
    ]
    


    INFO_NEW = [
    [
        InlineKeyboardButton("• ʙᴧᴄᴋ •", callback_data="settings_back_helper", style=ButtonStyle.DANGER)
    ],
    ]
    
    

# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 😎
# 
# 🧑‍💻 Developer : t.me/TheSigmaCoder
# 🔗 Source link : GitHub.com/Im-Notcoder/Shivi-V2
# 📢 Telegram channel : t.me/Purvi_Bots
# ===========================================================
