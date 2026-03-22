# ======================================================
# ©️ 2025-26 All Rights Reserved by Kirti 😎
# 🧑‍💻 Developer : t.me/lll_APNA_BADNAM_BABY_lll
# =======================================================

import math
from config import SUPPORT_CHAT, OWNER_USERNAME
from pyrogram.types import InlineKeyboardButton
from ShiviMusic import app
import config
from ShiviMusic.utils.formatters import time_to_seconds

# --- DRUGS FILTER SYSTEM ---
BANNED_KEYWORDS = ["drugs", "ganja", "charas", "nashe", "cocaine", "weed", "opium", "fukni", "chitta"]

def is_drugs_song(title):
    if not title:
        return False
    title_lower = title.lower()
    return any(word in title_lower for word in BANNED_KEYWORDS)
# ---------------------------

def track_markup(_, videoid, user_id, channel, fplay, title=None):
    # Agar title me drugs hai toh block button dikhao
    if is_drugs_song(title):
        return [
            [InlineKeyboardButton(text="🚫 CONTENT BLOCKED (DRUGS)", callback_data="close")],
            [InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data=f"forceclose {videoid}|{user_id}")]
        ]

    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
            )
        ],
    ]
    return buttons


def stream_markup_timer(_, chat_id, played, dur):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    percentage = (played_sec / duration_sec) * 100
    umm = math.floor(percentage)
    
    # Progress Bar Logic
    bar_icons = ["◉—————————", "—◉————————", "——◉———————", "———◉——————", 
                 "————◉—————", "—————◉————", "——————◉———", "———————◉——", 
                 "————————◉—", "—————————◉"]
    
    idx = min(int(umm / 10), 9)
    bar = bar_icons[idx]
    
    buttons = [
        [InlineKeyboardButton(text=f"{played} {bar} {dur}", callback_data="GetTimer")],
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="↻", callback_data=f"ADMIN Replay|{chat_id}"),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [
             InlineKeyboardButton(text="< - 20s", callback_data=f"ADMIN SeekB|{chat_id}"),
             InlineKeyboardButton(text="ᴘʀᴏᴍᴏ", url=f"https://t.me/III_Yadav_op_III"),
             InlineKeyboardButton(text="20s + >", callback_data=f"ADMIN SeekF|{chat_id}")
        ],
        [InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close")]
    ]
    return buttons


def stream_markup(_, chat_id):
    buttons = [
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="↻", callback_data=f"ADMIN Replay|{chat_id}"),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
         ],
        [
             InlineKeyboardButton(text="< - 20s", callback_data=f"ADMIN SeekB|{chat_id}"),
             InlineKeyboardButton(text="ᴘʀᴏᴍᴏ", url=f"https://t.me/III_Yadav_op_III"),
             InlineKeyboardButton(text="20s + >", callback_data=f"ADMIN SeekF|{chat_id}")
         ],
        [InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close")]
    ]
    return buttons


def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"ShiviPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"ShiviPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}",
            ),
        ],
        [InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data=f"forceclose {videoid}|{user_id}")]
    ]
    return buttons


def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_3"],
                callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}",
            ),
        ],
        [InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data=f"forceclose {videoid}|{user_id}")]
    ]
    return buttons


def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    query = f"{query[:20]}"
    buttons = [
        [
            InlineKeyboardButton(text=_["P_B_1"], callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}"),
            InlineKeyboardButton(text=_["P_B_2"], callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}"),
        ],
        [
            InlineKeyboardButton(text="◁", callback_data=f"slider B|{query_type}|{query}|{user_id}|{channel}|{fplay}"),
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data=f"forceclose {query}|{user_id}"),
            InlineKeyboardButton(text="▷", callback_data=f"slider F|{query_type}|{query}|{user_id}|{channel}|{fplay}"),
        ],
    ]
    return buttons
