# ======================================================
# ©️ 2025-26 All Rights Reserved by Kirti 😎
# 🧑‍💻 Developer : t.me/lll_APNA_BADNAM_BABY_lll
# ======================================================

import math
import random

from pyrogram.types import InlineKeyboardButton
from pyrogram.enums import ButtonStyle

from ShiviMusic import app
from ShiviMusic.utils.formatters import time_to_seconds


# ======================================================
# BUTTON STYLES
# ======================================================

styles = [
    ButtonStyle.PRIMARY,
    ButtonStyle.SUCCESS,
    ButtonStyle.DANGER,
]


# ======================================================
# TRACK MARKUP
# ======================================================

def track_markup(_, videoid, user_id, channel, fplay):
    return [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
                style=random.choice(styles),
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
                style=random.choice(styles),
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
                style=random.choice(styles),
            )
        ],
    ]


# ======================================================
# PROGRESS BAR
# ======================================================

def progress_bar(played, dur):
    try:
        played_sec = time_to_seconds(played)
        duration_sec = time_to_seconds(dur)

        if duration_sec <= 0:
            return "──────────"

        percent = math.floor(
            (played_sec / duration_sec) * 100
        )

        percent = max(0, min(percent, 100))

    except Exception:
        percent = 0

    bars = [
        "◉─────────",
        "─◉────────",
        "──◉───────",
        "───◉──────",
        "────◉─────",
        "─────◉────",
        "──────◉───",
        "───────◉──",
        "────────◉─",
        "─────────◉",
    ]

    index = min(percent // 10, 9)

    return bars[index]


# ======================================================
# ADMIN CONTROL BUTTONS
# Screenshot style:
#
# ▷ | II | ↻ | ‣‣I | ▢
#
# <-20s | LOOP | 20s+>
# ======================================================

def admin_buttons(chat_id):
    return [
        # ---------------- FIRST ROW ----------------
        [
            InlineKeyboardButton(
                "▷",
                callback_data=f"ADMIN Resume|{chat_id}",
                style=random.choice(styles),
            ),
            InlineKeyboardButton(
                "II",
                callback_data=f"ADMIN Pause|{chat_id}",
                style=random.choice(styles),
            ),
            InlineKeyboardButton(
                "↻",
                callback_data=f"ADMIN Replay|{chat_id}",
                style=random.choice(styles),
            ),
            InlineKeyboardButton(
                "‣‣I",
                callback_data=f"ADMIN Skip|{chat_id}",
                style=random.choice(styles),
            ),
            InlineKeyboardButton(
                "▢",
                callback_data=f"ADMIN Stop|{chat_id}",
                style=random.choice(styles),
            ),
        ],

        # ---------------- SECOND ROW ----------------
        [
            InlineKeyboardButton(
                "< - 𝟤𝟢s",
                callback_data=f"seek_backward_20|{chat_id}",
                style=random.choice(styles),
            ),
            InlineKeyboardButton(
                "▣",
                callback_data=f"ADMIN Loop|{chat_id}",
                style=random.choice(styles),
            ),
            InlineKeyboardButton(
                "𝟤𝟢s + >",
                callback_data=f"seek_forward_20|{chat_id}",
                style=random.choice(styles),
            ),
        ],
    ]


# ======================================================
# STREAM TIMER MARKUP
# ======================================================

def stream_markup_timer(_, chat_id, played, dur):
    bar = progress_bar(played, dur)

    return [
        # ---------------- PROGRESS ----------------
        [
            InlineKeyboardButton(
                f"{played} {bar} {dur}",
                callback_data=f"GetTimer|{chat_id}",
                style=random.choice(styles),
            )
        ],

        # ---------------- CONTROLS ----------------
        *admin_buttons(chat_id),

        # ---------------- ADD ME / CLOSE ----------------
        [
            InlineKeyboardButton(
                "✙ ʌᴅᴅ ϻє ✙",
                url=f"https://t.me/{app.username}?startgroup=true",
                style=random.choice(styles),
            ),
            InlineKeyboardButton(
                _["CLOSE_BUTTON"],
                callback_data="close",
                style=random.choice(styles),
            ),
        ],
    ]


# ======================================================
# STREAM MARKUP
# ======================================================

def stream_markup(_, chat_id):
    return [
        *admin_buttons(chat_id),

        [
            InlineKeyboardButton(
                "✙ ʌᴅᴅ ϻє ✙",
                url=f"https://t.me/{app.username}?startgroup=true",
                style=random.choice(styles),
            ),
            InlineKeyboardButton(
                _["CLOSE_BUTTON"],
                callback_data="close",
                style=random.choice(styles),
            ),
        ],
    ]


# ======================================================
# PLAYLIST MARKUP
# ======================================================

def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    return [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=(
                    f"ShiviPlaylists "
                    f"{videoid}|{user_id}|{ptype}|a|{channel}|{fplay}"
                ),
                style=random.choice(styles),
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=(
                    f"ShiviPlaylists "
                    f"{videoid}|{user_id}|{ptype}|v|{channel}|{fplay}"
                ),
                style=random.choice(styles),
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
                style=random.choice(styles),
            )
        ],
    ]


# ======================================================
# LIVE STREAM MARKUP
# ======================================================

def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    return [
        [
            InlineKeyboardButton(
                text=_["P_B_3"],
                callback_data=(
                    f"LiveStream "
                    f"{videoid}|{user_id}|{mode}|{channel}|{fplay}"
                ),
                style=random.choice(styles),
            )
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
                style=random.choice(styles),
            )
        ],
    ]


# ======================================================
# SLIDER MARKUP
# ======================================================

def slider_markup(
    _,
    videoid,
    user_id,
    query,
    query_type,
    channel,
    fplay,
):
    query = str(query)[:20]

    return [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=(
                    f"MusicStream "
                    f"{videoid}|{user_id}|a|{channel}|{fplay}"
                ),
                style=random.choice(styles),
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=(
                    f"MusicStream "
                    f"{videoid}|{user_id}|v|{channel}|{fplay}"
                ),
                style=random.choice(styles),
            ),
        ],
        [
            InlineKeyboardButton(
                text="◁",
                callback_data=(
                    f"slider B|{query_type}|{query}|"
                    f"{user_id}|{channel}|{fplay}"
                ),
                style=random.choice(styles),
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {query}|{user_id}",
                style=random.choice(styles),
            ),
            InlineKeyboardButton(
                text="▷",
                callback_data=(
                    f"slider F|{query_type}|{query}|"
                    f"{user_id}|{channel}|{fplay}"
                ),
                style=random.choice(styles),
            ),
        ],
    ]
