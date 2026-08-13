# ===========================================================
# ©️ 2025-26 ShiviMusic
# YouTube Handler - Fixed Version
# ===========================================================

import asyncio
import os
import re
from typing import Union

import aiohttp
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch


# ===========================================================
# CONFIG
# ===========================================================

API_URL = os.environ.get(
    "SHRUTI_API_URL",
    "https://api01.shrutibots.site",
)

API_KEY = os.environ.get(
    "SHRUTI_API_KEY",
    "ShrutiBotsAlSpfeG7JItQmuoxCqKd",
)

DOWNLOAD_DIR = "downloads"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# ===========================================================
# HELPERS
# ===========================================================


def time_to_seconds(time):
    """Convert HH:MM:SS / MM:SS to seconds."""
    try:
        if time is None:
            return 0

        value = str(time).strip()

        if not value:
            return 0

        parts = value.split(":")

        total = 0
        for part in parts:
            total = total * 60 + int(part)

        return total

    except (ValueError, TypeError):
        return 0


def clean_youtube_url(url: str) -> str:
    """Remove unnecessary YouTube parameters."""
    if not url:
        return url

    url = str(url).strip()

    if "&" in url:
        url = url.split("&", 1)[0]

    return url


def extract_video_id(link: str) -> str:
    """Extract YouTube video ID from URL or ID."""
    if not link:
        return ""

    link = str(link).strip()

    if "youtu.be/" in link:
        video_id = link.split("youtu.be/", 1)[1].split("?", 1)[0]
        return video_id.split("&", 1)[0]

    if "v=" in link:
        video_id = link.split("v=", 1)[1]
        return video_id.split("&", 1)[0]

    return link


def safe_filename(name: str) -> str:
    """Make filename filesystem-safe."""
    if not name:
        return "youtube"

    name = str(name)

    name = re.sub(r'[\\/:*?"<>|]', "_", name)
    name = re.sub(r"\s+", " ", name).strip()

    return name[:150] or "youtube"


# ===========================================================
# API DOWNLOAD
# ===========================================================


async def _api_download(link: str, media_type: str, extension: str):
    """
    Download media through configured API.

    Returns:
        file_path or None
    """

    video_id = extract_video_id(link)

    if not video_id or len(video_id) < 3:
        return None

    file_path = os.path.join(
        DOWNLOAD_DIR,
        f"{video_id}.{extension}",
    )

    if os.path.exists(file_path):
        try:
            if os.path.getsize(file_path) > 0:
                return file_path
        except OSError:
            pass

    params = {
        "url": video_id,
        "type": media_type,
        "api_key": API_KEY,
    }

    try:
        timeout = 600 if media_type == "video" else 300

        client_timeout = aiohttp.ClientTimeout(
            total=timeout,
            connect=30,
            sock_read=timeout,
        )

        async with aiohttp.ClientSession(
            timeout=client_timeout
        ) as session:

            async with session.get(
                f"{API_URL.rstrip('/')}/download",
                params=params,
            ) as response:

                if response.status != 200:
                    return None

                content_type = response.headers.get(
                    "Content-Type",
                    "",
                ).lower()

                # Do not save obvious JSON/API error responses
                if "application/json" in content_type:
                    return None

                with open(file_path, "wb") as output:
                    async for chunk in response.content.iter_chunked(
                        131072
                    ):
                        if chunk:
                            output.write(chunk)

        if os.path.exists(file_path):
            if os.path.getsize(file_path) > 0:
                return file_path

        return None

    except (
        asyncio.TimeoutError,
        aiohttp.ClientError,
        OSError,
    ):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except OSError:
            pass

        return None

    except Exception:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except OSError:
            pass

        return None


async def download_song(link: str) -> str:
    """Download audio."""
    return await _api_download(
        link,
        "audio",
        "mp3",
    )


async def download_video(link: str) -> str:
    """Download video."""
    return await _api_download(
        link,
        "video",
        "mp4",
    )


# ===========================================================
# YOUTUBE API
# ===========================================================


