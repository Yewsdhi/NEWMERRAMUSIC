# ===========================================================
# DATABASE (FULL FIXED WITH AUTOPLAY)
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
autoplaydb = mongodb.autoplay  # ✅ NEW

# ================== MEMORY CACHE ==================

active = []
activevideo = []
assistantdict = {}
autoend = {}
count = {}
channelconnect = {}
langm = {}
loop = {}
maintenance = []
nonadmin = {}
pause = {}
playmode = {}
playtype = {}
skipmode = {}
playlist = []
autoplay = {}  # ✅ NEW

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

# ================== PLAYLIST ==================

async def _get_playlists(chat_id: int) -> Dict[str, int]:
    _notes = await playlistdb.find_one({"chat_id": chat_id})
    if not _notes:
        return {}
    return _notes["notes"]


async def get_playlist_names(chat_id: int) -> List[str]:
    return list(await _get_playlists(chat_id))


async def get_playlist(chat_id: int, name: str):
    _notes = await _get_playlists(chat_id)
    return _notes.get(name, False)


async def save_playlist(chat_id: int, name: str, note: dict):
    _notes = await _get_playlists(chat_id)
    _notes[name] = note
    await playlistdb.update_one(
        {"chat_id": chat_id}, {"$set": {"notes": _notes}}, upsert=True
    )


async def delete_playlist(chat_id: int, name: str):
    notes = await _get_playlists(chat_id)
    if name in notes:
        del notes[name]
        await playlistdb.update_one(
            {"chat_id": chat_id}, {"$set": {"notes": notes}}, upsert=True
        )
        return True
    return False

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
        upsert=True,
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

# ================== SKIP MODE ==================

async def is_skipmode(chat_id: int):
    if chat_id not in skipmode:
        data = await skipdb.find_one({"chat_id": chat_id})
        skipmode[chat_id] = False if data else True
    return skipmode[chat_id]


async def skip_on(chat_id: int):
    skipmode[chat_id] = True
    await skipdb.delete_one({"chat_id": chat_id})


async def skip_off(chat_id: int):
    skipmode[chat_id] = False
    await skipdb.insert_one({"chat_id": chat_id})

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
        {"chat_id": chat_id}, {"$set": {"mode": mode}}, upsert=True
    )

# ================== LANG ==================

async def get_lang(chat_id: int):
    if chat_id not in langm:
        data = await langdb.find_one({"chat_id": chat_id})
        langm[chat_id] = data["lang"] if data else "en"
    return langm[chat_id]


async def set_lang(chat_id: int, lang: str):
    langm[chat_id] = lang
    await langdb.update_one(
        {"chat_id": chat_id}, {"$set": {"lang": lang}}, upsert=True
    )

# ================== ACTIVE CHAT ==================

async def is_active_chat(chat_id: int):
    return chat_id in active


async def add_active_chat(chat_id: int):
    if chat_id not in active:
        active.append(chat_id)


async def remove_active_chat(chat_id: int):
    if chat_id in active:
        active.remove(chat_id)

# ================== MAINTENANCE ==================

async def is_maintenance():
    data = await onoffdb.find_one({"on_off": 1})
    return not bool(data)


async def maintenance_on():
    await onoffdb.insert_one({"on_off": 1})


async def maintenance_off():
    await onoffdb.delete_one({"on_off": 1})

# ================== USERS ==================

async def is_served_user(user_id: int):
    return bool(await usersdb.find_one({"user_id": user_id}))


async def add_served_user(user_id: int):
    if not await is_served_user(user_id):
        await usersdb.insert_one({"user_id": user_id})

# ================== BANS ==================

async def is_banned_user(user_id: int):
    return bool(await blockeddb.find_one({"user_id": user_id}))


async def add_banned_user(user_id: int):
    if not await is_banned_user(user_id):
        await blockeddb.insert_one({"user_id": user_id})


async def remove_banned_user(user_id: int):
    await blockeddb.delete_one({"user_id": user_id})
