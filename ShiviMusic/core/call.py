# -----------------------------------------------
# ShiviMusic - fixed call.py
# Fixes:
# - None/empty media_path TypeError
# - invalid YouTube download response
# - queue None protection
# - skip -> next track
# - queue empty -> autoplay
# - safer Telegram/PyTgCalls retries
# -----------------------------------------------

import asyncio
import os
from datetime import datetime, timedelta
from typing import Union

from ntgcalls import ConnectionNotFound, TelegramServerError
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup
from pytgcalls import PyTgCalls, exceptions, types
from pytgcalls.pytgcalls_session import PyTgCallsSession

import config

from ShiviMusic import LOGGER, YouTube, app
from ShiviMusic.misc import db

from ShiviMusic.utils.database import (
    add_active_chat,
    add_active_video_chat,
    get_lang,
    get_loop,
    group_assistant,
    is_autoend,
    is_autoplay_on,
    music_on,
    remove_active_chat,
    remove_active_video_chat,
    set_loop,
)

from ShiviMusic.utils.autoplay import (
    fetch_autoplay_track,
    remember_played,
)

from ShiviMusic.utils.exceptions import AssistantErr
from ShiviMusic.utils.formatters import (
    check_duration,
    seconds_to_min,
    speed_converter,
)
from ShiviMusic.utils.inline.play import stream_markup
from ShiviMusic.utils.stream.autoclear import auto_clean
from ShiviMusic.utils.stream.queue import put_queue
from ShiviMusic.utils.thumbnails import get_thumb as gen_thumb

from strings import get_string


autoend = {}
counter = {}


def _safe_str(value, default=""):
    if value is None:
        return default
    try:
        value = str(value).strip()
    except Exception:
        return default
    return value or default


def _valid_source(source):
    source = _safe_str(source)
    if not source:
        return None

    is_url = source.lower().startswith(
        ("http://", "https://", "rtmp://", "rtmps://")
    )

    if not is_url:
        if not os.path.exists(source):
            return None
        if os.path.isdir(source):
            return None
        try:
            if os.path.getsize(source) <= 0:
                return None
        except OSError:
            return None

    return source


async def _clear_(chat_id: int):
    try:
        for item in list(db.get(chat_id, [])):
            try:
                msg = item.get("mystic")
                if msg:
                    await msg.delete()
            except Exception:
                pass
    except Exception:
        pass

    try:
        db[chat_id] = []
    except Exception:
        pass

    try:
        await remove_active_video_chat(chat_id)
    except Exception:
        pass

    try:
        await remove_active_chat(chat_id)
    except Exception:
        pass


