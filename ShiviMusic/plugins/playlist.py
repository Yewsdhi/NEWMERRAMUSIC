# ======================================================
# ShiviMusic - Playlist System
# Python / Pyrogram compatible playlist handlers
# ======================================================

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from ShiviMusic import app
from ShiviMusic.utils.database import db


def _playlist_store():
    """Return a small in-memory fallback store if database playlist APIs
    are not available. Existing database implementations are preferred."""
    if not hasattr(_playlist_store, "_data"):
        _playlist_store._data = {}
    return _playlist_store._data


async def _get_user_playlists(user_id):
    for name in ("get_user_playlists", "get_user_playlists_db", "get_playlists"):
        fn = getattr(db, name, None)
        if fn:
            try:
                return await fn(user_id)
            except Exception:
                pass
    return list(_playlist_store().get(user_id, {}).values())


async def _get_playlist(user_id, playlist_id):
    for name in ("get_playlist", "get_playlist_db"):
        fn = getattr(db, name, None)
        if fn:
            try:
                return await fn(playlist_id)
            except Exception:
                pass
    return _playlist_store().get(user_id, {}).get(playlist_id)


@app.on_message(filters.command("createplaylist"))
async def create_playlist(_, message):
    name = message.text.split(None, 1)[1].strip() if len(message.command) > 1 else ""
    if not name:
        return await message.reply_text(
            "<b>Usage:</b> <code>/createplaylist Playlist Name</code>"
        )

    if len(name) > 40:
        name = name[:40]

    user_id = message.from_user.id
    playlists = await _get_user_playlists(user_id)

    if len(playlists) >= 10:
        return await message.reply_text(
            "<b>❖ Playlist Limit</b>\n\nYou can have maximum <b>10 playlists</b>."
        )

    playlist_id = str(len(playlists) + 1)

    data = {
        "id": playlist_id,
        "name": name,
        "user_id": user_id,
        "songs": [],
    }

    # Prefer an existing database API.
    for method in ("create_playlist", "create_playlist_db"):
        fn = getattr(db, method, None)
        if fn:
            try:
                result = await fn(name, user_id)
                playlist_id = str(result or playlist_id)
                break
            except Exception:
                continue
    else:
        _playlist_store().setdefault(user_id, {})[playlist_id] = data

    return await message.reply_text(
        f"<b>❖ PLAYLIST CREATED</b>\n\n"
        f"╭ <b>Name:</b> {name}\n"
        f"╰ <b>ID:</b> <code>{playlist_id}</code>"
    )


@app.on_message(filters.command("myplaylists"))
async def my_playlists(_, message):
    playlists = await _get_user_playlists(message.from_user.id)

    if not playlists:
        return await message.reply_text(
            "<b>❖ MY PLAYLISTS</b>\n\nNo playlists found."
        )

    text = "<b>❖ MY PLAYLISTS</b>\n\n"
    for i, playlist in enumerate(playlists, 1):
        if isinstance(playlist, dict):
            name = playlist.get("name", "Unknown")
            pid = playlist.get("id", i)
            songs = playlist.get("songs", [])
        else:
            name = getattr(playlist, "name", "Unknown")
            pid = getattr(playlist, "id", i)
            songs = getattr(playlist, "songs", [])
        text += f"<b>{i}.</b> {name} — <code>{pid}</code> — {len(songs)} songs\n"

    text += "\n<blockquote>Use <code>/playlistinfo ID</code> to view songs.</blockquote>"
    return await message.reply_text(text)


