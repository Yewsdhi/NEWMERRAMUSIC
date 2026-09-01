import asyncio
import os
import random
import re
from typing import Union

import aiohttp
import yt_dlp

from mutagen import File as MutagenFile
from mutagen.id3 import ID3, TIT2, TPE1

from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import Playlist


# =========================================================
# CONFIG
# =========================================================

API_URL = os.environ.get(
    "SHRUTI_API_URL",
    "https://api.shrutibots.site",
).rstrip("/")

# Keep API key in environment variable.
# Example:
# SHRUTI_API_KEY=your_key_here
API_KEY = os.environ.get("SHRUTI_API_KEY", "").strip()

# Optional exported Netscape-format cookies file.
# Set YTDLP_COOKIES_FILE to a secure Heroku-mounted/managed path if you
# legitimately have permission to use the cookies. Never hard-code cookies.
YTDLP_COOKIES_FILE = os.environ.get("YTDLP_COOKIES_FILE", "").strip()

DOWNLOAD_DIR = "downloads"


# =========================================================
# HELPERS
# =========================================================


def time_to_seconds(value):
    if not value:
        return 0

    try:
        total = 0

        for part in str(value).split(":"):
            total = total * 60 + int(part)

        return total

    except (ValueError, TypeError):
        return 0


def _clean_youtube_url(link: str) -> str:
    if not link:
        return ""

    link = str(link).strip()

    if re.fullmatch(r"[\w-]{6,}", link):
        return (
            "https://www.youtube.com/watch?v="
            + link
        )

    if "youtu.be/" in link:
        vid = (
            link.split("youtu.be/", 1)[1]
            .split("?", 1)[0]
            .split("&", 1)[0]
            .split("/", 1)[0]
        )

        return (
            "https://www.youtube.com/watch?v="
            + vid
        )

    if "youtube.com/watch" in link and "v=" in link:
        vid = (
            link.split("v=", 1)[1]
            .split("&", 1)[0]
            .split("#", 1)[0]
        )

        return (
            "https://www.youtube.com/watch?v="
            + vid
        )

    if "youtube.com" in link and "v=" in link:
        vid = (
            link.split("v=", 1)[1]
            .split("&", 1)[0]
            .split("#", 1)[0]
        )

        return (
            "https://www.youtube.com/watch?v="
            + vid
        )

    if "youtube.com/embed/" in link:
        vid = (
            link.split(
                "youtube.com/embed/",
                1,
            )[1]
            .split("?", 1)[0]
            .split("&", 1)[0]
            .split("/", 1)[0]
        )

        return (
            "https://www.youtube.com/watch?v="
            + vid
        )

    if "youtube.com/shorts/" in link:
        vid = (
            link.split(
                "youtube.com/shorts/",
                1,
            )[1]
            .split("?", 1)[0]
            .split("&", 1)[0]
            .split("/", 1)[0]
        )

        return (
            "https://www.youtube.com/watch?v="
            + vid
        )

    return link


def _video_id(link: str) -> str:
    if not link:
        return ""

    clean = _clean_youtube_url(link)

    if "v=" in clean:
        return (
            clean.split("v=", 1)[1]
            .split("&", 1)[0]
            .split("?", 1)[0]
            .split("#", 1)[0]
            .strip()
        )

    return ""


def _is_video_id(value: str) -> bool:
    value = str(value or "").strip()

    return bool(
        re.fullmatch(
            r"[\w-]{6,20}",
            value,
        )
    )


def _normalize_title(value: str) -> str:
    value = str(value or "").lower().strip()

    value = re.sub(
        r"\([^)]*\)|\[[^]]*\]",
        " ",
        value,
    )

    value = re.sub(
        r"\b("
        r"official|video|audio|lyrics|lyric|full|song|music|"
        r"hd|4k|remastered|version|visualizer|mv|"
        r"lvideo|fullvideo|status"
        r")\b",
        " ",
        value,
    )

    return re.sub(
        r"[^a-z0-9]+",
        "",
        value,
    )


