import asyncio
import os
import re
from typing import Union

import yt_dlp
import aiohttp

from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import Playlist

# VideosSearch ka import apni existing dependency ke hisaab se rakho
from py_yt import Playlist


API_URL = os.environ.get(
    "ROYAL_API_URL",
    "https://youtubeapikey-production-701a.up.railway.app"
).rstrip("/")

API_KEY = os.environ.get(
    "ROYAL_API_KEY",
    "Royal_660703bee3b31dea"
)

DOWNLOAD_DIR = "downloads"


def time_to_seconds(time):
    stringt = str(time)
    return sum(
        int(x) * 60 ** i
        for i, x in enumerate(reversed(stringt.split(":")))
    )


def youtube_full_url(link: str) -> str:
    """YouTube link ko proper full URL mein convert karta hai."""
    link = str(link).strip()

    if "youtube.com/" in link or "youtu.be/" in link:
        return link

    return f"https://www.youtube.com/watch?v={link}"


async def api_download(link: str, media_type: str, timeout: int):
    """Railway API se media download karta hai."""

    full_url = youtube_full_url(link)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_URL}/download",
                params={
                    "url": full_url,
                    "type": media_type,
                    "api_key": API_KEY,
                },
                timeout=aiohttp.ClientTimeout(total=timeout),
            ) as resp:

                if resp.status != 200:
                    try:
                        error = await resp.text()
                    except Exception:
                        error = "Unknown API error"

                    print(
                        f"API ERROR {resp.status}: {error}"
                    )
                    return None

                os.makedirs(DOWNLOAD_DIR, exist_ok=True)

                content_type = resp.headers.get(
                    "Content-Type", ""
                ).lower()

                if media_type == "audio":
                    ext = "mp3"
                else:
                    ext = "mp4"

                video_id = link.split("v=")[-1].split("&")[0]

                if not video_id or len(video_id) < 3:
                    return None

                file_path = os.path.join(
                    DOWNLOAD_DIR,
                    f"{video_id}.{ext}"
                )

                with open(file_path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(131072):
                        f.write(chunk)

                if (
                    os.path.exists(file_path)
                    and os.path.getsize(file_path) > 0
                ):
                    return file_path

                return None

    except Exception as e:
        print(f"API DOWNLOAD ERROR: {e}")
        return None


async def download_song(link: str) -> str:
    full_url = youtube_full_url(link)

    video_id = (
        full_url.split("v=")[-1].split("&")[0]
        if "v=" in full_url
        else link
    )

    if not video_id or len(video_id) < 3:
        return None

    file_path = os.path.join(
        DOWNLOAD_DIR,
        f"{video_id}.mp3"
    )

    if (
        os.path.exists(file_path)
        and os.path.getsize(file_path) > 0
    ):
        return file_path

    return await api_download(
        full_url,
        "audio",
        300
    )


async def download_video(link: str) -> str:
    full_url = youtube_full_url(link)

    video_id = (
        full_url.split("v=")[-1].split("&")[0]
        if "v=" in full_url
        else link
    )

    if not video_id or len(video_id) < 3:
        return None

    file_path = os.path.join(
        DOWNLOAD_DIR,
        f"{video_id}.mp4"
    )

    if (
        os.path.exists(file_path)
        and os.path.getsize(file_path) > 0
    ):
        return file_path

    return await api_download(
        full_url,
        "video",
        600
    )


class YouTubeAPI:

    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(
            r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])"
        )

    async def exists(
        self,
        link: str,
        videoid: Union[bool, str] = None
    ):
        if videoid:
            link = self.base + link

        return bool(re.search(self.regex, link))

    async def url(
        self,
        message_1: Message
    ) -> Union[str, None]:

        messages = [message_1]

        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)

        for message in messages:

            if message.entities:

                for entity in message.entities:

                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption

                        return text[
                            entity.offset:
                            entity.offset + entity.length
                        ]

            elif message.caption_entities:

                for entity in message.caption_entities:

                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url

        return None

    async def details(
        self,
        link: str,
        videoid: Union[bool, str] = None
    ):

        if videoid:
            link = self.base + link

        if "&" in link:
            link = link.split("&")[0]

        results = VideosSearch(link, limit=1)

        for result in (
            await results.next()
        )["result"]:

            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            duration_sec = (
                int(time_to_seconds(duration_min))
                if duration_min
                else 0
            )

            return (
                title,
                duration_min,
                duration_sec,
                thumbnail,
                vidid
            )

    async def title(
        self,
        link: str,
        videoid: Union[bool, str] = None
    ):

        if videoid:
            link = self.base + link

        if "&" in link:
            link = link.split("&")[0]

        results = VideosSearch(link, limit=1)

        for result in (
            await results.next()
        )["result"]:
            return result["title"]

    async def duration(
        self,
        link: str,
        videoid: Union[bool, str] = None
    ):

        if videoid:
            link = self.base + link

        if "&" in link:
            link = link.split("&")[0]

        results = VideosSearch(link, limit=1)

        for result in (
            await results.next()
        )["result"]:
            return result["duration"]

    async def thumbnail(
        self,
        link: str,
        videoid: Union[bool, str] = None
    ):

        if videoid:
            link = self.base + link

        if "&" in link:
            link = link.split("&")[0]

        results = VideosSearch(link, limit=1)

        for result in (
            await results.next()
        )["result"]:
            return result["thumbnails"][0]["url"].split("?")[0]

    async def video(
        self,
        link: str,
        videoid: Union[bool, str] = None
    ):

        if videoid:
            link = self.base + link

        try:
            downloaded_file = await download_video(link)

            if downloaded_file:
                return 1, downloaded_file

            return 0, "Video download failed"

        except Exception as e:
            return 0, f"Video download error: {e}"

    async def playlist(
        self,
        link,
        limit,
        user_id,
        videoid: Union[bool, str] = None
    ):

        if videoid:
            link = self.listbase + link

        if "&" in link:
            link = link.split("&")[0]

        try:
            plist = await Playlist.get(link)
        except Exception:
            return []

        videos = plist.get("videos") or []
        ids = []

        for data in videos[:limit]:

            if not data:
                continue

            vid = data.get("id")

            if not vid:
                continue

            ids.append(vid)

        return ids

    async def track(
        self,
        link: str,
        videoid: Union[bool, str] = None
    ):

        if videoid:
            link = self.base + link

        if "&" in link:
            link = link.split("&")[0]

        results = VideosSearch(link, limit=1)

        for result in (
            await results.next()
        )["result"]:

            title = result["title"]
            duration_min = result["duration"]
            vidid = result["id"]
            yturl = result["link"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]

            track_details = {
                "title": title,
                "link": yturl,
                "vidid": vidid,
                "duration_min": duration_min,
                "thumb": thumbnail,
            }

            return track_details, vidid

    async def formats(
        self,
        link: str,
        videoid: Union[bool, str] = None
    ):

        if videoid:
            link = self.base + link

        if "&" in link:
            link = link.split("&")[0]

        ytdl_opts = {"quiet": True}

        ydl = yt_dlp.YoutubeDL(ytdl_opts)

        with ydl:

            formats_available = []

            r = ydl.extract_info(
                link,
                download=False
            )

            for format in r["formats"]:

                try:

                    if "dash" not in str(
                        format["format"]
                    ).lower():

                        formats_available.append({
                            "format": format["format"],
                            "filesize": format.get("filesize"),
                            "format_id": format["format_id"],
                            "ext": format["ext"],
                            "format_note": format["format_note"],
                            "yturl": link,
                        })

                except Exception:
                    continue

        return formats_available, link

    async def slider(
        self,
        link: str,
        query_type: int,
        videoid: Union[bool, str] = None
    ):

        if videoid:
            link = self.base + link

        if "&" in link:
            link = link.split("&")[0]

        a = VideosSearch(link, limit=10)

        result = (
            await a.next()
        ).get("result")

        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = (
            result[query_type]["thumbnails"][0]["url"]
            .split("?")[0]
        )

        return (
            title,
            duration_min,
            thumbnail,
            vidid
        )

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

        if videoid:
            link = self.base + link

        try:

            if video:
                downloaded_file = await download_video(link)
            else:
                downloaded_file = await download_song(link)

            if downloaded_file:
                return downloaded_file, True

            return None, False

        except Exception as e:

            print(f"Download error: {e}")
            return None, False


YouTube = YouTubeAPI()
