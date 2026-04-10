# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 🚀
# 
# This source code is under MIT License 📜
# ❌ Unauthorized forking, importing, or using this code
#    without giving proper credit will result in legal action ⚠️
# 
# 📩 DM for permission : @TheSigmaCoder
# ===========================================================

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ButtonStyle


def stats_buttons(_, status):
    not_sudo = [
        InlineKeyboardButton(
            text=_["SA_B_1"],
            callback_data="TopOverall",
            style=ButtonStyle.PRIMARY,
        )
    ]
    sudo = [
        InlineKeyboardButton(
            text=_["SA_B_2"],
            callback_data="bot_stats_sudo",
            style=ButtonStyle.SUCCESS,
        ),
        InlineKeyboardButton(
            text=_["SA_B_3"],
            callback_data="TopOverall",
            style=ButtonStyle.PRIMARY,
        ),
    ]
    upl = InlineKeyboardMarkup(
        [
            sudo if status else not_sudo,
            [
                InlineKeyboardButton(
                    text=_["CLOSE_BUTTON"],
                    callback_data="close",
                    style=ButtonStyle.DANGER,
                ),
            ],
        ]
    )
    return upl


def back_stats_buttons(_):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["BACK_BUTTON"],
                    callback_data="stats_back",
                    style=ButtonStyle.PRIMARY,
                ),
                InlineKeyboardButton(
                    text=_["CLOSE_BUTTON"],
                    callback_data="close",
                    style=ButtonStyle.DANGER,
                ),
            ],
        ]
    )
    return upl

# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 😎
# 
# 🧑‍💻 Developer : t.me/TheSigmaCoder
# 🔗 Source link : GitHub.com/Im-Notcoder/Shivi-V2
# 📢 Telegram channel : t.me/Purvi_Bots
# ===========================================================