def _title_words(value: str):
    value = str(value or "").lower()

    value = re.sub(
        r"\([^)]*\)|\[[^]]*\]",
        " ",
        value,
    )

    value = re.sub(
        r"\b("
        r"official|video|audio|lyrics|lyric|full|song|music|"
        r"hd|4k|remastered|version|visualizer|mv"
        r")\b",
        " ",
        value,
    )

    words = re.findall(
        r"[a-z0-9]+",
        value,
    )

    return {
        word
        for word in words
        if len(word) >= 4
    }


def _safe_artist(value: str) -> str:
    """
    Clean artist/uploader/channel name.
    """

    value = str(value or "").strip()

    if not value:
        return ""

    invalid = {
        "youtube",
        "unknown",
        "unknown artist",
        "youtube music",
    }

    if value.lower() in invalid:
        return ""

    return value


def _get_artist_from_info(info) -> str:
    """
    Try multiple yt-dlp fields for artist.
    """

    if not info:
        return ""

    possible = [
        info.get("artist"),
        info.get("creator"),
        info.get("album_artist"),
        info.get("uploader"),
        info.get("channel"),
    ]

    for value in possible:
        value = _safe_artist(value)

        if value:
            return value

    return ""


# =========================================================
# YT-DLP OPTIONS
# =========================================================


def _ydl_opts():
    return {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "skip_download": True,
        "socket_timeout": 30,
        "retries": 2,
        "fragment_retries": 2,
        "extractor_retries": 2,
        "extractor_args": {
            "youtube": {
                "player_client": [
                    "android",
                    "web",
                ],
            },
        },
    }


async def _extract_info(
    link: str,
    download=False,
    opts=None,
):
    def run():
        options = dict(_ydl_opts())

        if opts:
            options.update(opts)

        options["skip_download"] = not download
        if YTDLP_COOKIES_FILE and os.path.isfile(YTDLP_COOKIES_FILE):
            options["cookiefile"] = YTDLP_COOKIES_FILE

        with yt_dlp.YoutubeDL(
            options
        ) as ydl:
            return ydl.extract_info(
                link,
                download=download,
            )

    return await asyncio.to_thread(run)


async def _search_youtube(query: str):
    def run():
        options = _ydl_opts()
        options["extract_flat"] = True

        with yt_dlp.YoutubeDL(
            options
        ) as ydl:

            data = ydl.extract_info(
                f"ytsearch1:{query}",
                download=False,
            )

            entries = data.get(
                "entries"
            ) or []

            return (
                entries[0]
                if entries
                else None
            )

    return await asyncio.to_thread(run)


# =========================================================
# YOUTUBE TITLE
# =========================================================


async def _get_youtube_title(
    video_id: str,
) -> str:

    video_id = str(
        video_id or ""
    ).strip()

    if not video_id:
        return ""

    url = (
        "https://www.youtube.com/oembed"
        "?url=https://www.youtube.com/watch?v="
        f"{video_id}&format=json"
    )

    try:
        timeout = aiohttp.ClientTimeout(
            total=20
        )

        async with aiohttp.ClientSession(
            timeout=timeout
        ) as session:

            async with session.get(
                url,
                allow_redirects=True,
            ) as response:

                if response.status == 200:

                    data = await response.json(
                        content_type=None
                    )

                    title = str(
                        data.get("title")
                        or ""
                    ).strip()

                    if (
                        title
                        and not _is_video_id(title)
                        and title.lower()
                        != "youtube"
                    ):
                        return title

    except Exception:
        pass

    return ""


async def _get_youtube_details_fallback(
    video_id: str,
):
    video_id = str(
        video_id or ""
    ).strip()

    if not video_id:
        return None

    try:
        result = await _search_youtube(
            f"https://www.youtube.com/watch?v={video_id}"
        )

        if result:
            return result

    except Exception:
        pass

    return None