class YouTubeAPI:

    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="

        self.reg = re.compile(
            r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])"
        )

    # =======================================================
    # EXISTS
    # =======================================================

    async def exists(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):
        if not link:
            return False

        try:
            if videoid:
                link = self.base + str(link)

            return bool(
                re.search(
                    self.regex,
                    str(link),
                    re.IGNORECASE,
                )
            )

        except Exception:
            return False

    # =======================================================
    # URL FROM TELEGRAM MESSAGE
    # =======================================================

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

            # Text URL
            if message.entities:

                for entity in message.entities:

                    if entity.type == MessageEntityType.URL:

                        text = (
                            message.text
                            or message.caption
                            or ""
                        )

                        return text[
                            entity.offset:
                            entity.offset + entity.length
                        ]

            # Hidden text-link
            if message.caption_entities:

                for entity in message.caption_entities:

                    if (
                        entity.type
                        == MessageEntityType.TEXT_LINK
                    ):
                        return entity.url

        return None

    # =======================================================
    # SEARCH DETAILS
    # =======================================================

    async def details(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        if not link:
            raise ValueError(
                "YouTube link is empty"
            )

        if videoid:
            link = self.base + str(link)

        link = clean_youtube_url(link)

        results = VideosSearch(
            link,
            limit=1,
        )

        response = await results.next()

        items = (
            response.get("result", [])
            if isinstance(response, dict)
            else []
        )

        if not items:
            raise ValueError(
                "YouTube search returned no result"
            )

        result = items[0]

        title = result.get(
            "title",
            "Unknown Title",
        )

        duration_min = result.get(
            "duration"
        )

        thumbnail_list = result.get(
            "thumbnails"
        ) or []

        thumbnail = ""

        if thumbnail_list:
            first_thumbnail = thumbnail_list[0]

            if isinstance(
                first_thumbnail,
                dict,
            ):
                thumbnail = first_thumbnail.get(
                    "url",
                    "",
                )

        thumbnail = thumbnail.split(
            "?",
            1,
        )[0]

        vidid = result.get(
            "id"
        )

        if not vidid:
            raise ValueError(
                "YouTube video ID not found"
            )

        duration_sec = time_to_seconds(
            duration_min
        )

        return (
            title,
            duration_min,
            duration_sec,
            thumbnail,
            vidid,
        )

    # =======================================================
    # TITLE
    # =======================================================

    async def title(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = self.base + str(link)

        link = clean_youtube_url(link)

        results = VideosSearch(
            link,
            limit=1,
        )

        response = await results.next()

        items = (
            response.get("result", [])
            if isinstance(response, dict)
            else []
        )

        if not items:
            return None

        return items[0].get(
            "title"
        )

    # =======================================================
    # DURATION
    # =======================================================

    async def duration(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = self.base + str(link)

        link = clean_youtube_url(link)

        results = VideosSearch(
            link,
            limit=1,
        )

        response = await results.next()

        items = (
            response.get("result", [])
            if isinstance(response, dict)
            else []
        )

        if not items:
            return None

        return items[0].get(
            "duration"
        )

    # =======================================================
    # THUMBNAIL
    # =======================================================

    async def thumbnail(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = self.base + str(link)

        link = clean_youtube_url(link)

        results = VideosSearch(
            link,
            limit=1,
        )

        response = await results.next()

        items = (
            response.get("result", [])
            if isinstance(response, dict)
            else []
        )

        if not items:
            return None

        thumbnails = items[0].get(
            "thumbnails"
        ) or []

        if not thumbnails:
            return None

        thumbnail = thumbnails[0].get(
            "url",
            "",
        )

        return thumbnail.split(
            "?",
            1,
        )[0]

    # =======================================================
    # VIDEO DOWNLOAD
    # =======================================================

    async def video(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        if not link:
            return 0, "Video link is empty"

        if videoid:
            link = self.base + str(link)

        link = clean_youtube_url(link)

        try:
            downloaded_file = await download_video(
                link
            )

            if downloaded_file:
                return 1, downloaded_file

            return 0, "Video download failed"

        except Exception as e:
            return 0, f"Video download error: {e}"

    # =======================================================
    # PLAYLIST
    # =======================================================

    async def playlist(
        self,
        link,
        limit,
        user_id=None,
        videoid: Union[bool, str] = None,
    ):
        """
        Get video IDs from YouTube playlist.

        Uses yt-dlp instead of the missing Playlist import
        from the old source.
        """

        if not link:
            return []

        if videoid:
            link = self.listbase + str(link)

        link = str(link).strip()

        try:
            limit = int(limit)
        except (
            ValueError,
            TypeError,
        ):
            limit = 10

        if limit <= 0:
            return []

        ytdl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,
            "skip_download": True,
            "playlistend": limit,
        }

        def extract():
            with yt_dlp.YoutubeDL(
                ytdl_opts
            ) as ydl:

                return ydl.extract_info(
                    link,
                    download=False,
                )

        try:
            info = await asyncio.to_thread(
                extract
            )

        except Exception:
            return []

        if not info:
            return []

        entries = info.get(
            "entries"
        ) or []

        ids = []

        for entry in entries:

            if not entry:
                continue

            vid = (
                entry.get("id")
                if isinstance(entry, dict)
                else None
            )

            if not vid:
                continue

            ids.append(
                str(vid)
            )

            if len(ids) >= limit:
                break

        return ids

    # =======================================================
    # TRACK
    # =======================================================

    async def track(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        if not link:
            raise ValueError(
                "YouTube query is empty"
            )

        if videoid:
            link = self.base + str(link)

        link = clean_youtube_url(link)

        results = VideosSearch(
            link,
            limit=1,
        )

        response = await results.next()

        items = (
            response.get("result", [])
            if isinstance(response, dict)
            else []
        )

        if not items:
            raise ValueError(
                "YouTube search returned no result"
            )

        result = items[0]

        title = result.get(
            "title",
            "Unknown Title",
        )

        duration_min = result.get(
            "duration"
        )

        vidid = result.get(
            "id"
        )

        yturl = result.get(
            "link"
        )

        thumbnails = result.get(
            "thumbnails"
        ) or []

        thumbnail = ""

        if thumbnails:
            thumbnail = thumbnails[0].get(
                "url",
                "",
            )

        thumbnail = thumbnail.split(
            "?",
            1,
        )[0]

        if not vidid:
            raise ValueError(
                "YouTube video ID not found"
            )

        if not yturl:
            yturl = self.base + str(vidid)

        track_details = {
            "title": title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }

        return (
            track_details,
            vidid,
        )

    # =======================================================
    # FORMATS
    # =======================================================

    async def formats(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        if not link:
            return [], link

        if videoid:
            link = self.base + str(link)

        link = clean_youtube_url(link)

        ytdl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
        }

        def extract_formats():
            with yt_dlp.YoutubeDL(
                ytdl_opts
            ) as ydl:

                return ydl.extract_info(
                    link,
                    download=False,
                )

        try:
            info = await asyncio.to_thread(
                extract_formats
            )

        except Exception:
            return [], link

        if not info:
            return [], link

        formats_available = []

        for fmt in info.get(
            "formats",
            [],
        ):

            try:
                format_name = str(
                    fmt.get(
                        "format",
                        "",
                    )
                )

                if "dash" in format_name.lower():
                    continue

                formats_available.append(
                    {
                        "format": format_name,
                        "filesize": fmt.get(
                            "filesize"
                        ),
                        "format_id": fmt.get(
                            "format_id"
                        ),
                        "ext": fmt.get(
                            "ext"
                        ),
                        "format_note": fmt.get(
                            "format_note"
                        ),
                        "yturl": link,
                    }
                )

            except Exception:
                continue

        return (
            formats_available,
            link,
        )

    # =======================================================
    # SLIDER
    # =======================================================

    async def slider(
        self,
        link: str,
        query_type: int,
        videoid: Union[bool, str] = None,
    ):

        if not link:
            raise ValueError(
                "YouTube search query is empty"
            )

        if videoid:
            link = self.base + str(link)

        link = clean_youtube_url(link)

        try:
            query_type = int(
                query_type
            )
        except (
            ValueError,
            TypeError,
        ):
            query_type = 0

        query_type = max(
            0,
            min(
                query_type,
                9,
            ),
        )

        results = VideosSearch(
            link,
            limit=10,
        )

        response = await results.next()

        items = (
            response.get("result", [])
            if isinstance(response, dict)
            else []
        )

        if not items:
            raise ValueError(
                "No YouTube results found"
            )

        if query_type >= len(items):
            query_type = len(items) - 1

        result = items[query_type]

        title = result.get(
            "title",
            "Unknown Title",
        )

        duration_min = result.get(
            "duration"
        )

        vidid = result.get(
            "id"
        )

        thumbnails = result.get(
            "thumbnails"
        ) or []

        thumbnail = ""

        if thumbnails:
            thumbnail = thumbnails[0].get(
                "url",
                "",
            )

        thumbnail = thumbnail.split(
            "?",
            1,
        )[0]

        if not vidid:
            raise ValueError(
                "YouTube video ID not found"
            )

        return (
            title,
            duration_min,
            thumbnail,
            vidid,
        )

    # =======================================================
    # DOWNLOAD
    # =======================================================

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
    ):
        """
        Compatible with existing stream.py/play.py.

        Returns:
            (file_path, True)
            or
            (None, False)
        """

        if not link:
            return None, False

        if videoid:
            link = self.base + str(link)

        link = clean_youtube_url(link)

        try:

            # Video requested
            if video:
                downloaded_file = await download_video(
                    link
                )

            # Audio requested
            else:
                downloaded_file = await download_song(
                    link
                )

            if downloaded_file:
                return (
                    downloaded_file,
                    True,
                )

            return (
                None,
                False,
            )

        except Exception:
            return (
                None,
                False,
            )


# ===========================================================
# INSTANCE
# ===========================================================

YouTube = YouTubeAPI()
