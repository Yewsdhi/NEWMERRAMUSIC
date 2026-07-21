import math
from pyrogram.types import InlineKeyboardButton
from ShiviMusic.utils.formatters import time_to_seconds
from ShiviMusic import app

def track_markup(_, videoid, user_id, channel, fplay):
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

    remaining_sec = duration_sec - played_sec
    if remaining_sec < 0:
        remaining_sec = 0

    rem_min = remaining_sec // 60
    rem_sec = remaining_sec % 60
    remaining = f"{rem_min:02d}:{rem_sec:02d}"

    percentage = (played_sec / duration_sec) * 100 if duration_sec else 0
    umm = math.floor(percentage)

    if 0 < umm <= 10:
        bar = "|⚪─────────|"
    elif 10 < umm < 20:
        bar = "|━⚪────────|"
    elif 20 <= umm < 30:
        bar = "|━━⚪───────|"
    elif 30 <= umm < 40:
        bar = "|━━━⚪──────|"
    elif 40 <= umm < 50:
        bar = "|━━━━⚪─────|"
    elif 50 <= umm < 60:
        bar = "|━━━━━⚪────|"
    elif 60 <= umm < 70:
        bar = "|━━━━━━⚪───|"
    elif 70 <= umm < 80:
        bar = "|━━━━━━━⚪──|"
    elif 80 <= umm < 95:
        bar = "|━━━━━━━━⚪─|"
    else:
        bar = "|━━━━━━━━━⚪|"

    buttons = [
        [
            InlineKeyboardButton(
                text=f"{played} {bar} {remaining}",
                callback_data="GetTimer",
                icon_custom_emoji_id=5204046146955153467,
            )
        ],
        [
            InlineKeyboardButton(text="❚❚", callback_data=f"ADMIN Pause|{chat_id}", icon_custom_emoji_id=5409222721869459068, 
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}", icon_custom_emoji_id=5409042015415448331, 
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}", icon_custom_emoji_id=5408832111773757273, 
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}", icon_custom_emoji_id=5408832111773757273, 
        ],
        [
            InlineKeyboardButton(text="⪻ -𝟸𝟶s", callback_data="seek_backward_20", icon_custom_emoji_id=5408832111773757273, 
            InlineKeyboardButton(text="↻", callback_data=f"ADMIN Replay|{chat_id}", icon_custom_emoji_id=5408832111773757273, 
            InlineKeyboardButton(text="+𝟸𝟶s ⪼", callback_data="seek_forward_20", icon_custom_emoji_id=5408832111773757273, 
        ],
        [
            InlineKeyboardButton(text="✙ 𝐀ᴅᴅ 𝐌є", url=f"https://t.me/{app.username}?startgroup=true",  icon_custom_emoji_id=5408832111773757273, 
            InlineKeyboardButton(text="𝐂ʟᴏsᴇ[✗]", callback_data="close",  icon_custom_emoji_id=5408832111773757273, 
        ],
    ]
    return buttons


def stream_markup(_, chat_id):
    buttons = [
        [
            InlineKeyboardButton(text="❚❚", callback_data=f"ADMIN Pause|{chat_id}",  icon_custom_emoji_id=5408832111773757273, 
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}", icon_custom_emoji_id=5408832111773757273, 
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}",  icon_custom_emoji_id=5408832111773757273, 
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}",  icon_custom_emoji_id=5408832111773757273, 
        ],
        [
            InlineKeyboardButton(text="⪻ -𝟸𝟶s", callback_data="seek_backward_20"),
            InlineKeyboardButton(text="↻", callback_data=f"ADMIN Replay|{chat_id}"),
            InlineKeyboardButton(text="+𝟸𝟶s ⪼", callback_data="seek_forward_20"),
        ],
        [
            InlineKeyboardButton(text="✙ 𝐀ᴅᴅ 𝐌є", url=f"https://t.me/{app.username}?startgroup=true"),
            InlineKeyboardButton(text="𝐂ʟᴏsᴇ[✗]", callback_data="close"),
        ],
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
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
            ),
        ],
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
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
            ),
        ],
    ]
    return buttons


def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    query = f"{query[:20]}"
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
                text="◁",
                callback_data=f"slider B|{query_type}|{query}|{user_id}|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {query}|{user_id}",
            ),
            InlineKeyboardButton(
                text="▷",
                callback_data=f"slider F|{query_type}|{query}|{user_id}|{channel}|{fplay}",
            ),
        ],
    ]
    return buttons
