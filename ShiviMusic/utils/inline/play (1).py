import math
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from MecoMusic import app
import config
from pyrogram.enums import ButtonStyle
from MecoMusic.utils.formatters import time_to_seconds


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
    percentage = (played_sec / duration_sec) * 100
    
    umm = math.floor(percentage)
    if 0 < umm <= 10:
        bar = "𖣐—————————"
    elif 10 < umm < 20:
        bar = "—𖣐————————"
    elif 20 <= umm < 30:
        bar = "—𖣐———————"
    elif 30 <= umm < 40:
        bar = "——𖣐——————"
    elif 40 <= umm < 50:
        bar = "———𖣐—————"
    elif 50 <= umm < 60:
        bar = "————𖣐————"
    elif 60 <= umm < 70:
        bar = "—————𖣐———"
    elif 70 <= umm < 80:
        bar = "——————𖣐——"
    elif 80 <= umm < 95:
        bar = "———————𖣐—"
    else:
        bar = "————————𖣐"
    buttons = [
                [
            InlineKeyboardButton(
                text=f"{played} {bar} {dur}",
                callback_data="GetTimer",
                style=ButtonStyle.PRIMARY,
            )
        ],
        [
           # InlineKeyboardButton(text="", callback_data=f"ADMIN Resume|{chat_id}", icon_custom_emoji_id=5409222721869459068),
           # InlineKeyboardButton(text="", callback_data=f"ADMIN Pause|{chat_id}", icon_custom_emoji_id=5409042015415448331),
           # InlineKeyboardButton(text="", callback_data=f"ADMIN Stop|{chat_id}", icon_custom_emoji_id=5408832111773757273),
        ],
        [
            InlineKeyboardButton(
                text="α∂∂ мє",
                url="https://t.me/ChaahatMusicBot?startgroup=true",
                icon_custom_emoji_id=5395476176527447827,
                style=ButtonStyle.SUCCESS
                
            ),
            InlineKeyboardButton(
                text="ѕυρροʀᴛ",
                url="https://t.me/Mecobots",
                icon_custom_emoji_id=5438600169325095982,
                style=ButtonStyle.DANGER
            
            )
        ],
            

       # [InlineKeyboardButton(text=" ᴄʟᴏsᴇ ▣", callback_data="close", style=ButtonStyle.DANGER, icon_custom_emoji_id=5408832111773757273)],
    ]
    return buttons


def stream_markup(_, chat_id):
    buttons = [
        [
           # InlineKeyboardButton(text="", callback_data=f"ADMIN Resume|{chat_id}", icon_custom_emoji_id=5409222721869459068),
           # InlineKeyboardButton(text="", callback_data=f"ADMIN Pause|{chat_id}", icon_custom_emoji_id=5409042015415448331),
           # InlineKeyboardButton(text="", callback_data=f"ADMIN Stop|{chat_id}", icon_custom_emoji_id=5408832111773757273),
        ],
        [
            InlineKeyboardButton(
                text="α∂∂ мє",
                url="https://t.me/ChaahatMusicBot?startgroup=true",
                icon_custom_emoji_id=5395476176527447827,
                style=ButtonStyle.DANGER
                
            ),
            InlineKeyboardButton(
                text="ѕυρροʀᴛ",
                url="https://t.me/Mecobots",
                icon_custom_emoji_id=5438600169325095982,
                style=ButtonStyle.DANGER
            
            )
        ],
            

       # [InlineKeyboardButton(text=" ᴄʟᴏsᴇ ▣", callback_data="close", style=ButtonStyle.DANGER, icon_custom_emoji_id=5408832111773757273)],
    ]
    return buttons

def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MecoPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MecoPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}",
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
