# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 🚀
#
# This source code is under MIT License 📜
# ❌ Unauthorized forking, importing, or using this code
#    without giving proper credit will result in legal action ⚠️
#
# 📩 DM for permission : @TheSigmaCoder
# ===========================================================

import random

from py_yt import VideosSearch

# =========================================================
# PER-CHAT PLAY HISTORY (in-memory, session based)
# Used only to make sure autoplay never repeats a song it
# already played for that chat.
# =========================================================
_HISTORY_LIMIT = 50
_played_history: dict[int, list[str]] = {}


def remember_played(chat_id: int, vidid: str):
    if not vidid:
        return
    hist = _played_history.setdefault(chat_id, [])
    if vidid in hist:
        hist.remove(vidid)
    hist.append(vidid)
    if len(hist) > _HISTORY_LIMIT:
        del hist[: len(hist) - _HISTORY_LIMIT]


def _history(chat_id: int) -> list:
    return _played_history.get(chat_id, [])


def clear_history(chat_id: int):
    _played_history.pop(chat_id, None)


def _extract_candidates(results, chat_id: int, skip_history: bool):
    candidates = []
    played = [] if skip_history else _history(chat_id)
    for video in results:
        vidid = video.get("id")
        title = video.get("title")
        link = video.get("link")
        duration = video.get("duration")
        if not (vidid and title and link and duration):
            continue
        if vidid in played:
            continue
        thumbs = video.get("thumbnails") or []
        thumb = thumbs[0].get("url", "").split("?")[0] if thumbs else None
        candidates.append(
            {
                "vidid": vidid,
                "title": title,
                "link": link,
                "duration_min": duration,
                "thumb": thumb,
            }
        )
    return candidates


async def fetch_autoplay_track(chat_id: int, seed_title: str):
    """
    Searches YouTube using the last played song's title and returns a
    random track that this chat hasn't already heard in this session.
    Returns None if nothing usable could be found.
    """
    if not seed_title:
        return None

    query = f"{seed_title}"
    try:
        search = VideosSearch(query, limit=20)
        data = await search.next()
        results = data.get("result", []) if isinstance(data, dict) else []
    except Exception as e:
        print(f"[AUTOPLAY SEARCH ERROR] {e}")
        return None

    if not results:
        return None

    candidates = _extract_candidates(results, chat_id, skip_history=False)

    if not candidates:
        # Everything from this search was already played recently.
        # Reset the history for this chat and try again from the same
        # result set so autoplay never just stalls out.
        clear_history(chat_id)
        candidates = _extract_candidates(results, chat_id, skip_history=True)

    if not candidates:
        return None

    return random.choice(candidates)

# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 😎
#
# 🧑‍💻 Developer : t.me/TheSigmaCoder
# 🔗 Source link : GitHub.com/Im-Notcoder/Shivi-V2
# 📢 Telegram channel : t.me/Purvi_Bots
# ===========================================================