# =========================================================
# REAL TITLE
# =========================================================


async def _resolve_real_title(
    info,
    video_id: str,
    fallback_query: str = "",
):

    video_id = str(
        video_id or ""
    ).strip()

    title = str(
        (info or {}).get("title")
        or ""
    ).strip()

    invalid_titles = {
        "",
        "unknown title",
        "youtube",
        "youtube music",
        video_id.lower(),
    }

    if title.lower() in invalid_titles:
        title = ""

    if _is_video_id(title):
        title = ""

    if not title and video_id:
        title = await _get_youtube_title(
            video_id
        )

    if not title and video_id:

        fallback = (
            await _get_youtube_details_fallback(
                video_id
            )
        )

        if fallback:

            found_title = str(
                fallback.get("title")
                or ""
            ).strip()

            if (
                found_title
                and not _is_video_id(
                    found_title
                )
                and found_title.lower()
                not in invalid_titles
            ):
                title = found_title

    if not title and fallback_query:

        search = await _search_youtube(
            fallback_query
        )

        if search:

            found_title = str(
                search.get("title")
                or ""
            ).strip()

            if (
                found_title
                and not _is_video_id(
                    found_title
                )
            ):
                title = found_title

    if not title:
        title = "Unknown Song"

    return title


# =========================================================
# AUDIO METADATA
# =========================================================


async def _set_audio_metadata(
    file_path: str,
    video_id: str,
    title: str = "",
    performer: str = "",
):
    """
    Write proper title + artist into downloaded audio.

    This is the important fix for Telegram showing:
        YouTube

    Instead it will use:
        Real Song Title
        Real Artist
    """

    if not file_path:
        return file_path

    if not os.path.exists(file_path):
        return file_path

    try:

        title = str(
            title or ""
        ).strip()

        performer = _safe_artist(
            performer
        )

        # -------------------------------------------------
        # Get title if missing
        # -------------------------------------------------

        if not title and video_id:
            title = await _get_youtube_title(
                video_id
            )

        if (
            not title
            or title.lower() == "youtube"
            or _is_video_id(title)
        ):
            title = "Unknown Song"

        # -------------------------------------------------
        # Default artist
        # -------------------------------------------------

        if not performer:
            performer = "Unknown Artist"

        # -------------------------------------------------
        # MP3
        # -------------------------------------------------

        if file_path.lower().endswith(
            ".mp3"
        ):

            try:
                tags = ID3(
                    file_path
                )

            except Exception:
                tags = ID3()

            # Remove old values.
            try:
                tags.delall("TIT2")
            except Exception:
                pass

            try:
                tags.delall("TPE1")
            except Exception:
                pass

            tags.add(
                TIT2(
                    encoding=3,
                    text=[title],
                )
            )

            tags.add(
                TPE1(
                    encoding=3,
                    text=[performer],
                )
            )

            tags.save(
                file_path
            )

            return file_path

        # -------------------------------------------------
        # M4A / MP4
        # -------------------------------------------------

        if file_path.lower().endswith(
            (
                ".m4a",
                ".mp4",
            )
        ):

            try:
                audio = MutagenFile(
                    file_path,
                    easy=False,
                )

                if audio is not None:

                    audio["\xa9nam"] = [
                        title
                    ]

                    audio["\xa9ART"] = [
                        performer
                    ]

                    audio.save()

            except Exception:
                pass

            return file_path

        # -------------------------------------------------
        # WEBM / OPUS / OTHER
        # -------------------------------------------------

        try:

            audio = MutagenFile(
                file_path,
                easy=False,
            )

            if audio is not None:

                if audio.tags is None:
                    try:
                        audio.add_tags()
                    except Exception:
                        pass

                if audio.tags is not None:

                    try:
                        audio.tags[
                            "TITLE"
                        ] = title
                    except Exception:
                        pass

                    try:
                        audio.tags[
                            "ARTIST"
                        ] = performer
                    except Exception:
                        pass

                    try:
                        audio.save()
                    except Exception:
                        pass

        except Exception:
            pass

        return file_path

    except Exception:
        return file_path


