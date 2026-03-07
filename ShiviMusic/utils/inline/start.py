from pyrogram.types import InlineKeyboardButton
from pyrogram.enums import ButtonStyle
import config
from ShiviMusic import app


def start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_1"], url=f"https://t.me/{app.username}?startgroup=true"
            ),
            InlineKeyboardButton(text=_["S_B_2"], url=config.SUPPORT_GROUP),
        ],
    ]
    return buttons


def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true",
                style=ButtonStyle.DANGER,
            )
        ],
        [InlineKeyboardButton(text=_["S_B_4"], callback_data="settings_back_helper")],
        [
            InlineKeyboardButton(
                text="𝖠𝖯𝖨 𝖢𝗈𝗇𝗌𝗈𝗅𝖾",
                callback_data="api_console"
            )
        ],
        [
            InlineKeyboardButton(text=_["S_B_5"], user_id=config.OWNER_ID, style=ButtonStyle.SUCCESS),
            InlineKeyboardButton(text=_["S_B_2"], url=config.SUPPORT_GROUP, style=ButtonStyle.SUCCESS),
        ],
        [
            InlineKeyboardButton(text=_["S_B_6"], url=config.SUPPORT_CHANNEL, style=ButtonStyle.SUCCESS),
            InlineKeyboardButton(text=_["S_B_7"], url=f"https://t.me/ll_ROYAL_ABOUT_ll", style=ButtonStyle.SUCCESS),
        ],
    ]
    return buttons