class Call(PyTgCalls):

    def __init__(self):
        PyTgCallsSession.notice_displayed = True

        self.userbot1 = Client(
            name="ShiviAss1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
        )
        self.one = PyTgCalls(self.userbot1, cache_duration=100)

        self.userbot2 = Client(
            name="ShiviAss2",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING2),
        )
        self.two = PyTgCalls(self.userbot2, cache_duration=100)

        self.userbot3 = Client(
            name="ShiviAss3",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING3),
        )
        self.three = PyTgCalls(self.userbot3, cache_duration=100)

        self.userbot4 = Client(
            name="ShiviAss4",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING4),
        )
        self.four = PyTgCalls(self.userbot4, cache_duration=100)

        self.userbot5 = Client(
            name="ShiviAss5",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING5),
        )
        self.five = PyTgCalls(self.userbot5, cache_duration=100)

    # -----------------------------------------------------
    # STREAM BUILDER
    # -----------------------------------------------------

    def _build_stream(self, source, video=False, ffmpeg=None):
        source = _valid_source(source)

        if not source:
            raise AssistantErr("Media source is empty or invalid.")

        try:
            if video:
                return types.MediaStream(
                    media_path=source,
                    audio_parameters=types.AudioQuality.HIGH,
                    video_parameters=types.VideoQuality.HD_720p,
                    audio_flags=types.MediaStream.Flags.REQUIRED,
                    video_flags=types.MediaStream.Flags.AUTO_DETECT,
                    ffmpeg_parameters=ffmpeg,
                )

            return types.MediaStream(
                media_path=source,
                audio_parameters=types.AudioQuality.HIGH,
                video_parameters=types.VideoQuality.HD_720p,
                audio_flags=types.MediaStream.Flags.REQUIRED,
                video_flags=types.MediaStream.Flags.IGNORE,
                ffmpeg_parameters=ffmpeg,
            )

        except TypeError as e:
            LOGGER(__name__).error(
                "MediaStream TypeError: source=%r video=%r ffmpeg=%r error=%s",
                source, video, ffmpeg, e,
            )
            raise AssistantErr(
                "Media stream configuration is incompatible with the installed PyTgCalls."
            )
        except Exception as e:
            LOGGER(__name__).error(
                "MediaStream build failed: %s", e
            )
            raise AssistantErr("Unable to create media stream.")

    # -----------------------------------------------------
    # PLAY WITH RETRY
    # -----------------------------------------------------

    async def _play_on_assistant(
        self,
        client: PyTgCalls,
        chat_id: int,
        stream: types.MediaStream,
        retries: int = 3,
    ):
        if stream is None:
            raise AssistantErr("Stream is empty.")

        last_error = None

        for attempt in range(1, retries + 1):
            try:
                await client.play(
                    chat_id=chat_id,
                    stream=stream,
                    config=types.GroupCallConfig(auto_start=False),
                )
                return True

            except (
                exceptions.NoActiveGroupCall,
                exceptions.NoAudioSourceFound,
            ):
                raise

            except (
                ConnectionNotFound,
                TelegramServerError,
                asyncio.TimeoutError,
            ) as e:
                last_error = e
                LOGGER(__name__).warning(
                    "Voice server error %s/%s in %s: %s",
                    attempt, retries, chat_id, e,
                )
                if attempt < retries:
                    await asyncio.sleep(1.5 * attempt)
                    continue
                raise

            except Exception:
                raise

        if last_error:
            raise last_error

        return False

    # -----------------------------------------------------
    # PAUSE / RESUME
    # -----------------------------------------------------

    async def pause_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            await assistant.pause(chat_id)
        except (ConnectionNotFound, TelegramServerError) as e:
            raise AssistantErr(
                "Telegram voice server is temporarily unavailable."
            ) from e

    async def resume_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            await assistant.resume(chat_id)
        except (ConnectionNotFound, TelegramServerError) as e:
            raise AssistantErr(
                "Telegram voice server is temporarily unavailable."
            ) from e

    # -----------------------------------------------------
    # STOP
    # -----------------------------------------------------

    async def stop_stream(self, chat_id: int):
        try:
            assistant = await group_assistant(self, chat_id)
        except Exception:
            assistant = None

        await _clear_(chat_id)

        if assistant:
            try:
                await assistant.leave_call(chat_id, close=False)
            except Exception:
                pass

    async def stop_stream_force(self, chat_id: int):
        for string, client in [
            (config.STRING1, self.one),
            (config.STRING2, self.two),
            (config.STRING3, self.three),
            (config.STRING4, self.four),
            (config.STRING5, self.five),
        ]:
            if not string:
                continue
            try:
                await client.leave_call(chat_id, close=False)
            except Exception:
                pass

        await _clear_(chat_id)

    # -----------------------------------------------------
    # SPEED
    # -----------------------------------------------------

    async def speedup_stream(self, chat_id, file_path, speed, playing):
        assistant = await group_assistant(self, chat_id)

        file_path = _valid_source(file_path)
        if not file_path:
            raise AssistantErr("Media file is empty or missing.")

        speed = _safe_str(speed, "1.0")

        if speed != "1.0":
            base = os.path.basename(file_path)
            chatdir = os.path.join(os.getcwd(), "playback", speed)
            os.makedirs(chatdir, exist_ok=True)
            out = os.path.join(chatdir, base)

            if not os.path.isfile(out):
                vs_map = {
                    "0.5": 2.0,
                    "0.75": 1.35,
                    "1.5": 0.68,
                    "2.0": 0.5,
                }
                vs = vs_map.get(speed, 1.0)

                proc = await asyncio.create_subprocess_exec(
                    "ffmpeg", "-y", "-i", file_path,
                    "-filter:v", f"setpts={vs}*PTS",
                    "-filter:a", f"atempo={speed}",
                    out,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.PIPE,
                )
                await proc.communicate()

                if proc.returncode != 0:
                    raise AssistantErr("Unable to change playback speed.")
        else:
            out = file_path

        out = _valid_source(out) or _valid_source(file_path)
        if not out:
            raise AssistantErr("Speed-adjusted media file not found.")

        dur = await asyncio.get_running_loop().run_in_executor(
            None, check_duration, out
        )
        if str(dur) == "Unknown":
            dur = 0
        dur = int(dur)

        played, con_seconds = speed_converter(
            playing[0].get("played", 0), speed
        )
        duration = seconds_to_min(dur)
        ffmpeg = f"-ss {played} -to {duration}"

        video_mode = playing[0].get("streamtype") == "video"
        stream = self._build_stream(out, video=video_mode, ffmpeg=ffmpeg)

        if not db.get(chat_id):
            raise AssistantErr("Playback state changed.")

        if str(db[chat_id][0].get("file")) != str(file_path):
            raise AssistantErr("Playback state changed.")

        await self._play_on_assistant(assistant, chat_id, stream)

        if db.get(chat_id):
            item = db[chat_id][0]
            if not item.get("old_dur"):
                item["old_dur"] = item.get("dur")
                item["old_second"] = item.get("seconds", 0)

            item["played"] = con_seconds
            item["dur"] = duration
            item["seconds"] = dur
            item["speed_path"] = out
            item["speed"] = speed

    # -----------------------------------------------------
    # FILTER
    # -----------------------------------------------------

    async def apply_filter(self, chat_id, file_path, filter_type, playing):
        assistant = await group_assistant(self, chat_id)

        file_path = _valid_source(file_path)
        if not file_path:
            raise AssistantErr("Media file is missing.")

        base = os.path.basename(file_path)
        chatdir = os.path.join(os.getcwd(), "filters", str(filter_type))
        os.makedirs(chatdir, exist_ok=True)
        out = os.path.join(chatdir, base)

        if filter_type == "normal":
            out = file_path
        elif not os.path.isfile(out):
            filters = {
                "bass": "bass=g=20,firequalizer=gain_entry='entry(0,0);entry(250,0);entry(4000,0);entry(16000,0)'",
                "echo": "aecho=0.8:0.88:60:0.4",
                "slowed": "atempo=0.8,aecho=0.8:0.88:60:0.4",
                "nightcore": "asetrate=48000*1.25,atempo=1.25",
            }
            ff_filter = filters.get(filter_type)

            if not ff_filter:
                out = file_path
            else:
                proc = await asyncio.create_subprocess_exec(
                    "ffmpeg", "-y", "-i", file_path,
                    "-filter:a", ff_filter, out,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.PIPE,
                )
                await proc.communicate()
                if proc.returncode != 0 or not os.path.isfile(out):
                    out = file_path

        dur = await asyncio.get_running_loop().run_in_executor(
            None, check_duration, out
        )
        if str(dur) == "Unknown":
            dur = 0
        dur = int(dur)

        played = playing[0].get("played", 0)
        duration = seconds_to_min(dur)
        ffmpeg = f"-ss {played} -to {duration}"
        video_mode = playing[0].get("streamtype") == "video"

        stream = self._build_stream(
            out, video=video_mode, ffmpeg=ffmpeg
        )

        if not db.get(chat_id):
            raise AssistantErr("Stream changed.")

        if str(db[chat_id][0].get("file")) != str(file_path):
            raise AssistantErr("Stream changed.")

        await self._play_on_assistant(assistant, chat_id, stream)

        if db.get(chat_id):
            db[chat_id][0]["played"] = played
            db[chat_id][0]["dur"] = duration
            db[chat_id][0]["seconds"] = dur

    # -----------------------------------------------------
    # FORCE STOP CURRENT
    # -----------------------------------------------------

    async def force_stop_stream(self, chat_id: int):
        try:
            check = db.get(chat_id)
            if check:
                popped = check.pop(0)
                if popped:
                    try:
                        await auto_clean(popped)
                    except Exception:
                        pass
        except Exception:
            pass

        try:
            await remove_active_video_chat(chat_id)
        except Exception:
            pass
        try:
            await remove_active_chat(chat_id)
        except Exception:
            pass

        try:
            assistant = await group_assistant(self, chat_id)
            await assistant.leave_call(chat_id, close=False)
        except Exception:
            pass

    # -----------------------------------------------------
    # SKIP
    # -----------------------------------------------------

    async def skip_stream(
        self,
        chat_id: int,
        link: str,
        video: Union[bool, str] = None,
        image: Union[bool, str] = None,
    ):
        link = _valid_source(link)
        if not link:
            raise AssistantErr("Next media source is empty.")

        assistant = await group_assistant(self, chat_id)
        stream = self._build_stream(link, video=bool(video))

        await self._play_on_assistant(
            assistant, chat_id, stream, retries=3
        )

    # -----------------------------------------------------
    # SEEK
    # -----------------------------------------------------

    async def seek_stream(
        self, chat_id, file_path, to_seek, duration, mode
    ):
        assistant = await group_assistant(self, chat_id)

        ffmpeg = f"-ss {to_seek} -to {duration}"
        stream = self._build_stream(
            file_path,
            video=(mode == "video"),
            ffmpeg=ffmpeg,
        )

        await self._play_on_assistant(
            assistant, chat_id, stream
        )

    # -----------------------------------------------------
    # AUTOPLAY
    # -----------------------------------------------------

    async def autoplay_start(
        self,
        chat_id: int,
        original_chat_id: int,
        seed_title: str,
        seed_vidid: str = None,
        client: PyTgCalls = None,
    ) -> bool:

        seed_title = _safe_str(seed_title, "Music")
        seed_vidid = _safe_str(seed_vidid)

        if seed_vidid:
            try:
                remember_played(chat_id, seed_vidid)
            except Exception:
                pass

        status_msg = None

        try:
            status_msg = await app.send_message(
                original_chat_id,
                "ʜσʟᴅ ση...\n\nᴅσᴡηʟσᴧᴅɪηɢ ηєxᴛ ϻєᴅɪᴧ...",
            )
        except Exception:
            pass

        async def fail():
            if status_msg:
                try:
                    await status_msg.delete()
                except Exception:
                    pass
            return False

        try:
            track = await fetch_autoplay_track(
                chat_id, seed_title, seed_vidid
            )
        except Exception as e:
            LOGGER(__name__).error(
                "Autoplay search failed in %s: %s",
                chat_id, e
            )
            return await fail()

        if not track or not isinstance(track, dict):
            return await fail()

        vidid = _safe_str(track.get("vidid"))
        title = _safe_str(track.get("title"), "Unknown")
        duration_min = _safe_str(
            track.get("duration_min"), "00:00"
        )

        if not vidid:
            return await fail()

        # Download API must return (file, direct)
        try:
            result = await YouTube.download(
                vidid,
                None,
                videoid=True,
            )
        except Exception as e:
            LOGGER(__name__).error(
                "Autoplay download failed in %s: %s",
                chat_id, e
            )
            return await fail()

        if not isinstance(result, (tuple, list)) or len(result) < 2:
            LOGGER(__name__).error(
                "Invalid autoplay download response: %r",
                result
            )
            return await fail()

        file_path, direct = result
        file_path = _safe_str(file_path)

        if not file_path:
            return await fail()

        # Keep the original file if API returns a local file.
        if not direct and not file_path.startswith(("http://", "https://")):
            if not os.path.isfile(file_path):
                return await fail()

        try:
            remember_played(chat_id, vidid)
        except Exception:
            pass

        try:
            await put_queue(
                chat_id,
                original_chat_id,
                file_path if direct else f"vid_{vidid}",
                title,
                duration_min,
                "🔁 𝐀ᴜᴛᴏᴘʟᴀʏ",
                vidid,
                1,
                "audio",
                forceplay=True,
            )
        except Exception as e:
            LOGGER(__name__).error(
                "Autoplay queue failed in %s: %s",
                chat_id, e
            )
            return await fail()

        check = db.get(chat_id)
        if not check:
            return await fail()

        item = check[0]
        item["played"] = 0
        item["seconds"] = 0
        item["speed"] = 1.0
        item["speed_path"] = None
        item["old_dur"] = None
        item["old_second"] = 0

        assistant = client
        if assistant is None:
            assistant = await group_assistant(self, chat_id)

        # If queue uses vid_<id>, download now for immediate autoplay.
        if not direct:
            try:
                result = await YouTube.download(
                    vidid,
                    None,
                    videoid=True,
                )
                if not isinstance(result, (tuple, list)) or not result:
                    return await fail()
                file_path = _safe_str(result[0])
                if not file_path:
                    return await fail()
            except Exception as e:
                LOGGER(__name__).error(
                    "Autoplay second download failed: %s", e
                )
                return await fail()

        stream = self._build_stream(
            file_path,
            video=False,
        )

        try:
            await self._play_on_assistant(
                assistant, chat_id, stream, retries=3
            )
        except (
            ConnectionNotFound,
            TelegramServerError,
        ) as e:
            LOGGER(__name__).warning(
                "Autoplay Telegram error in %s: %s",
                chat_id, e
            )
            return await fail()
        except Exception as e:
            LOGGER(__name__).error(
                "Autoplay playback failed in %s: %s",
                chat_id, e
            )
            return await fail()

        item = db.get(chat_id, [None])[0]
        if item:
            item["file"] = file_path
            item["played"] = 0
            item["seconds"] = 0
            item["speed"] = 1.0
            item["speed_path"] = None

        # Now-playing message
        try:
            language = await get_lang(chat_id)
            strings = get_string(language)

            img = await gen_thumb(vidid)
            button = stream_markup(strings, chat_id)

            run = await app.send_photo(
                chat_id=original_chat_id,
                photo=img,
                caption=strings["stream_1"].format(
                    f"https://t.me/{app.username}?start=info_{vidid}",
                    title[:23],
                    duration_min,
                    "𝐀ᴜᴛᴏᴘʟᴀʏ 🚩",
                    " 🎵 Aᴜᴅɪᴏ",
                ),
                reply_markup=InlineKeyboardMarkup(button),
            )

            if db.get(chat_id):
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "stream"
        except Exception as e:
            LOGGER(__name__).warning(
                "Autoplay message failed: %s", e
            )

        if status_msg:
            try:
                await status_msg.delete()
            except Exception:
                pass

        try:
            await add_active_chat(chat_id)
        except Exception:
            pass

        try:
            await music_on(chat_id)
        except Exception:
            pass

        return True

    # -----------------------------------------------------
    # STREAM CALL
    # -----------------------------------------------------

    async def stream_call(self, link):
        link = _valid_source(link)
        if not link:
            raise AssistantErr("Media source is empty.")

        assistant = await group_assistant(
            self, config.LOG_GROUP_ID
        )

        stream = self._build_stream(link, video=True)

        await self._play_on_assistant(
            assistant, config.LOG_GROUP_ID, stream
        )

        await asyncio.sleep(0.2)

        try:
            await assistant.leave_call(
                config.LOG_GROUP_ID, close=False
            )
        except Exception:
            pass

    # -----------------------------------------------------
    # JOIN CALL
    # -----------------------------------------------------

    async def join_call(
        self,
        chat_id: int,
        original_chat_id: int,
        link,
        video: Union[bool, str] = None,
        image: Union[bool, str] = None,
    ):
        link = _valid_source(link)
        if not link:
            raise AssistantErr("Media source is empty.")

        assistant = await group_assistant(self, chat_id)

        language = await get_lang(chat_id)
        strings = get_string(language)

        stream = self._build_stream(
            link, video=bool(video)
        )

        try:
            await self._play_on_assistant(
                assistant, chat_id, stream
            )
        except exceptions.NoActiveGroupCall:
            raise AssistantErr(strings["call_8"])
        except exceptions.NoAudioSourceFound:
            raise AssistantErr(strings["call_10"])
        except (
            ConnectionNotFound,
            TelegramServerError,
        ):
            raise AssistantErr(
                "Telegram voice server is temporarily unavailable."
            )
        except Exception as e:
            LOGGER(__name__).error(
                "join_call failed in %s: %s",
                chat_id, e
            )
            raise AssistantErr(strings["call_10"])

        await add_active_chat(chat_id)
        await music_on(chat_id)

        if video:
            await add_active_video_chat(chat_id)

        if await is_autoend():
            counter[chat_id] = {}
            try:
                users = len(
                    await assistant.get_participants(chat_id)
                )
                if users == 1:
                    autoend[chat_id] = (
                        datetime.now() + timedelta(minutes=1)
                    )
            except Exception:
                pass

    # -----------------------------------------------------
    # CHANGE STREAM / QUEUE / AUTOPLAY
    # -----------------------------------------------------

    async def change_stream(
        self,
        client: PyTgCalls,
        chat_id: int,
    ):
        check = db.get(chat_id)

        if not check:
            try:
                await client.leave_call(
                    chat_id, close=False
                )
            except Exception:
                pass
            return

        popped = None

        try:
            loop = await get_loop(chat_id)

            if loop == 0:
                if check:
                    popped = check.pop(0)
            else:
                loop = max(0, loop - 1)
                await set_loop(chat_id, loop)

            if popped:
                try:
                    await auto_clean(popped)
                except Exception:
                    pass

            # Queue is empty -> autoplay
            if not check:
                autoplay = False
                try:
                    autoplay = await is_autoplay_on(chat_id)
                except Exception:
                    autoplay = False

                if autoplay and popped:
                    seed_vidid = _safe_str(
                        popped.get("vidid")
                    )
                    seed_title = _safe_str(
                        popped.get("title"), "Music"
                    )
                    original_chat_id = popped.get(
                        "chat_id", chat_id
                    )

                    if seed_vidid:
                        try:
                            started = await self.autoplay_start(
                                chat_id,
                                original_chat_id,
                                seed_title,
                                seed_vidid,
                                client=client,
                            )
                            if started:
                                return
                        except Exception as e:
                            LOGGER(__name__).error(
                                "Autoplay error in %s: %s",
                                chat_id, e
                            )

                await _clear_(chat_id)

                try:
                    await client.leave_call(
                        chat_id, close=False
                    )
                except Exception:
                    pass
                return

        except (
            ConnectionNotFound,
            TelegramServerError,
        ) as e:
            LOGGER(__name__).warning(
                "Telegram server error in change_stream %s: %s",
                chat_id, e
            )
            await asyncio.sleep(2)

            # Retry only if a queue still exists.
            if db.get(chat_id):
                try:
                    await self.change_stream(
                        client, chat_id
                    )
                except Exception as retry_error:
                    LOGGER(__name__).error(
                        "change_stream retry failed: %s",
                        retry_error
                    )
            return

        except Exception as e:
            LOGGER(__name__).error(
                "change_stream queue error in %s: %s",
                chat_id, e
            )
            return

        check = db.get(chat_id)
        if not check:
            return

        queued = _safe_str(
            check[0].get("file")
        )

        if not queued:
            LOGGER(__name__).error(
                "Empty/None queued media in %s",
                chat_id
            )
            try:
                check.pop(0)
            except Exception:
                pass
            return

        language = await get_lang(chat_id)
        strings = get_string(language)

        title = _safe_str(
            check[0].get("title"), "Unknown"
        )
        user = _safe_str(
            check[0].get("by"), "Unknown"
        )
        original_chat_id = check[0].get(
            "chat_id", chat_id
        )
        streamtype = _safe_str(
            check[0].get("streamtype"), "audio"
        )
        videoid = _safe_str(
            check[0].get("vidid")
        )

        check[0]["played"] = 0

        video = streamtype.lower() == "video"

        # Delete queue/status message safely.
        try:
            old_msg = check[0].get("mystic")
            if old_msg:
                await old_msg.delete()
        except Exception:
            pass

        # -------------------------------------------------
        # LIVE
        # -------------------------------------------------
        if "live_" in queued:
            try:
                result = await YouTube.video(
                    videoid, True
                )
                if not result:
                    raise AssistantErr(strings["call_6"])

                n, link = result

                if n == 0 or not link:
                    raise AssistantErr(strings["call_6"])

                stream = self._build_stream(
                    link, video=video
                )
                await self._play_on_assistant(
                    client, chat_id, stream
                )

                if db.get(chat_id):
                    db[chat_id][0]["file"] = link

            except Exception as e:
                LOGGER(__name__).error(
                    "Live playback failed: %s", e
                )
                try:
                    await app.send_message(
                        original_chat_id,
                        strings["call_6"]
                    )
                except Exception:
                    pass
                return

        # -------------------------------------------------
        # YOUTUBE
        # -------------------------------------------------
        elif "vid_" in queued:
            status = None

            try:
                status = await app.send_message(
                    original_chat_id,
                    strings["call_7"]
                )
            except Exception:
                pass

            try:
                result = await YouTube.download(
                    videoid,
                    status,
                    videoid=True,
                    video=video,
                )

                if (
                    not isinstance(result, (tuple, list))
                    or len(result) < 2
                ):
                    raise AssistantErr(
                        "Invalid YouTube download response."
                    )

                file_path, direct = result
                file_path = _safe_str(file_path)

                if not file_path:
                    raise AssistantErr(
                        "YouTube returned empty media source."
                    )

                if (
                    not direct
                    and not file_path.startswith(
                        ("http://", "https://")
                    )
                    and not os.path.isfile(file_path)
                ):
                    raise AssistantErr(
                        "Downloaded media file was not found."
                    )

                stream = self._build_stream(
                    file_path, video=video
                )
                await self._play_on_assistant(
                    client, chat_id, stream
                )

                if db.get(chat_id):
                    db[chat_id][0]["file"] = file_path

                if status:
                    try:
                        await status.delete()
                    except Exception:
                        pass

            except Exception as e:
                LOGGER(__name__).error(
                    "YouTube playback failed in %s: %s",
                    chat_id, e
                )
                if status:
                    try:
                        await status.edit_text(
                            strings["call_6"]
                        )
                    except Exception:
                        pass
                return

        # -------------------------------------------------
        # TELEGRAM INDEX
        # -------------------------------------------------
        elif "index_" in queued:
            try:
                stream = self._build_stream(
                    videoid, video=video
                )
                await self._play_on_assistant(
                    client, chat_id, stream
                )

                if db.get(chat_id):
                    db[chat_id][0]["file"] = videoid

            except Exception as e:
                LOGGER(__name__).error(
                    "Index playback failed: %s", e
                )
                return

        # -------------------------------------------------
        # NORMAL LOCAL/URL
        # -------------------------------------------------
        else:
            try:
                stream = self._build_stream(
                    queued, video=video
                )
                await self._play_on_assistant(
                    client, chat_id, stream
                )

            except Exception as e:
                LOGGER(__name__).error(
                    "Normal playback failed: %s", e
                )
                try:
                    await app.send_message(
                        original_chat_id,
                        strings["call_6"]
                    )
                except Exception:
                    pass
                return

        # -------------------------------------------------
        # NOW PLAYING UI
        # -------------------------------------------------
        if not db.get(chat_id):
            return

        try:
            button = stream_markup(
                strings, chat_id
            )

            if videoid == "telegram":
                photo = config.TELEGRAM_VIDEO_URL if video else config.TELEGRAM_AUDIO_URL
            elif videoid == "soundcloud":
                photo = config.SOUNDCLOUD_IMG_URL
            else:
                photo = await gen_thumb(videoid)

            caption = strings["stream_1"].format(
                (
                    f"https://t.me/{app.username}"
                    f"?start=info_{videoid}"
                    if videoid
                    else config.SUPPORT_GROUP
                ),
                title[:23],
                check[0].get("dur", "00:00"),
                user,
                "🎵 Video" if video else "🎵 Audio",
            )

            run = await app.send_photo(
                chat_id=original_chat_id,
                photo=photo,
                caption=caption,
                reply_markup=InlineKeyboardMarkup(button),
            )

            if db.get(chat_id):
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "stream"

        except Exception as e:
            LOGGER(__name__).warning(
                "Now-playing UI failed: %s", e
            )

    # -----------------------------------------------------
    # PING
    # -----------------------------------------------------

    async def ping(self):
        values = []

        for string, client in [
            (config.STRING1, self.one),
            (config.STRING2, self.two),
            (config.STRING3, self.three),
            (config.STRING4, self.four),
            (config.STRING5, self.five),
        ]:
            if not string:
                continue
            try:
                value = client.ping
                if callable(value):
                    value = value()
                    if asyncio.iscoroutine(value):
                        value = await value
                values.append(float(value))
            except Exception:
                pass

        if not values:
            return "0"

        return str(round(sum(values) / len(values), 3))

    # -----------------------------------------------------
    # START
    # -----------------------------------------------------

    async def start(self):
        LOGGER(__name__).info(
            "Starting PyTgCalls Clients..."
        )

        for number, string, client in [
            (1, config.STRING1, self.one),
            (2, config.STRING2, self.two),
            (3, config.STRING3, self.three),
            (4, config.STRING4, self.four),
            (5, config.STRING5, self.five),
        ]:
            if not string:
                continue

            try:
                await client.start()
                LOGGER(__name__).info(
                    "Assistant %s started.", number
                )
            except Exception as e:
                LOGGER(__name__).error(
                    "Assistant %s failed: %s",
                    number, e
                )

    # -----------------------------------------------------
    # UPDATE HANDLERS
    # -----------------------------------------------------

    async def decorators(self):
        for string, client in [
            (config.STRING1, self.one),
            (config.STRING2, self.two),
            (config.STRING3, self.three),
            (config.STRING4, self.four),
            (config.STRING5, self.five),
        ]:
            if not string:
                continue

            @client.on_update()
            async def _update_handler(
                _,
                update: types.Update,
                _client=client,
            ):
                try:
                    if isinstance(
                        update, types.StreamEnded
                    ):
                        if (
                            update.stream_type
                            == types.StreamEnded.Type.AUDIO
                        ):
                            await self.change_stream(
                                _client,
                                update.chat_id,
                            )

                    elif isinstance(
                        update, types.ChatUpdate
                    ):
                        if update.status in [
                            types.ChatUpdate.Status.KICKED,
                            types.ChatUpdate.Status.LEFT_GROUP,
                            types.ChatUpdate.Status.CLOSED_VOICE_CHAT,
                        ]:
                            await self.stop_stream(
                                update.chat_id
                            )

                except (
                    ConnectionNotFound,
                    TelegramServerError,
                ) as e:
                    LOGGER(__name__).warning(
                        "Telegram update error: %s", e
                    )

                except Exception as e:
                    LOGGER(__name__).error(
                        "Update handler error: %s", e
                    )


Shivi = Call()
