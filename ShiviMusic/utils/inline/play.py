# ======================================================
# ©️ 2025-26 All Rights Reserved by Kirti 😎
# 🧑‍💻 Developer : t.me/lll_APNA_BADNAM_BABY_lll
# ======================================================

from pyrogram.types import InlineKeyboardButton
from pyrogram.enums import ButtonStyle


# ======================================================
# ADMIN CONTROL PANEL
# ======================================================

def admin_buttons(chat_id, autoplay=True):

    if autoplay:
        autoplay_text = "ᴀᴜᴛᴏ : ᴏɴ"
        autoplay_style = ButtonStyle.SUCCESS
    else:
        autoplay_text = "ᴀᴜᴛᴏ : ᴏғғ"
        autoplay_style = ButtonStyle.DANGER

    return [
        [
            InlineKeyboardButton(
                "ᴘᴀᴜsᴇ",
                callback_data=f"ADMIN Pause|{chat_id}",
                style=ButtonStyle.PRIMARY,
            ),

            InlineKeyboardButton(
                "ʀᴇsᴜᴍᴇ",
                callback_data=f"ADMIN Resume|{chat_id}",
                style=ButtonStyle.SUCCESS,
            ),

            InlineKeyboardButton(
                "sᴋɪᴘ",
                callback_data=f"ADMIN Skip|{chat_id}",
                style=ButtonStyle.PRIMARY,
            ),
        ],
        [
            InlineKeyboardButton(
                autoplay_text,
                callback_data=f"ADMIN AutoPlay|{chat_id}",
                style=autoplay_style,
            ),

            InlineKeyboardButton(
                "ᴄʟᴏsᴇ",
                callback_data="close",
                style=ButtonStyle.DANGER,
            ),
        ],
    ]


# ======================================================
# STREAM MARKUP
# ======================================================

def stream_markup(_, chat_id):

    return admin_buttons(
        chat_id,
        autoplay=True,
    )


# ======================================================
# STREAM MARKUP TIMER
# ======================================================
# Timer/progress bar removed.
# Kept for compatibility with old imports.
# ======================================================

def stream_markup_timer(
    _,
    chat_id,
    played=None,
    dur=None,
):

    return admin_buttons(
        chat_id,
        autoplay=True,
    )


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
                style=ButtonStyle.PRIMARY,
            ),

            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=(
                    f"MusicStream "
                    f"{videoid}|{user_id}|v|"
                    f"{channel}|{fplay}"
                ),
                style=ButtonStyle.SUCCESS,
            ),
        ],

        [
            InlineKeyboardButton(
                text="ᴄʟᴏsᴇ",
                callback_data=(
                    f"forceclose "
                    f"{videoid}|{user_id}"
                ),
                style=ButtonStyle.DANGER,
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
                style=ButtonStyle.PRIMARY,
            ),

            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=(
                    f"ShiviPlaylists "
                    f"{videoid}|{user_id}|{ptype}|v|"
                    f"{channel}|{fplay}"
                ),
                style=ButtonStyle.SUCCESS,
            ),
        ],

        [
            InlineKeyboardButton(
                text="ᴄʟᴏsᴇ",
                callback_data=(
                    f"forceclose "
                    f"{videoid}|{user_id}"
                ),
                style=ButtonStyle.DANGER,
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
                style=ButtonStyle.PRIMARY,
            )
        ],

        [
            InlineKeyboardButton(
                text="ᴄʟᴏsᴇ",
                callback_data=(
                    f"forceclose "
                    f"{videoid}|{user_id}"
                ),
                style=ButtonStyle.DANGER,
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
                style=ButtonStyle.PRIMARY,
            ),

            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=(
                    f"MusicStream "
                    f"{videoid}|{user_id}|v|"
                    f"{channel}|{fplay}"
                ),
                style=ButtonStyle.SUCCESS,
            ),
        ],

        [
            InlineKeyboardButton(
                "ʙᴀᴄᴋ",
                callback_data=(
                    f"slider B|{query_type}|{query}|"
                    f"{user_id}|{channel}|{fplay}"
                ),
                style=ButtonStyle.PRIMARY,
            ),

            InlineKeyboardButton(
                "ᴄʟᴏsᴇ",
                callback_data=(
                    f"forceclose "
                    f"{query}|{user_id}"
                ),
                style=ButtonStyle.DANGER,
            ),

            InlineKeyboardButton(
                "ɴᴇxᴛ",
                callback_data=(
                    f"slider F|{query_type}|{query}|"
                    f"{user_id}|{channel}|{fplay}"
                ),
                style=ButtonStyle.PRIMARY,
            ),
        ],
    ]