# =========================================================
# DOWNLOAD SONG
# =========================================================


async def download_song(
    link: str,
    title: str = "",
    performer: str = "",
) -> Union[str, None]:

    url = _clean_youtube_url(
        link
    )

    vid = _video_id(
        url
    )

    if not vid:
        return None

    os.makedirs(
        DOWNLOAD_DIR,
        exist_ok=True,
    )

    cached = os.path.join(
        DOWNLOAD_DIR,
        f"{vid}.mp3",
    )

    # -------------------------------------------------
    # Fetch metadata
    # -------------------------------------------------

    info = None

    try:
        info = await _extract_info(
            url
        )
    except Exception:
        info = None

    if not title:

        title = await _resolve_real_title(
            info,
            vid,
            "",
        )

    if not performer:
        performer = _get_artist_from_info(
            info
        )

    # -------------------------------------------------
    # Cached file
    # -------------------------------------------------

    if (
        os.path.exists(cached)
        and os.path.getsize(cached) > 0
    ):

        await _set_audio_metadata(
            cached,
            vid,
            title,
            performer,
        )

        return cached

    # =================================================
    # API DOWNLOAD
    # =================================================

    if API_URL and API_KEY:

        try:

            timeout = aiohttp.ClientTimeout(
                total=300
            )

            async with aiohttp.ClientSession(
                timeout=timeout
            ) as session:

                async with session.get(
                    f"{API_URL}/download",
                    params={
                        "url": vid,
                        "type": "audio",
                        "api_key": API_KEY,
                    },
                ) as resp:

                    if resp.status == 200:

                        content_type = (
                            resp.headers.get(
                                "content-type",
                                "",
                            )
                            .lower()
                        )

                        if (
                            "text/"
                            not in content_type
                            and "json"
                            not in content_type
                        ):

                            tmp = (
                                cached
                                + ".part"
                            )

                            try:

                                with open(
                                    tmp,
                                    "wb",
                                ) as file:

                                    async for chunk in (
                                        resp.content.iter_chunked(
                                            131072
                                        )
                                    ):

                                        if chunk:
                                            file.write(
                                                chunk
                                            )

                                if (
                                    os.path.exists(
                                        tmp
                                    )
                                    and os.path.getsize(
                                        tmp
                                    )
                                    > 0
                                ):

                                    os.replace(
                                        tmp,
                                        cached,
                                    )

                                    await _set_audio_metadata(
                                        cached,
                                        vid,
                                        title,
                                        performer,
                                    )

                                    return cached

                            except Exception:

                                if os.path.exists(
                                    tmp
                                ):
                                    try:
                                        os.remove(
                                            tmp
                                        )
                                    except Exception:
                                        pass

        except Exception:
            pass

    # =================================================
    # YT-DLP FALLBACK
    # =================================================

    try:

        def run():

            base = os.path.join(
                DOWNLOAD_DIR,
                vid,
            )

            opts = {
                "format": (
                    "bestaudio[ext=m4a]/"
                    "bestaudio/best"
                ),
                "outtmpl": (
                    base
                    + ".%(ext)s"
                ),
                "noplaylist": True,
                "quiet": True,
                "no_warnings": True,
                "socket_timeout": 30,
                "retries": 2,
                "fragment_retries": 2,
                "extractor_retries": 2,
                "extractor_args": {
                    "youtube": {
                        "player_client": [
                            "android",
                            "web",
                        ],
                    },
                },
            }

            with yt_dlp.YoutubeDL(
                opts
            ) as ydl:

                ydl.download(
                    [url]
                )

            candidates = [
                base + ".m4a",
                base + ".webm",
                base + ".opus",
                base + ".mp3",
                base + ".aac",
            ]

            for path in candidates:

                if (
                    os.path.exists(path)
                    and os.path.getsize(path)
                    > 0
                ):
                    return path

            return None

        file_path = await asyncio.to_thread(
            run
        )

        if file_path:

            await _set_audio_metadata(
                file_path,
                vid,
                title,
                performer,
            )

            return file_path

        return None

    except Exception as error:
        print(f"[YouTube] audio download failed: {type(error).__name__}: {error}")
        return None


