# ======================================================
# ©️ 2025-26 All Rights Reserved by Kirti 😎
#
# 🧑‍💻 Developer : t.me/lll_APNA_BADNAM_BABY_lll
# 🔗 Source link : https://github.com/Badnam019
# 📢 Telegram channel : t.me/lll_APNA_BADNAM_BABY_lll
# =======================================================

from typing import Union

from ShiviMusic import app
from ShiviMusic.utils.formatters import time_to_seconds
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ButtonStyle


def queue_markup(
    _,
    DURATION,
    CPLAY,
    videoid,
    played: Union[bool, int] = None,
    dur: Union[bool, int] = None,
):
    # Buttons when duration is unknown
    not_dur = [
        [
            InlineKeyboardButton(
                text=_["QU_B_1"],
                callback_data=f"GetQueued {CPLAY}|{videoid}",
                style=ButtonStyle.PRIMARY,
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data="close",
                style=ButtonStyle.DANGER,
            ),
        ]
    ]

    # Buttons when duration is available
    dur = [
        [
            InlineKeyboardButton(
                text=_["QU_B_2"].format(played, dur),
                callback_data="GetTimer",
                style=ButtonStyle.SUCCESS,
            )
        ],
        [
            InlineKeyboardButton(
                text=_["QU_B_1"],
                callback_data=f"GetQueued {CPLAY}|{videoid}",
                style=ButtonStyle.PRIMARY,
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data="close",
                style=ButtonStyle.DANGER,
            ),
        ],
    ]

    upl = InlineKeyboardMarkup(
        not_dur if DURATION == "Unknown" else dur
    )

    return upl


def queue_back_markup(_, CPLAY):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["BACK_BUTTON"],
                    callback_data=f"queue_back_timer {CPLAY}",
                    style=ButtonStyle.PRIMARY,
                ),
                InlineKeyboardButton(
                    text=_["CLOSE_BUTTON"],
                    callback_data="close",
                    style=ButtonStyle.DANGER,
                ),
            ]
        ]
    )

    return upl


def aq_markup(_, chat_id):
    """
    Autoplay / Music control buttons.
    Join Now and Group Chat buttons removed.
    """

    buttons = [
        # Resume / Pause
        [
            InlineKeyboardButton(
                text="▶️ RESUME",
                callback_data=f"resume_stream {chat_id}",
                style=ButtonStyle.SUCCESS,
            ),
            InlineKeyboardButton(
                text="⏸️ PAUSE",
                callback_data=f"pause_stream {chat_id}",
                style=ButtonStyle.PRIMARY,
            ),
        ],

        # Skip / Stop
        [
            InlineKeyboardButton(
                text="⏭️ SKIP",
                callback_data=f"skip_stream {chat_id}",
                style=ButtonStyle.PRIMARY,
            ),
            InlineKeyboardButton(
                text="⏹️ STOP",
                callback_data=f"stop_stream {chat_id}",
                style=ButtonStyle.DANGER,
            ),
        ],

        # Close
        [
            InlineKeyboardButton(
                text="❌ CLOSE",
                callback_data="close",
                style=ButtonStyle.DANGER,
            )
        ],
    ]

    return InlineKeyboardMarkup(buttons)


# ======================================================
# ©️ 2025-26 All Rights Reserved by Kirti 😎
#
# 🧑‍💻 Developer : t.me/lll_APNA_BADNAM_BABY_lll
# 🔗 Source link : https://github.com/Badnam019
# 📢 Telegram channel : t.me/lll_APNA_BADNAM_BABY_lll
# ======================================================
