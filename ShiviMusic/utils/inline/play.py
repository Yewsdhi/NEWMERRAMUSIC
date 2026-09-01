# ======================================================
# ©️ 2025-26 All Rights Reserved by Kirti 😎
# 🧑‍💻 Developer : t.me/lll_APNA_BADNAM_BABY_lll
# ======================================================

import math

from pyrogram.types import InlineKeyboardButton

from ShiviMusic import app
from ShiviMusic.utils.formatters import time_to_seconds


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
        "◉—————————",
        "—◉————————",
        "——◉———————",
        "———◉——————",
        "————◉—————",
        "—————◉————",
        "——————◉———",
        "———————◉——",
        "————————◉—",
        "—————————◉",
    ]

    index = min(percent // 10, 9)

    return bars[index]


# ======================================================
# ADMIN BUTTONS
# ======================================================

def admin_buttons(chat_id, autoplay=True):

    if autoplay:
        autoplay_text = "🔄 ᴀᴜᴛᴏᴘʟᴀʏ : ON ✅"
    else:
        autoplay_text = "🔄 ᴀᴜᴛᴏᴘʟᴀʏ : OFF ❌"

    return [

        # ==============================================
        # ROW 1
        # ==============================================

        [
            InlineKeyboardButton(
                "⏸ ᴘᴀᴜsᴇ",
                callback_data=f"ADMIN Pause|{chat_id}",
            ),

            InlineKeyboardButton(
                "▶️ ʀᴇsᴜᴍᴇ",
                callback_data=f"ADMIN Resume|{chat_id}",
            ),

            InlineKeyboardButton(
                "⏭ sᴋɪᴘ",
                callback_data=f"ADMIN Skip|{chat_id}",
            ),
        ],

        # ==============================================
        # ROW 2
        # ==============================================

        [
            InlineKeyboardButton(
                autoplay_text,
                callback_data=f"ADMIN AutoPlay|{chat_id}",
            ),

            InlineKeyboardButton(
                "✕ ᴄʟᴏsᴇ",
                callback_data="close",
            ),
        ],
    ]


# ======================================================
# STREAM MARKUP
# ======================================================

def stream_markup(_, chat_id):

    # Default ON display.
    # Actual ON/OFF state should be supplied from DB
    # if your project already has an autoplay database.
    return admin_buttons(
        chat_id,
        autoplay=True,
    )


# ======================================================
# STREAM MARKUP WITH TIMER
# ======================================================

def stream_markup_timer(
    _,
    chat_id,
    played,
    dur,
):

    bar = progress_bar(
        played,
        dur,
    )

    return [
        [
            InlineKeyboardButton(
                f"{played} {bar} {dur}",
                callback_data="GetTimer",
            )
        ],

        *admin_buttons(
            chat_id,
            autoplay=True,
        ),
    ]


# ======================================================
# TRACK MARKUP
# ======================================================

def track_markup(
    _,
    videoid,
    user_id,
    channel,
    fplay,
):

    return [

        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=(
                    f"MusicStream "
                    f"{videoid}|{user_id}|a|"
                    f"{channel}|{fplay}"
                ),
            ),

            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=(
                    f"MusicStream "
                    f"{videoid}|{user_id}|v|"
                    f"{channel}|{fplay}"
                ),
            ),
        ],

        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=(
                    f"forceclose "
                    f"{videoid}|{user_id}"
                ),
            )
        ],
    ]


# ======================================================
# PLAYLIST MARKUP
# ======================================================

def playlist_markup(
    _,
    videoid,
    user_id,
    ptype,
    channel,
    fplay,
):

    return [

        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=(
                    f"ShiviPlaylists "
                    f"{videoid}|{user_id}|{ptype}|a|"
                    f"{channel}|{fplay}"
                ),
            ),

            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=(
                    f"ShiviPlaylists "
                    f"{videoid}|{user_id}|{ptype}|v|"
                    f"{channel}|{fplay}"
                ),
            ),
        ],

        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=(
                    f"forceclose "
                    f"{videoid}|{user_id}"
                ),
            )
        ],
    ]


# ======================================================
# LIVESTREAM MARKUP
# ======================================================

def livestream_markup(
    _,
    videoid,
    user_id,
    mode,
    channel,
    fplay,
):

    return [

        [
            InlineKeyboardButton(
                text=_["P_B_3"],
                callback_data=(
                    f"LiveStream "
                    f"{videoid}|{user_id}|{mode}|"
                    f"{channel}|{fplay}"
                ),
            )
        ],

        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=(
                    f"forceclose "
                    f"{videoid}|{user_id}"
                ),
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
                    f"{videoid}|{user_id}|a|"
                    f"{channel}|{fplay}"
                ),
            ),

            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=(
                    f"MusicStream "
                    f"{videoid}|{user_id}|v|"
                    f"{channel}|{fplay}"
                ),
            ),
        ],

        [
            InlineKeyboardButton(
                "◀️",
                callback_data=(
                    f"slider B|{query_type}|{query}|"
                    f"{user_id}|{channel}|{fplay}"
                ),
            ),

            InlineKeyboardButton(
                _["CLOSE_BUTTON"],
                callback_data=(
                    f"forceclose "
                    f"{query}|{user_id}"
                ),
            ),

            InlineKeyboardButton(
                "▶️",
                callback_data=(
                    f"slider F|{query_type}|{query}|"
                    f"{user_id}|{channel}|{fplay}"
                ),
            ),
        ],
    ]