# =========================================================
# DOWNLOAD VIDEO
# =========================================================


async def download_video(
    link: str,
) -> Union[str, None]:

    url = _clean_youtube_url(
        link
    )

    vid = _video_id(
        url
    )

    if not vid:
        return None

    os.makedirs(
        DOWNLOAD_DIR,
        exist_ok=True,
    )

    path = os.path.join(
        DOWNLOAD_DIR,
        f"{vid}.mp4",
    )

    # -------------------------------------------------
    # Existing video
    # -------------------------------------------------

    if (
        os.path.exists(path)
        and os.path.getsize(path) > 0
    ):
        return path

    # =================================================
    # API
    # =================================================

    if API_URL and API_KEY:

        try:

            timeout = aiohttp.ClientTimeout(
                total=600
            )

            async with aiohttp.ClientSession(
                timeout=timeout
            ) as session:

                async with session.get(
                    f"{API_URL}/download",
                    params={
                        "url": vid,
                        "type": "video",
                        "api_key": API_KEY,
                    },
                ) as resp:

                    if resp.status == 200:

                        content_type = (
                            resp.headers.get(
                                "content-type",
                                "",
                            )
                            .lower()
                        )

                        if (
                            "text/"
                            not in content_type
                            and "json"
                            not in content_type
                        ):

                            tmp = (
                                path
                                + ".part"
                            )

                            try:

                                with open(
                                    tmp,
                                    "wb",
                                ) as file:

                                    async for chunk in (
                                        resp.content.iter_chunked(
                                            131072
                                        )
                                    ):

                                        if chunk:
                                            file.write(
                                                chunk
                                            )

                                if (
                                    os.path.exists(
                                        tmp
                                    )
                                    and os.path.getsize(
                                        tmp
                                    ) > 0
                                ):

                                    os.replace(
                                        tmp,
                                        path,
                                    )

                                    return path

                            except Exception:

                                if os.path.exists(
                                    tmp
                                ):
                                    try:
                                        os.remove(
                                            tmp
                                        )
                                    except Exception:
                                        pass

        except Exception:
            pass

    # =================================================
    # YT-DLP
    # =================================================

    try:

        def run():

            opts = {
                "format": (
                    "bestvideo+bestaudio/"
                    "best"
                ),
                "merge_output_format": "mp4",
                "outtmpl": path,
                "noplaylist": True,
                "quiet": True,
                "no_warnings": True,
                "socket_timeout": 30,
                "retries": 2,
                "fragment_retries": 2,
                "extractor_retries": 2,
                "extractor_args": {
                    "youtube": {
                        "player_client": [
                            "android",
                            "web",
                        ],
                    },
                },
            }

            with yt_dlp.YoutubeDL(
                opts
            ) as ydl:

                ydl.download(
                    [url]
                )

            if (
                os.path.exists(path)
                and os.path.getsize(path) > 0
            ):
                return path

            return None

        return await asyncio.to_thread(
            run
        )

    except Exception as error:
        print(f"[YouTube] video download failed: {type(error).__name__}: {error}")
        return None


# =========================================================
# YOUTUBE API
# =========================================================


