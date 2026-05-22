import asyncio
import glob
import json
import os
import random
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Union

import requests
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ShiviMusic import LOGGER
from ShiviMusic.utils.formatters import time_to_seconds
from config import YT_API_KEY, YTPROXY_URL as YTPROXY
from py_yt import VideosSearch

logger = LOGGER(__name__)


def cookie_txt_file():
    try:
        folder_path = f"{os.getcwd()}/cookies"
        filename = f"{os.getcwd()}/cookies/logs.csv"

        txt_files = glob.glob(os.path.join(folder_path, "*.txt"))

        if not txt_files:
            return None

        selected = random.choice(txt_files)

        with open(filename, "a") as file:
            file.write(f"Choosen File : {selected}\n")

        return f"cookies/{str(selected).split('/')[-1]}"

    except Exception as e:
        logger.error(f"Cookie Error: {e}")
        return None


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.listbase = "https://youtube.com/playlist?list="

    async def exists(self, link: str, videoid: Union[bool, str] = None):

        if videoid:
            link = self.base + link

        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message):

        messages = [message_1]

        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)

        text = ""
        offset = None
        length = None

        for message in messages:

            if offset:
                break

            if message.entities:
                for entity in message.entities:

                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        offset = entity.offset
                        length = entity.length
                        break

            elif message.caption_entities:
                for entity in message.caption_entities:

                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url

        if offset is None:
            return None

        return text[offset : offset + length]

    def clean_url(self, link):

        if "&" in link:
            link = link.split("&")[0]

        if "?si=" in link:
            link = link.split("?si=")[0]

        elif "&si=" in link:
            link = link.split("&si=")[0]

        return link

    async def details(self, link, videoid=None):

        if videoid:
            link = self.base + link

        link = self.clean_url(link)

        results = VideosSearch(link, limit=1)

        data = (await results.next())["result"][0]

        title = data["title"]
        duration_min = data.get("duration")
        thumbnail = data["thumbnails"][0]["url"].split("?")[0]
        vidid = data["id"]

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
            vidid,
        )

    async def title(self, link, videoid=None):

        if videoid:
            link = self.base + link

        link = self.clean_url(link)

        results = VideosSearch(link, limit=1)

        data = (await results.next())["result"][0]

        return data["title"]

    async def duration(self, link, videoid=None):

        if videoid:
            link = self.base + link

        link = self.clean_url(link)

        results = VideosSearch(link, limit=1)

        data = (await results.next())["result"][0]

        return data.get("duration")

    async def thumbnail(self, link, videoid=None):

        if videoid:
            link = self.base + link

        link = self.clean_url(link)

        results = VideosSearch(link, limit=1)

        data = (await results.next())["result"][0]

        return data["thumbnails"][0]["url"].split("?")[0]

    async def track(self, link, videoid=None):

        if videoid:
            link = self.base + link

        link = self.clean_url(link)

        results = VideosSearch(link, limit=1)

        data = (await results.next())["result"][0]

        track_details = {
            "title": data["title"],
            "link": data["link"],
            "vidid": data["id"],
            "duration_min": data.get("duration"),
            "thumb": data["thumbnails"][0]["url"].split("?")[0],
        }

        return track_details, data["id"]

    async def video(self, link, videoid=None):

        if videoid:
            link = self.base + link

        link = self.clean_url(link)

        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "-g",
            "-f",
            "best[height<=720][width<=1280]",
            link,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await proc.communicate()

        if stdout:
            return 1, stdout.decode().split("\n")[0]

        return 0, stderr.decode()

    async def formats(self, link, videoid=None):

        if videoid:
            link = self.base + link

        link = self.clean_url(link)

        ytdl_opts = {
            "quiet": True,
            "nocheckcertificate": True,
        }

        formats_available = []

        try:

            with yt_dlp.YoutubeDL(ytdl_opts) as ydl:

                data = ydl.extract_info(
                    link,
                    download=False
                )

                for fmt in data["formats"]:

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
                                "format_note": fmt.get("format_note"),
                                "yturl": link,
                            }
                        )

                    except Exception:
                        continue

        except Exception as e:
            logger.error(f"Formats Error: {e}")

        return formats_available, link

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

        vid_id = None

        if videoid:
            vid_id = link
            link = self.base + link

        else:
            match = re.search(
                r"(?:v=|\/)([0-9A-Za-z_-]{11})",
                link,
            )

            if match:
                vid_id = match.group(1)

        if not vid_id:
            logger.error("Invalid YouTube URL")
            return None

        link = self.clean_url(link)

        os.makedirs("downloads", exist_ok=True)

        loop = asyncio.get_running_loop()

        def create_session():

            session = requests.Session()

            retries = Retry(
                total=5,
                backoff_factor=1,
                status_forcelist=[500, 502, 503, 504],
            )

            adapter = HTTPAdapter(max_retries=retries)

            session.mount("http://", adapter)
            session.mount("https://", adapter)

            return session

        async def download_file(url, filepath, headers=None):

            try:

                session = create_session()

                response = session.get(
                    url,
                    headers=headers,
                    stream=True,
                    timeout=120,
                    allow_redirects=True,
                )

                response.raise_for_status()

                with open(filepath, "wb") as f:

                    for chunk in response.iter_content(
                        chunk_size=1024 * 1024
                    ):

                        if chunk:
                            f.write(chunk)

                session.close()

                if os.path.exists(filepath):
                    return filepath

                return None

            except Exception as e:

                logger.error(f"Download Error: {e}")

                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                except:
                    pass

                return None

        async def ytdlp_fallback(
            is_video=False,
            custom_path=None,
        ):

            try:

                cookie_file = cookie_txt_file()

                if is_video:

                    filepath = (
                        custom_path
                        or f"downloads/{vid_id}.mp4"
                    )

                    ydl_opts = {
                        "format": (
                            f"{format_id}+bestaudio/best"
                            if format_id
                            else "best[height<=720]"
                        ),
                        "outtmpl": filepath,
                        "quiet": True,
                        "geo_bypass": True,
                        "nocheckcertificate": True,
                        "cookiefile": cookie_file,
                        "noplaylist": True,
                    }

                else:

                    filepath = (
                        custom_path
                        or f"downloads/{vid_id}.mp3"
                    )

                    ydl_opts = {
                        "format": "bestaudio/best",
                        "outtmpl": filepath,
                        "quiet": True,
                        "geo_bypass": True,
                        "nocheckcertificate": True,
                        "cookiefile": cookie_file,
                        "noplaylist": True,
                        "postprocessors": [
                            {
                                "key": "FFmpegExtractAudio",
                                "preferredcodec": "mp3",
                                "preferredquality": "192",
                            }
                        ],
                    }

                def run():

                    with yt_dlp.YoutubeDL(
                        ydl_opts
                    ) as ydl:

                        ydl.download([link])

                await loop.run_in_executor(
                    ThreadPoolExecutor(),
                    run,
                )

                if os.path.exists(filepath):
                    return filepath

                return None

            except Exception as e:
                logger.error(f"Fallback Error: {e}")
                return None

        async def proxy_download(is_video=False):

            try:

                headers = {
                    "x-api-key": str(YT_API_KEY),
                    "User-Agent": "Mozilla/5.0",
                }

                session = create_session()

                response = session.get(
                    f"{YTPROXY}/info/{vid_id}",
                    headers=headers,
                    timeout=60,
                )

                data = response.json()

                session.close()

                if data.get("status") != "success":
                    return None

                media_url = (
                    data.get("video_url")
                    if is_video
                    else data.get("audio_url")
                )

                if not media_url:
                    return None

                filepath = (
                    f"downloads/{vid_id}.mp4"
                    if is_video
                    else f"downloads/{vid_id}.mp3"
                )

                downloaded = await download_file(
                    media_url,
                    filepath,
                    headers,
                )

                return downloaded

            except Exception as e:
                logger.error(f"Proxy Error: {e}")
                return None

        async def audio_dl():

            filepath = f"downloads/{vid_id}.mp3"

            if os.path.exists(filepath):
                return filepath

            file = await proxy_download(False)

            if file:
                return file

            return await ytdlp_fallback(False)

        async def video_dl():

            filepath = f"downloads/{vid_id}.mp4"

            if os.path.exists(filepath):
                return filepath

            file = await proxy_download(True)

            if file:
                return file

            return await ytdlp_fallback(True)

        async def song_video_dl():

            safe_title = "".join(
                x
                for x in str(title)
                if x.isalnum()
                or x in (" ", "_", "-")
            ).rstrip()

            filepath = (
                f"downloads/{safe_title}.mp4"
            )

            if os.path.exists(filepath):
                return filepath

            file = await proxy_download(True)

            if file:
                try:
                    os.rename(
                        file,
                        filepath,
                    )
                except:
                    pass

                return filepath

            return await ytdlp_fallback(
                True,
                filepath,
            )

        try:

            if songaudio:
                return await audio_dl()

            elif songvideo:
                return await song_video_dl()

            elif video:
                return await video_dl()

            return None

        except Exception as e:
            logger.error(f"Main Download Error: {e}")
            return None