@app.on_message(filters.command("playlistinfo"))
async def playlist_info(_, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "<b>Usage:</b> <code>/playlistinfo ID</code>"
        )

    pid = message.command[1]
    playlist = await _get_playlist(message.from_user.id, pid)

    if not playlist:
        return await message.reply_text("<b>❌ Playlist not found.</b>")

    if isinstance(playlist, dict):
        name = playlist.get("name", "Unknown")
        songs = playlist.get("songs", [])
    else:
        name = getattr(playlist, "name", "Unknown")
        songs = getattr(playlist, "songs", [])

    text = f"<b>❖ PLAYLIST: {name}</b>\n\n"
    if not songs:
        text += "<i>This playlist has no songs yet.</i>"
    else:
        for i, song in enumerate(songs[:30], 1):
            if isinstance(song, dict):
                title = song.get("title") or song.get("name") or "Unknown"
                duration = song.get("duration", "")
            else:
                title = getattr(song, "title", None) or getattr(song, "name", "Unknown")
                duration = getattr(song, "duration", "")
            text += f"<b>{i}.</b> {title} {f'— {duration}' if duration else ''}\n"

        if len(songs) > 30:
            text += f"\n<i>...and {len(songs) - 30} more tracks</i>"

    return await message.reply_text(text)


@app.on_message(filters.command("deleteplaylist"))
async def delete_playlist(_, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "<b>Usage:</b> <code>/deleteplaylist ID</code>"
        )

    pid = message.command[1]
    user_id = message.from_user.id

    for method in ("delete_playlist", "delete_playlist_db"):
        fn = getattr(db, method, None)
        if fn:
            try:
                await fn(pid, user_id)
                return await message.reply_text("<b>✅ Playlist deleted successfully.</b>")
            except Exception:
                pass

    playlists = _playlist_store().get(user_id, {})
    if pid in playlists:
        del playlists[pid]
        return await message.reply_text("<b>✅ Playlist deleted successfully.</b>")

    return await message.reply_text("<b>❌ Playlist not found.</b>")


@app.on_message(filters.command("addtoplaylist"))
async def add_to_playlist(_, message):
    args = message.text.split(None, 2)
    if len(args) < 3:
        return await message.reply_text(
            "<b>Usage:</b> <code>/addtoplaylist ID song_url</code>"
        )

    pid, url = args[1], args[2]
    user_id = message.from_user.id
    playlist = await _get_playlist(user_id, pid)

    if not playlist:
        return await message.reply_text("<b>❌ Playlist not found.</b>")

    # Save URL immediately. The normal play/search system can resolve it later.
    song = {"title": url, "url": url, "duration": "", "platform": "URL"}

    for method in ("add_song_to_playlist", "add_song_to_playlist_db"):
        fn = getattr(db, method, None)
        if fn:
            try:
                await fn(pid, song)
                return await message.reply_text("<b>✅ Track added to playlist.</b>")
            except Exception:
                pass

    if isinstance(playlist, dict):
        playlist.setdefault("songs", []).append(song)
    else:
        getattr(playlist, "songs", []).append(song)

    return await message.reply_text("<b>✅ Track added to playlist.</b>")


@app.on_message(filters.command("removefromplaylist"))
async def remove_from_playlist(_, message):
    args = message.text.split(None, 2)
    if len(args) < 3:
        return await message.reply_text(
            "<b>Usage:</b> <code>/removefromplaylist ID number</code>"
        )

    pid, identifier = args[1], args[2]
    user_id = message.from_user.id
    playlist = await _get_playlist(user_id, pid)

    if not playlist:
        return await message.reply_text("<b>❌ Playlist not found.</b>")

    for method in ("remove_song_from_playlist", "remove_song_from_playlist_db"):
        fn = getattr(db, method, None)
        if fn:
            try:
                await fn(pid, identifier)
                return await message.reply_text("<b>✅ Track removed.</b>")
            except Exception:
                pass

    songs = playlist.get("songs", []) if isinstance(playlist, dict) else getattr(playlist, "songs", [])
    try:
        index = int(identifier) - 1
        if index < 0 or index >= len(songs):
            raise ValueError
        songs.pop(index)
        return await message.reply_text("<b>✅ Track removed.</b>")
    except ValueError:
        return await message.reply_text("<b>❌ Invalid song number.</b>")