class YouTubeAPI:

    def __init__(self):

        self.base = (
            "https://www.youtube.com/watch?v="
        )

        self.regex = (
            r"(?:youtube\.com|youtu\.be)"
        )

        self.status = (
            "https://www.youtube.com/oembed?url="
        )

        self.listbase = (
            "https://youtube.com/playlist?list="
        )

        self.reg = re.compile(
            r"\x1B(?:[@-Z\\-_]|"
            r"\[[0-?]*[ -/]*[@-~])"
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
            link = (
                self.base
                + str(link)
            )

        return bool(
            re.search(
                self.regex,
                str(link),
            )
        )

    # =====================================================
    # URL
    # =====================================================

    async def url(
        self,
        message_1: Message,
    ) -> Union[str, None]:

        messages = [
            message_1
        ]

        if message_1.reply_to_message:
            messages.append(
                message_1.reply_to_message
            )

        for message in messages:

            text = (
                message.text
                or message.caption
                or ""
            )

            entities = (
                message.entities
                or message.caption_entities
                or []
            )

            for entity in entities:

                if (
                    entity.type
                    == MessageEntityType.URL
                ):

                    return text[
                        entity.offset:
                        entity.offset
                        + entity.length
                    ]

                if (
                    entity.type
                    == MessageEntityType.TEXT_LINK
                    and entity.url
                ):

                    return entity.url

        return None

    # =====================================================
    # DETAILS
    # =====================================================

    async def details(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        url = (
            self.base
            + str(link).strip()
            if videoid
            else _clean_youtube_url(link)
        )

        actual_video_id = _video_id(
            url
        )

        info = None

        try:
            info = await _extract_info(
                url
            )
        except Exception:
            info = None

        if not info:

            try:
                info = await _search_youtube(
                    url
                )
            except Exception:
                info = None

        vidid = str(
            (info or {}).get("id")
            or actual_video_id
            or ""
        ).strip()

        title = await _resolve_real_title(
            info,
            vidid,
            str(link),
        )

        duration_sec = int(
            (info or {}).get(
                "duration"
            )
            or 0
        )

        duration_min = (
            f"{duration_sec // 60}:"
            f"{duration_sec % 60:02d}"
            if duration_sec
            else "00:00"
        )

        thumbnail = (
            (info or {}).get(
                "thumbnail"
            )
            or (
                f"https://i.ytimg.com/vi/"
                f"{vidid}/hqdefault.jpg"
                if vidid
                else ""
            )
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

        return (
            await self.details(
                link,
                videoid,
            )
        )[0]

    # =====================================================
    # DURATION
    # =====================================================

    async def duration(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        return (
            await self.details(
                link,
                videoid,
            )
        )[1]

    # =====================================================
    # THUMBNAIL
    # =====================================================

    async def thumbnail(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        return (
            await self.details(
                link,
                videoid,
            )
        )[3]

    # =====================================================
    # VIDEO
    # =====================================================

    async def video(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        url = (
            self.base
            + str(link)
            if videoid
            else _clean_youtube_url(link)
        )

        try:

            downloaded_file = (
                await download_video(
                    url
                )
            )

            if downloaded_file:
                return (
                    1,
                    downloaded_file,
                )

            return (
                0,
                "Video download failed",
            )

        except Exception as error:

            return (
                0,
                f"Video download error: {error}",
            )

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
            link = (
                self.listbase
                + str(link)
            )

        if "&" in link:
            link = link.split(
                "&"
            )[0]

        try:

            plist = await Playlist.get(
                link
            )

            videos = (
                plist.get("videos")
                or []
            )

            return [
                video.get("id")
                for video in videos[:limit]
                if (
                    video
                    and video.get("id")
                )
            ]

        except Exception:
            return []

    # =====================================================
    # TRACK
    # =====================================================

    async def track(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        url = (
            self.base
            + str(link).strip()
            if videoid
            else _clean_youtube_url(link)
        )

        info = None

        try:

            if (
                videoid
                or re.search(
                    self.regex,
                    str(url),
                )
            ):

                info = await _extract_info(
                    url
                )

        except Exception:
            info = None

        if not info:

            try:
                info = await _search_youtube(
                    link
                )
            except Exception:
                info = None

        if not info:

            raise ValueError(
                "YouTube track details "
                "could not be fetched"
            )

        vidid = str(
            info.get("id")
            or _video_id(url)
            or ""
        ).strip()

        if not vidid:

            raise ValueError(
                "YouTube video ID not found"
            )

        title = await _resolve_real_title(
            info,
            vidid,
            str(link),
        )

        artist = _get_artist_from_info(
            info
        )

        duration_sec = int(
            info.get("duration")
            or 0
        )

        duration_min = (
            f"{duration_sec // 60}:"
            f"{duration_sec % 60:02d}"
            if duration_sec
            else "00:00"
        )

        yturl = (
            "https://www.youtube.com/watch?v="
            f"{vidid}"
        )

        thumbnail = (
            info.get("thumbnail")
            or (
                f"https://i.ytimg.com/vi/"
                f"{vidid}/hqdefault.jpg"
            )
        )

        return {
            "title": title,
            "artist": artist,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }, vidid

    # =====================================================
    # AUTOPLAY
    # =====================================================

    async def autoplay(
        self,
        videoid: str,
        title: str = "",
        max_duration: Union[int, None] = None,
        exclude_ids=None,
        exclude_titles=None,
    ):

        seed_id = str(
            videoid or ""
        ).strip()

        query = str(
            title or ""
        ).strip()

        if not query:
            return None

        excluded_ids = {
            str(item).strip()
            for item in (
                exclude_ids or []
            )
            if str(item).strip()
        }

        if seed_id:
            excluded_ids.add(
                seed_id
            )

        excluded_titles = {
            _normalize_title(item)
            for item in (
                exclude_titles or []
            )
            if _normalize_title(item)
        }

        current_title = _normalize_title(
            query
        )

        if current_title:
            excluded_titles.add(
                current_title
            )

        current_words = _title_words(
            query
        )

        def run_search(
            search_query
        ):

            options = _ydl_opts()

            options.update({
                "extract_flat": True,
                "ignoreerrors": True,
            })

            with yt_dlp.YoutubeDL(
                options
            ) as ydl:

                data = ydl.extract_info(
                    f"ytsearch20:{search_query}",
                    download=False,
                )

                return (
                    data.get("entries")
                    or []
                )

        search_queries = [
            "latest hindi songs official audio",
            "popular hindi bollywood songs",
            "trending hindi songs",
            "latest punjabi songs official audio",
            "popular punjabi songs",
            "latest english songs official audio",
            "popular english songs",
            "latest haryanvi songs official audio",
            "popular haryanvi songs",
            "latest bhojpuri songs official audio",
            "popular bhojpuri songs",
        ]

        random.shuffle(
            search_queries
        )

        candidates = []
        seen_ids = set()
        seen_titles = set()

        for search_query in search_queries:

            try:

                entries = await asyncio.to_thread(
                    run_search,
                    search_query,
                )

            except Exception:
                continue

            for entry in entries:

                if not entry:
                    continue

                candidate_id = str(
                    entry.get("id")
                    or ""
                ).strip()

                song_title = str(
                    entry.get("title")
                    or ""
                ).strip()

                if (
                    not candidate_id
                    or not song_title
                    or _is_video_id(
                        song_title
                    )
                ):
                    continue

                if candidate_id in excluded_ids:
                    continue

                if candidate_id in seen_ids:
                    continue

                normalized_title = (
                    _normalize_title(
                        song_title
                    )
                )

                if (
                    not normalized_title
                    or normalized_title
                    in excluded_titles
                    or normalized_title
                    in seen_titles
                ):
                    continue

                duration_sec = int(
                    entry.get(
                        "duration"
                    )
                    or 0
                )

                if duration_sec <= 0:
                    continue

                if (
                    max_duration
                    and duration_sec
                    > int(max_duration)
                ):
                    continue

                candidate_words = _title_words(
                    song_title
                )

                overlap = (
                    current_words
                    & candidate_words
                )

                if (
                    len(current_words) >= 2
                    and len(overlap) >= 2
                ):
                    continue

                seen_ids.add(
                    candidate_id
                )

                seen_titles.add(
                    normalized_title
                )

                candidates.append({
                    "id": candidate_id,
                    "title": song_title,
                    "duration": duration_sec,
                    "entry": entry,
                })

                if len(candidates) >= 40:
                    break

            if len(candidates) >= 40:
                break

        if not candidates:
            return None

        selected = random.choice(
            candidates
        )

        entry = selected[
            "entry"
        ]

        candidate_id = selected[
            "id"
        ]

        song_title = selected[
            "title"
        ]

        duration_sec = selected[
            "duration"
        ]

        thumbnail = (
            entry.get("thumbnail")
            or (
                f"https://i.ytimg.com/vi/"
                f"{candidate_id}/hqdefault.jpg"
            )
        )

        artist = _get_artist_from_info(
            entry
        )

        return {
            "title": song_title,
            "artist": artist,
            "link": (
                "https://www.youtube.com/"
                f"watch?v={candidate_id}"
            ),
            "vidid": candidate_id,
            "duration_sec": duration_sec,
            "duration_min": (
                f"{duration_sec // 60}:"
                f"{duration_sec % 60:02d}"
            ),
            "thumb": thumbnail,
        }

    # =====================================================
    # FORMATS
    # =====================================================

    async def formats(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        url = (
            self.base
            + str(link)
            if videoid
            else _clean_youtube_url(link)
        )

        try:

            result = await _extract_info(
                url
            )

            formats_available = []

            for fmt in (
                result.get(
                    "formats",
                    []
                )
            ):

                if (
                    "dash"
                    in str(
                        fmt.get(
                            "format",
                            "",
                        )
                    ).lower()
                ):
                    continue

                formats_available.append({
                    "format": fmt.get(
                        "format"
                    ),
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
                    "yturl": url,
                })

            return (
                formats_available,
                url,
            )

        except Exception:
            return (
                [],
                url,
            )

    # =====================================================
    # SLIDER
    # =====================================================

    async def slider(
        self,
        link: str,
        query_type: int,
        videoid: Union[bool, str] = None,
    ):

        url = (
            self.base
            + str(link)
            if videoid
            else _clean_youtube_url(link)
        )

        def run():

            opts = _ydl_opts()
            opts["extract_flat"] = True

            with yt_dlp.YoutubeDL(
                opts
            ) as ydl:

                if videoid:

                    data = ydl.extract_info(
                        url,
                        download=False,
                    )

                    if data.get(
                        "entries"
                    ):

                        return (
                            data.get(
                                "entries"
                            )
                            or []
                        )[query_type]

                    return data

                data = ydl.extract_info(
                    f"ytsearch10:{link}",
                    download=False,
                )

                entries = (
                    data.get(
                        "entries"
                    )
                    or []
                )

                return entries[
                    query_type
                ]

        result = await asyncio.to_thread(
            run
        )

        vidid = str(
            result.get("id")
            or ""
        ).strip()

        duration = int(
            result.get("duration")
            or 0
        )

        duration_min = (
            f"{duration // 60}:"
            f"{duration % 60:02d}"
            if duration
            else "00:00"
        )

        title = await _resolve_real_title(
            result,
            vidid,
            str(link),
        )

        thumb = (
            result.get(
                "thumbnail"
            )
            or (
                f"https://i.ytimg.com/vi/"
                f"{vidid}/hqdefault.jpg"
            )
        )

        return (
            title,
            duration_min,
            thumb,
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
    ):

        url = (
            self.base
            + str(link)
            if videoid
            else _clean_youtube_url(link)
        )

        try:

            if video:

                file_path = await download_video(
                    url
                )

            else:

                # title is passed from your play code.
                file_path = await download_song(
                    url,
                    title=str(
                        title or ""
                    ),
                )

            if file_path:

                return (
                    file_path,
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


# =========================================================
# GLOBAL INSTANCE
# =========================================================

YouTube = YouTubeAPI()
    
