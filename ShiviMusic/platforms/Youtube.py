import asyncio
import os
import re
from typing import Union

import aiohttp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch


# =========================================================
# CONFIG
# =========================================================

API_URL = os.environ.get(
    "SHRUTI_API_URL",
    "https://api01.shrutibots.site",
).rstrip("/")

# IMPORTANT:
# API key environment variable se set karo.
API_KEY = os.environ.get("SHRUTI_API_KEY")

DOWNLOAD_DIR = os.environ.get(
    "DOWNLOAD_DIR",
    "downloads",
)

SEARCH_LIMIT = 1

AUDIO_TIMEOUT = 300
VIDEO_TIMEOUT = 600

CHUNK_SIZE = 256 * 1024

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# =========================================================
# GLOBAL HTTP SESSION
# =========================================================

_http_session = None
_session_lock = asyncio.Lock()

_download_locks = {}


async def get_http_session():
    global _http_session

    if _http_session is not None and not _http_session.closed:
        return _http_session

    async with _session_lock:
        if _http_session is None or _http_session.closed:
            timeout = aiohttp.ClientTimeout(
                total=None,
                connect=20,
                sock_connect=20,
                sock_read=60,
            )

            connector = aiohttp.TCPConnector(
                limit=20,
                limit_per_host=10,
                ttl_dns_cache=300,
                enable_cleanup_closed=True,
            )

            _http_session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers={
                    "User-Agent": "Mozilla/5.0",
                    "Accept": "*/*",
                    "Connection": "keep-alive",
                },
            )

    return _http_session


async def close_http_session():
    global _http_session

    if _http_session is not None and not _http_session.closed:
        await _http_session.close()

    _http_session = None


# =========================================================
# HELPERS
# =========================================================

def time_to_seconds(time):
    if not time:
        return 0

    try:
        stringt = str(time)

        return sum(
            int(x) * 60 ** i
            for i, x in enumerate(
                reversed(stringt.split(":"))
            )
        )
    except Exception:
        return 0


def extract_video_id(link: str):
    if not link:
        return None

    link = str(link).strip()

    # Normal YouTube URL
    match = re.search(
        r"(?:v=|youtu\.be/|youtube\.com/shorts/|youtube\.com/live/)([A-Za-z0-9_-]{6,})",
        link,
    )

    if match:
        return match.group(1)

    # Already a video ID
    if re.fullmatch(r"[A-Za-z0-9_-]{6,}", link):
        return link

    return None


def clean_youtube_url(link: str):
    if not link:
        return None

    link = str(link).strip()

    if "&" in link:
        link = link.split("&", 1)[0]

    return link


def cache_valid(path):
    try:
        return (
            os.path.isfile(path)
            and os.path.getsize(path) > 0
        )
    except Exception:
        return False


def get_download_lock(video_id):
    lock = _download_locks.get(video_id)

    if lock is None:
        lock = asyncio.Lock()
        _download_locks[video_id] = lock

    return lock


# =========================================================
# API DOWNLOAD
# =========================================================

async def _download_from_api(
    video_id: str,
    media_type: str,
    file_path: str,
):
    if not API_KEY:
        return None

    session = await get_http_session()

    params = {
        "url": video_id,
        "type": media_type,
        "api_key": API_KEY,
    }

    timeout_value = (
        VIDEO_TIMEOUT
        if media_type == "video"
        else AUDIO_TIMEOUT
    )

    timeout = aiohttp.ClientTimeout(
        total=timeout_value,
        connect=20,
        sock_connect=20,
        sock_read=60,
    )

    temp_path = f"{file_path}.part"

    try:
        async with session.get(
            f"{API_URL}/download",
            params=params,
            timeout=timeout,
        ) as resp:

            if resp.status != 200:
                return None

            content_type = (
                resp.headers.get("Content-Type", "")
                .lower()
            )

            # API error responses ko media file samajhne se bachao.
            if (
                "text/html" in content_type
                or "application/json" in content_type
            ):
                return None

            with open(temp_path, "wb") as output:

                async for chunk in resp.content.iter_chunked(
                    CHUNK_SIZE
                ):
                    if chunk:
                        output.write(chunk)

            if not cache_valid(temp_path):
                return None

            os.replace(temp_path, file_path)

            if cache_valid(file_path):
                return file_path

            return None

    except asyncio.TimeoutError:
        return None

    except Exception:
        return None

    finally:
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception:
            pass


