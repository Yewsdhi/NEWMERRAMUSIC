# ===========================================================
# FINAL DATABASE (NO ERROR VERSION)
# ===========================================================

import random
from typing import Dict, List, Union

from ShiviMusic import userbot
from ShiviMusic.core.mongo import mongodb

# ================== COLLECTIONS ==================

authdb = mongodb.adminauth
authuserdb = mongodb.authuser
autoenddb = mongodb.autoend
assdb = mongodb.assistants
blacklist_chatdb = mongodb.blacklistChat
blockeddb = mongodb.blockedusers
chatsdb = mongodb.chats
channeldb = mongodb.cplaymode
countdb = mongodb.upcount
gbansdb = mongodb.gban
langdb = mongodb.language
onoffdb = mongodb.onoffper
playmodedb = mongodb.playmode
playtypedb = mongodb.playtypedb
skipdb = mongodb.skipmode
sudoersdb = mongodb.sudoers
usersdb = mongodb.tgusersdb
playlistdb = mongodb.playlist
autoplaydb = mongodb.autoplay

# ================== MEMORY ==================

active = []
activevideo = []
assistantdict = {}
channelconnect = {}
langm = {}
loop = {}
maintenance = []
nonadmin = {}
pause = {}
playmode = {}
playtype = {}
skipmode = {}
autoplay = {}

# ================== AUTOPLAY ==================

async def get_autoplay(chat_id: int) -> bool:
    mode = autoplay.get(chat_id)
    if mode is None:
        data = await autoplaydb.find_one({"chat_id": chat_id})
        if not data:
            autoplay[chat_id] = False
            return False
        autoplay[chat_id] = data["mode"]
        return data["mode"]
    return mode


async def set_autoplay(chat_id: int, mode: bool):
    autoplay[chat_id] = mode
    await autoplaydb.update_one(
        {"chat_id": chat_id},
        {"$set": {"mode": mode}},
        upsert=True
    )

# ================== CHANNEL MODE ==================

async def get_cmode(chat_id: int):
    mode = channelconnect.get(chat_id)
    if mode is None:
        data = await channeldb.find_one({"chat_id": chat_id})
        if not data:
            return None
        channelconnect[chat_id] = data["mode"]
        return data["mode"]
    return mode


async def set_cmode(chat_id: int, mode: int):
    channelconnect[chat_id] = mode
    await channeldb.update_one(
        {"chat_id": chat_id},
        {"$set": {"mode": mode}},
        upsert=True
    )

# ================== PLAYLIST ==================

async def _get_playlists(chat_id: int) -> Dict:
    data = await playlistdb.find_one({"chat_id": chat_id})
    return data["notes"] if data else {}


async def get_playlist(chat_id: int, name: str):
    return (await _get_playlists(chat_id)).get(name, False)


async def save_playlist(chat_id: int, name: str, note: dict):
    notes = await _get_playlists(chat_id)
    notes[name] = note
    await playlistdb.update_one(
        {"chat_id": chat_id},
        {"$set": {"notes": notes}},
        upsert=True
    )

# ================== ASSISTANT ==================

async def get_client(num: int):
    return {
        1: userbot.one,
        2: userbot.two,
        3: userbot.three,
        4: userbot.four,
        5: userbot.five,
    }.get(int(num))


async def set_assistant(chat_id):
    from ShiviMusic.core.userbot import assistants
    ran = random.choice(assistants)
    assistantdict[chat_id] = ran
    await assdb.update_one(
        {"chat_id": chat_id},
        {"$set": {"assistant": ran}},
        upsert=True
    )
    return await get_client(ran)


async def get_assistant(chat_id: int):
    from ShiviMusic.core.userbot import assistants
    assistant = assistantdict.get(chat_id)

    if not assistant:
        data = await assdb.find_one({"chat_id": chat_id})
        if not data:
            return await set_assistant(chat_id)
        assistant = data["assistant"]

    if assistant not in assistants:
        return await set_assistant(chat_id)

    assistantdict[chat_id] = assistant
    return await get_client(assistant)

# ================== LOOP ==================

async def get_loop(chat_id: int):
    return loop.get(chat_id, 0)


async def set_loop(chat_id: int, mode: int):
    loop[chat_id] = mode

# ================== PLAY MODE ==================

async def get_playmode(chat_id: int):
    if chat_id not in playmode:
        data = await playmodedb.find_one({"chat_id": chat_id})
        playmode[chat_id] = data["mode"] if data else "Direct"
    return playmode[chat_id]


async def set_playmode(chat_id: int, mode: str):
    playmode[chat_id] = mode
    await playmodedb.update_one(
        {"chat_id": chat_id},
        {"$set": {"mode": mode}},
        upsert=True
    )

# ================== LANG ==================

async def get_lang(chat_id: int):
    if chat_id not in langm:
        data = await langdb.find_one({"chat_id": chat_id})
        langm[chat_id] = data["lang"] if data else "en"
    return langm[chat_id]

# ================== ACTIVE ==================

async def add_active_chat(chat_id: int):
    if chat_id not in active:
        active.append(chat_id)


async def remove_active_chat(chat_id: int):
    if chat_id in active:
        active.remove(chat_id)

# ================== USERS ==================

async def add_served_user(user_id: int):
    if not await usersdb.find_one({"user_id": user_id}):
        await usersdb.insert_one({"user_id": user_id})

# ================== BAN ==================

async def is_banned_user(user_id: int):
    return bool(await blockeddb.find_one({"user_id": user_id}))