# =========================================================
# PUBLIC DOWNLOAD FUNCTIONS
# =========================================================

async def download_song(link: str) -> str:
    video_id = extract_video_id(link)

    if not video_id:
        return None

    file_path = os.path.join(
        DOWNLOAD_DIR,
        f"{video_id}.mp3",
    )

    # CACHE
    if cache_valid(file_path):
        return file_path

    lock = get_download_lock(video_id)

    async with lock:

        # Another request may have finished it.
        if cache_valid(file_path):
            return file_path

        return await _download_from_api(
            video_id,
            "audio",
            file_path,
        )


async def download_video(link: str) -> str:
    video_id = extract_video_id(link)

    if not video_id:
        return None

    file_path = os.path.join(
        DOWNLOAD_DIR,
        f"{video_id}.mp4",
    )

    # CACHE
    if cache_valid(file_path):
        return file_path

    lock = get_download_lock(
        f"video:{video_id}"
    )

    async with lock:

        if cache_valid(file_path):
            return file_path

        return await _download_from_api(
            video_id,
            "video",
            file_path,
        )


# =========================================================
# YOUTUBE API
# =========================================================

class YouTubeAPI:

    def __init__(self):
        self.base = (
            "https://www.youtube.com/watch?v="
        )

        self.regex = r"(?:youtube\.com|youtu\.be)"

        self.status = (
            "https://www.youtube.com/oembed?url="
        )

        self.listbase = (
            "https://youtube.com/playlist?list="
        )

        self.reg = re.compile(
            r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])"
        )

    # =====================================================
    # EXISTS
    # =====================================================

    async def exists(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):
        if videoid:
            link = self.base + link

        return bool(
            re.search(
                self.regex,
                str(link),
                re.IGNORECASE,
            )
        )

    # =====================================================
    # URL
    # =====================================================

    async def url(
        self,
        message_1: Message,
    ) -> Union[str, None]:

        messages = [message_1]

        if message_1.reply_to_message:
            messages.append(
                message_1.reply_to_message
            )

        for message in messages:

            if message.entities:

                for entity in message.entities:

                    if (
                        entity.type
                        == MessageEntityType.URL
                    ):
                        text = (
                            message.text
                            or message.caption
                            or ""
                        )

                        return text[
                            entity.offset:
                            entity.offset + entity.length
                        ]

            elif message.caption_entities:

                for entity in message.caption_entities:

                    if (
                        entity.type
                        == MessageEntityType.TEXT_LINK
                    ):
                        return entity.url

        return None

    # =====================================================
    # SEARCH
    # =====================================================

    async def _search(self, link, limit=1):
        link = clean_youtube_url(link)

        results = VideosSearch(
            link,
            limit=limit,
        )

        data = await results.next()

        return data.get("result") or []

    # =====================================================
    # DETAILS
    # =====================================================

    async def details(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = self.base + link

        result = await self._search(
            link,
            limit=SEARCH_LIMIT,
        )

        if not result:
            raise ValueError(
                "YouTube result not found"
            )

        result = result[0]

        title = result.get("title")
        duration_min = result.get("duration")
        thumbnail = (
            result.get("thumbnails", [{}])[0]
            .get("url")
            .split("?")[0]
        )
        vidid = result.get("id")

        duration_sec = (
            time_to_seconds(duration_min)
            if duration_min
            else 0
        )

        return (
            title,
            duration_min,
            duration_sec,
            thumbnail,
            vidid,
        )

    # =====================================================
    # TITLE
    # =====================================================

    async def title(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = self.base + link

        result = await self._search(link)

        if result:
            return result[0].get("title")

        return None

    # =====================================================
    # DURATION
    # =====================================================

    async def duration(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = self.base + link

        result = await self._search(link)

        if result:
            return result[0].get("duration")

        return None

    # =====================================================
    # THUMBNAIL
    # =====================================================

    async def thumbnail(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = self.base + link

        result = await self._search(link)

        if result:
            return (
                result[0]
                .get("thumbnails", [{}])[0]
                .get("url", "")
                .split("?")[0]
            )

        return None

    # =====================================================
    # VIDEO
    # =====================================================

    async def video(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = self.base + link

        try:
            downloaded_file = await download_video(
                link
            )

            if downloaded_file:
                return 1, downloaded_file

            return 0, "Video download failed"

        except Exception as e:
            return 0, str(e)

    # =====================================================
    # PLAYLIST
    # =====================================================

    async def playlist(
        self,
        link,
        limit,
        user_id,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = self.listbase + link

        if "&" in link:
            link = link.split("&")[0]

        try:
            # Keep your existing Playlist implementation
            plist = await Playlist.get(link)
        except Exception:
            return []

        videos = plist.get("videos") or []

        ids = []

        for data in videos[:limit]:

            if not data:
                continue

            vid = data.get("id")

            if vid:
                ids.append(vid)

        return ids

    # =====================================================
    # TRACK / SEARCH
    # =====================================================

    async def track(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = self.base + link

        result = await self._search(
            link,
            limit=SEARCH_LIMIT,
        )

        if not result:
            raise ValueError(
                "YouTube result not found"
            )

        result = result[0]

        title = result.get("title")
        duration_min = result.get("duration")
        vidid = result.get("id")
        yturl = result.get("link")

        thumbnail = (
            result.get("thumbnails", [{}])[0]
            .get("url", "")
            .split("?")[0]
        )

        track_details = {
            "title": title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }

        return track_details, vidid

    # =====================================================
    # FORMATS
    # =====================================================

    async def formats(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        # Kept for compatibility.
        # Your main playback path does not use this.

        try:
            import yt_dlp

            if videoid:
                link = self.base + link

            link = clean_youtube_url(link)

            opts = {
                "quiet": True,
                "no_warnings": True,
                "skip_download": True,
            }

            def extract():
                with yt_dlp.YoutubeDL(opts) as ydl:
                    return ydl.extract_info(
                        link,
                        download=False,
                    )

            info = await asyncio.to_thread(
                extract
            )

            formats_available = []

            for fmt in info.get("formats", []):

                try:
                    if "dash" in str(
                        fmt.get("format", "")
                    ).lower():
                        continue

                    formats_available.append(
                        {
                            "format": fmt.get("format"),
                            "filesize": fmt.get("filesize"),
                            "format_id": fmt.get("format_id"),
                            "ext": fmt.get("ext"),
                            "format_note": fmt.get(
                                "format_note"
                            ),
                            "yturl": link,
                        }
                    )

                except Exception:
                    continue

            return formats_available, link

        except Exception:
            return [], link

    # =====================================================
    # SLIDER
    # =====================================================

    async def slider(
        self,
        link: str,
        query_type: int,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = self.base + link

        results = await self._search(
            link,
            limit=10,
        )

        if not results:
            raise ValueError(
                "No YouTube results found"
            )

        query_type = max(
            0,
            min(
                int(query_type),
                len(results) - 1,
            ),
        )

        result = results[query_type]

        title = result.get("title")
        duration_min = result.get("duration")
        vidid = result.get("id")

        thumbnail = (
            result.get("thumbnails", [{}])[0]
            .get("url", "")
            .split("?")[0]
        )

        return (
            title,
            duration_min,
            thumbnail,
            vidid,
        )

    # =====================================================
    # DOWNLOAD
    # =====================================================

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:

        if videoid:
            link = self.base + link

        try:

            if video:
                downloaded_file = await download_video(
                    link
                )
            else:
                downloaded_file = await download_song(
                    link
                )

            if downloaded_file:
                return downloaded_file, True

            return None, False

        except Exception:
            return None, False


# =========================================================
# INSTANCE
# =========================================================

YouTube = YouTubeAPI()
