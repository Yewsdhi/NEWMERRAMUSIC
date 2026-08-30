# -----------------------------------------------
# 🔸 StrangerMusic Project
# 🔹 Developed & Maintained by: Shashank Shukla
# 📅 Copyright © 2022 – All Rights Reserved
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


# =========================================================
# LOGGER
# =========================================================

log = LOGGER(__name__)


# =========================================================
# CLEAR CHAT
# =========================================================

async def _clear_(chat_id: int):
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


# =========================================================
# CALL CLASS
# =========================================================

class Call(PyTgCalls):

    def __init__(self):

        PyTgCallsSession.notice_displayed = True

        # -------------------------------------------------
        # ASSISTANT 1
        # -------------------------------------------------

        self.userbot1 = Client(
            name="ShiviAss1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
        )

        self.one = PyTgCalls(
            self.userbot1,
            cache_duration=100,
        )

        # -------------------------------------------------
        # ASSISTANT 2
        # -------------------------------------------------

        self.userbot2 = Client(
            name="ShiviAss2",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING2),
        )

        self.two = PyTgCalls(
            self.userbot2,
            cache_duration=100,
        )

        # -------------------------------------------------
        # ASSISTANT 3
        # -------------------------------------------------

        self.userbot3 = Client(
            name="ShiviAss3",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING3),
        )

        self.three = PyTgCalls(
            self.userbot3,
            cache_duration=100,
        )

        # -------------------------------------------------
        # ASSISTANT 4
        # -------------------------------------------------

        self.userbot4 = Client(
            name="ShiviAss4",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING4),
        )

        self.four = PyTgCalls(
            self.userbot4,
            cache_duration=100,
        )

        # -------------------------------------------------
        # ASSISTANT 5
        # -------------------------------------------------

        self.userbot5 = Client(
            name="ShiviAss5",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING5),
        )

        self.five = PyTgCalls(
            self.userbot5,
            cache_duration=100,
        )

    # =====================================================
    # BUILD STREAM
    # =====================================================

    def _build_stream(
        self,
        source: str,
        video: bool,
        ffmpeg: str | None = None,
    ) -> types.MediaStream:

        if source is None:
            raise AssistantErr(
                "Media source is empty."
            )

        source = str(source).strip()

        if not source:
            raise AssistantErr(
                "Media source is empty."
            )

        # Local file check
        if not source.startswith(
            (
                "http://",
                "https://",
                "rtmp://",
                "rtmps://",
            )
        ):
            if not os.path.exists(source):
                raise AssistantErr(
                    f"Media file not found: {source}"
                )

            if os.path.isdir(source):
                raise AssistantErr(
                    "Media source is a directory."
                )

        return types.MediaStream(
            media_path=source,
            audio_parameters=types.AudioQuality.HIGH,
            video_parameters=types.VideoQuality.HD_720p,
            audio_flags=types.MediaStream.Flags.REQUIRED,
            video_flags=(
                types.MediaStream.Flags.AUTO_DETECT
                if video
                else types.MediaStream.Flags.IGNORE
            ),
            ffmpeg_parameters=ffmpeg,
        )

    # =====================================================
    # PLAY WITH RETRY
    # =====================================================

    async def _play_on_assistant(
        self,
        client: PyTgCalls,
        chat_id: int,
        stream: types.MediaStream,
        retries: int = 3,
    ):

        last_error = None

        for attempt in range(1, retries + 1):

            try:

                await client.play(
                    chat_id=chat_id,
                    stream=stream,
                    config=types.GroupCallConfig(
                        auto_start=False
                    ),
                )

                return True

            except exceptions.NoActiveGroupCall:
                raise

            except exceptions.NoAudioSourceFound:
                raise

            except (
                ConnectionNotFound,
                TelegramServerError,
            ) as e:

                last_error = e

                log.warning(
                    f"Telegram voice server error "
                    f"in {chat_id} | "
                    f"attempt {attempt}/{retries} | "
                    f"{type(e).__name__}: {e}"
                )

                if attempt < retries:

                    await asyncio.sleep(
                        1.5 * attempt
                    )

                    continue

                raise last_error

            except Exception as e:

                log.error(
                    f"Playback error in {chat_id}: {e}"
                )

                raise

        if last_error:
            raise last_error

        return False

    # =====================================================
    # PAUSE
    # =====================================================

    async def pause_stream(self, chat_id: int):

        assistant = await group_assistant(
            self,
            chat_id,
        )

        try:
            await assistant.pause(chat_id)

        except (
            ConnectionNotFound,
            TelegramServerError,
        ) as e:

            log.warning(
                f"Pause failed in {chat_id}: {e}"
            )

            raise AssistantErr(
                "Telegram voice server is temporarily unavailable."
            )

    # =====================================================
    # RESUME
    # =====================================================

    async def resume_stream(self, chat_id: int):

        assistant = await group_assistant(
            self,
            chat_id,
        )

        try:
            await assistant.resume(chat_id)

        except (
            ConnectionNotFound,
            TelegramServerError,
        ) as e:

            log.warning(
                f"Resume failed in {chat_id}: {e}"
            )

            raise AssistantErr(
                "Telegram voice server is temporarily unavailable."
            )

    # =====================================================
    # STOP
    # =====================================================

    async def stop_stream(self, chat_id: int):

        assistant = await group_assistant(
            self,
            chat_id,
        )

        await _clear_(chat_id)

        try:
            await assistant.leave_call(
                chat_id,
                close=False,
            )
        except Exception:
            pass

    # =====================================================
    # FORCE STOP
    # =====================================================

    async def stop_stream_force(self, chat_id: int):

        assistants = [
            (config.STRING1, self.one),
            (config.STRING2, self.two),
            (config.STRING3, self.three),
            (config.STRING4, self.four),
            (config.STRING5, self.five),
        ]

        for string, client in assistants:

            if not string:
                continue

            try:
                await client.leave_call(
                    chat_id,
                    close=False,
                )
            except Exception:
                pass

        await _clear_(chat_id)

    # =====================================================
    # SPEED
    # =====================================================

    async def speedup_stream(
        self,
        chat_id: int,
        file_path,
        speed,
        playing,
    ):

        assistant = await group_assistant(
            self,
            chat_id,
        )

        if str(speed) != "1.0":

            base = os.path.basename(
                str(file_path)
            )

            chatdir = os.path.join(
                os.getcwd(),
                "playback",
                str(speed),
            )

            os.makedirs(
                chatdir,
                exist_ok=True,
            )

            out = os.path.join(
                chatdir,
                base,
            )

            if not os.path.isfile(out):

                if str(speed) == "0.5":
                    vs = 2.0

                elif str(speed) == "0.75":
                    vs = 1.35

                elif str(speed) == "1.5":
                    vs = 0.68

                elif str(speed) == "2.0":
                    vs = 0.5

                else:
                    vs = 1.0

                proc = await asyncio.create_subprocess_shell(

                    cmd=(
                        "ffmpeg "
                        "-y "
                        "-i "
                        f'"{file_path}" '
                        "-filter:v "
                        f"setpts={vs}*PTS "
                        "-filter:a "
                        f"atempo={speed} "
                        f'"{out}"'
                    ),

                    stdin=asyncio.subprocess.PIPE,

                    stdout=asyncio.subprocess.DEVNULL,

                    stderr=asyncio.subprocess.PIPE,
                )

                await proc.communicate()

                if proc.returncode != 0:
                    raise AssistantErr(
                        "Unable to change playback speed."
                    )

        else:
            out = file_path

        if not os.path.exists(out):
            raise AssistantErr(
                "Speed-adjusted media file not found."
            )

        dur = await asyncio.get_running_loop().run_in_executor(
            None,
            check_duration,
            out,
        )

        dur = int(dur)

        played, con_seconds = speed_converter(
            playing[0]["played"],
            speed,
        )

        duration = seconds_to_min(dur)

        xx = f"-ss {played} -to {duration}"

        video_mode = (
            playing[0]["streamtype"] == "video"
        )

        stream = self._build_stream(
            out,
            video=video_mode,
            ffmpeg=xx,
        )

        if str(db[chat_id][0]["file"]) != str(
            file_path
        ):
            raise AssistantErr("Umm")

        await self._play_on_assistant(
            assistant,
            chat_id,
            stream,
        )

        if str(db[chat_id][0]["file"]) == str(
            file_path
        ):

            exis = playing[0].get(
                "old_dur"
            )

            if not exis:

                db[chat_id][0]["old_dur"] = (
                    db[chat_id][0]["dur"]
                )

                db[chat_id][0]["old_second"] = (
                    db[chat_id][0]["seconds"]
                )

            db[chat_id][0]["played"] = (
                con_seconds
            )

            db[chat_id][0]["dur"] = duration

            db[chat_id][0]["seconds"] = dur

            db[chat_id][0]["speed_path"] = out

            db[chat_id][0]["speed"] = speed

    # =====================================================
    # FORCE STOP CURRENT
    # =====================================================

    async def force_stop_stream(
        self,
        chat_id: int,
    ):

        assistant = await group_assistant(
            self,
            chat_id,
        )

        try:

            check = db.get(chat_id)

            if check:
                check.pop(0)

        except Exception:
            pass

        await remove_active_video_chat(
            chat_id
        )

        await remove_active_chat(
            chat_id
        )

        try:
            await assistant.leave_call(
                chat_id,
                close=False,
            )
        except Exception:
            pass

    # =====================================================
    # SKIP
    # =====================================================

    async def skip_stream(
        self,
        chat_id: int,
        link: str,
        video: Union[bool, str] = None,
        image: Union[bool, str] = None,
    ):

        if not link:
            raise AssistantErr(
                "Next media source is empty."
            )

        assistant = await group_assistant(
            self,
            chat_id,
        )

        stream = self._build_stream(
            str(link),
            video=bool(video),
        )

        try:

            await self._play_on_assistant(
                assistant,
                chat_id,
                stream,
                retries=3,
            )

        except (
            ConnectionNotFound,
            TelegramServerError,
        ) as e:

            log.warning(
                f"Skip failed in {chat_id}: {e}"
            )

            raise AssistantErr(
                "Telegram voice server temporarily "
                "unavailable. Please try Skip again."
            )

    # =====================================================
    # SEEK
    # =====================================================

    async def seek_stream(
        self,
        chat_id,
        file_path,
        to_seek,
        duration,
        mode,
    ):

        assistant = await group_assistant(
            self,
            chat_id,
        )

        ffmpeg = (
            f"-ss {to_seek} "
            f"-to {duration}"
        )

        video_mode = mode == "video"

        stream = self._build_stream(
            file_path,
            video=video_mode,
            ffmpeg=ffmpeg,
        )

        await self._play_on_assistant(
            assistant,
            chat_id,
            stream,
        )

    # =====================================================
    # AUTOPLAY
    # =====================================================

    async def autoplay_start(
        self,
        chat_id: int,
        original_chat_id: int,
        seed_title: str,
        seed_vidid: str = None,
        client: PyTgCalls = None,
    ) -> bool:

        if seed_vidid:
            try:
                remember_played(
                    chat_id,
                    seed_vidid,
                )
            except Exception:
                pass

        status_msg = None

        try:

            status_msg = await app.send_message(
                original_chat_id,
                "ʜσʟᴅ ση...\n\n"
                "ᴅσᴡηʟσᴧᴅɪηɢ ηєxᴛ ϻєᴅɪᴧ "
                "ғʀσϻ ᴛʜє ǫυєυє.",
            )

        except Exception:
            status_msg = None

        async def _fail():

            if status_msg:

                try:
                    await status_msg.delete()
                except Exception:
                    pass

            return False

        # -------------------------------------------------
        # FETCH NEXT TRACK
        # -------------------------------------------------

        try:

            track = await fetch_autoplay_track(
                chat_id,
                seed_title,
                seed_vidid,
            )

        except Exception as e:

            log.error(
                f"Autoplay search failed "
                f"in {chat_id}: {e}"
            )

            return await _fail()

        if not track:
            return await _fail()

        vidid = track.get(
            "vidid"
        )

        title = track.get(
            "title",
            "Unknown",
        )

        duration_min = track.get(
            "duration_min",
            "00:00",
        )

        if not vidid:
            return await _fail()

        # -------------------------------------------------
        # DOWNLOAD
        # -------------------------------------------------

        try:

            file_path, direct = await YouTube.download(
                vidid,
                None,
                videoid=True,
            )

        except Exception as e:

            log.error(
                f"Autoplay download failed "
                f"in {chat_id}: {e}"
            )

            return await _fail()

        if not file_path:
            return await _fail()

        # -------------------------------------------------
        # REMEMBER
        # -------------------------------------------------

        try:
            remember_played(
                chat_id,
                vidid,
            )
        except Exception:
            pass

        # -------------------------------------------------
        # QUEUE
        # -------------------------------------------------

        try:

            await put_queue(
                chat_id,
                original_chat_id,
                (
                    file_path
                    if direct
                    else f"vid_{vidid}"
                ),
                title.title(),
                duration_min,
                "🔁 𝐀ᴜᴛᴏᴘʟᴀʏ",
                vidid,
                1,
                "audio",
                forceplay=True,
            )

        except Exception as e:

            log.error(
                f"Autoplay queue failed "
                f"in {chat_id}: {e}"
            )

            return await _fail()

        # -------------------------------------------------
        # RESET STATE
        # -------------------------------------------------

        if db.get(chat_id):

            db[chat_id][0][
                "played"
            ] = 0

            db[chat_id][0][
                "seconds"
            ] = 0

            db[chat_id][0][
                "speed"
            ] = 1.0

            db[chat_id][0][
                "speed_path"
            ] = None

            db[chat_id][0][
                "old_dur"
            ] = None

            db[chat_id][0][
                "old_second"
            ] = 0

        # -------------------------------------------------
        # STREAM
        # -------------------------------------------------

        try:

            stream = self._build_stream(
                file_path,
                video=False,
            )

        except Exception as e:

            log.error(
                f"Autoplay stream build failed "
                f"in {chat_id}: {e}"
            )

            return await _fail()

        assistant = (
            client
            or await group_assistant(
                self,
                chat_id,
            )
        )

        try:

            await self._play_on_assistant(
                assistant,
                chat_id,
                stream,
                retries=3,
            )

        except (
            ConnectionNotFound,
            TelegramServerError,
        ) as e:

            log.warning(
                f"Autoplay Telegram error "
                f"in {chat_id}: {e}"
            )

            return await _fail()

        except Exception as e:

            log.error(
                f"Autoplay playback failed "
                f"in {chat_id}: {e}"
            )

            return await _fail()

        # -------------------------------------------------
        # SEND NOW PLAYING
        # -------------------------------------------------

        try:

            language = await get_lang(
                chat_id
            )

            _ = get_string(
                language
            )

            img = await gen_thumb(
                vidid
            )

            button = stream_markup(
                _,
                chat_id,
            )

            run = await app.send_photo(

                chat_id=original_chat_id,

                photo=img,

                caption=_[
                    "stream_1"
                ].format(

                    f"https://t.me/"
                    f"{app.username}"
                    f"?start=info_{vidid}",

                    title[:23],

                    duration_min,

                    "𝐀ᴜᴛᴏᴘʟᴀʏ 🚩",

                    " 🎵 Aᴜᴅɪᴏ",
                ),

                reply_markup=InlineKeyboardMarkup(
                    button
                ),
            )

            db[chat_id][0][
                "mystic"
            ] = run

            db[chat_id][0][
                "markup"
            ] = "stream"

        except Exception as e:

            log.warning(
                f"Autoplay message failed "
                f"in {chat_id}: {e}"
            )

        # -------------------------------------------------
        # DELETE DOWNLOAD MESSAGE
        # -------------------------------------------------

        if status_msg:

            try:
                await status_msg.delete()
            except Exception:
                pass

        # -------------------------------------------------
        # ACTIVE CHAT
        # -------------------------------------------------

        try:
            await add_active_chat(
                chat_id
            )
        except Exception:
            pass

        try:
            await music_on(
                chat_id
            )
        except Exception:
            pass

        return True

    # =====================================================
    # STREAM CALL
    # =====================================================

    async def stream_call(self, link):

        assistant = await group_assistant(
            self,
            config.LOG_GROUP_ID,
        )

        stream = self._build_stream(
            link,
            video=True,
        )

        await self._play_on_assistant(
            assistant,
            config.LOG_GROUP_ID,
            stream,
        )

        await asyncio.sleep(0.2)

        try:
            await assistant.leave_call(
                config.LOG_GROUP_ID,
                close=False,
            )
        except Exception:
            pass

    # =====================================================
    # JOIN CALL
    # =====================================================

    async def join_call(
        self,
        chat_id: int,
        original_chat_id: int,
        link,
        video: Union[bool, str] = None,
        image: Union[bool, str] = None,
    ):

        if not link:
            raise AssistantErr(
                "Media source is empty."
            )

        assistant = await group_assistant(
            self,
            chat_id,
        )

        language = await get_lang(
            chat_id
        )

        _ = get_string(
            language
        )

        stream = self._build_stream(
            link,
            video=bool(video),
        )

        try:

            await self._play_on_assistant(
                assistant,
                chat_id,
                stream,
                retries=3,
            )

        except exceptions.NoActiveGroupCall:

            raise AssistantErr(
                _["call_8"]
            )

        except exceptions.NoAudioSourceFound:

            raise AssistantErr(
                _["call_10"]
            )

        except (
            ConnectionNotFound,
            TelegramServerError,
        ) as e:

            log.warning(
                f"Telegram server error "
                f"while joining {chat_id}: {e}"
            )

            raise AssistantErr(
                "Telegram voice server is "
                "temporarily unavailable. "
                "Please try again."
            )

        except Exception as e:

            log.error(
                f"join_call failed "
                f"in {chat_id}: {e}"
            )

            raise AssistantErr(
                _["call_10"]
            )

        await add_active_chat(
            chat_id
        )

        await music_on(
            chat_id
        )

        if video:
            await add_active_video_chat(
                chat_id
            )

        if await is_autoend():

            counter[chat_id] = {}

            try:

                users = len(
                    await assistant.get_participants(
                        chat_id
                    )
                )

                if users == 1:

                    autoend[chat_id] = (
                        datetime.now()
                        + timedelta(
                            minutes=1
                        )
                    )

            except Exception:
                pass

    # =====================================================
    # CHANGE STREAM
    # =====================================================

    async def change_stream(
        self,
        client: PyTgCalls,
        chat_id: int,
    ):

        check = db.get(chat_id)

        if not check:
            try:
                await client.leave_call(
                    chat_id,
                    close=False,
                )
            except Exception:
                pass
            return

        popped = None

        try:

            loop = await get_loop(
                chat_id
            )

            # -------------------------------------------------
            # REMOVE CURRENT TRACK
            # -------------------------------------------------

            if loop == 0:

                popped = check.pop(0)

            else:

                loop = loop - 1

                await set_loop(
                    chat_id,
                    loop,
                )

            # -------------------------------------------------
            # DELETE OLD NOW PLAYING MESSAGE
            # -------------------------------------------------

            if popped:

                old_mystic = popped.get(
                    "mystic"
                )

                if old_mystic:

                    try:
                        await old_mystic.delete()
                    except Exception:
                        pass

            # -------------------------------------------------
            # AUTO CLEAN
            # -------------------------------------------------

            try:
                await auto_clean(
                    popped
                )
            except Exception as e:
                log.warning(
                    f"Auto clean failed: {e}"
                )

            # -------------------------------------------------
            # QUEUE EMPTY
            # -------------------------------------------------

            if not check:

                if (
                    popped
                    and await is_autoplay_on(
                        chat_id
                    )
                ):

                    try:

                        started = (
                            await self.autoplay_start(

                                chat_id,

                                popped.get(
                                    "chat_id",
                                    chat_id,
                                ),

                                popped.get(
                                    "title",
                                    "Music",
                                ),

                                popped.get(
                                    "vidid"
                                ),

                                client=client,
                            )
                        )

                        if started:
                            return

                    except (
                        ConnectionNotFound,
                        TelegramServerError,
                    ) as e:

                        log.warning(
                            f"Autoplay Telegram error "
                            f"in {chat_id}: {e}"
                        )

                    except Exception as e:

                        log.error(
                            f"Autoplay error "
                            f"in {chat_id}: {e}"
                        )

                await _clear_(
                    chat_id
                )

                try:
                    await client.leave_call(
                        chat_id,
                        close=False,
                    )
                except Exception:
                    pass

                return

        except (
            ConnectionNotFound,
            TelegramServerError,
        ) as e:

            # -------------------------------------------------
            # IMPORTANT:
            # DO NOT CLEAR QUEUE ON TEMPORARY
            # TELEGRAM SERVER ERROR
            # -------------------------------------------------

            log.warning(
                f"Telegram server error "
                f"while changing stream "
                f"in {chat_id}: {e}"
            )

            await asyncio.sleep(2)

            if db.get(chat_id):

                try:

                    await self.change_stream(
                        client,
                        chat_id,
                    )

                    return

                except Exception as retry_error:

                    log.error(
                        f"Stream retry failed "
                        f"in {chat_id}: "
                        f"{retry_error}"
                    )

            return

        except Exception as e:

            log.error(
                f"change_stream queue error "
                f"in {chat_id}: {e}"
            )

            return

        # =====================================================
        # NEXT TRACK
        # =====================================================

        check = db.get(chat_id)

        if not check:
            return

        queued = check[0].get(
            "file"
        )

        if not queued:
            log.error(
                f"Empty queued media "
                f"in {chat_id}"
            )
            return

        language = await get_lang(
            chat_id
        )

        _ = get_string(
            language
        )

        title = (
            check[0]
            .get("title", "Unknown")
            .title()
        )

        user = check[0].get(
            "by",
            "Unknown",
        )

        original_chat_id = check[0].get(
            "chat_id",
            chat_id,
        )

        streamtype = check[0].get(
            "streamtype",
            "audio",
        )

        stype = (
            streamtype.title()
            if streamtype
            else "Audio"
        )

        videoid = check[0].get(
            "vidid"
        )

        # -------------------------------------------------
        # RESET PLAY STATE
        # -------------------------------------------------

        db[chat_id][0][
            "played"
        ] = 0

        exis = check[0].get(
            "old_dur"
        )

        if exis:

            db[chat_id][0][
                "dur"
            ] = exis

            db[chat_id][0][
                "seconds"
            ] = check[0].get(
                "old_second",
                0,
            )

            db[chat_id][0][
                "speed_path"
            ] = None

            db[chat_id][0][
                "speed"
            ] = 1.0

        video = (
            str(streamtype)
            == "video"
        )

        # =====================================================
        # LIVE STREAM
        # =====================================================

        if "live_" in str(queued):

            try:

                n, link = await YouTube.video(
                    videoid,
                    True,
                )

            except Exception as e:

                log.error(
                    f"Live video fetch failed "
                    f"in {chat_id}: {e}"
                )

                return await app.send_message(
                    original_chat_id,
                    text=_["call_6"],
                )

            if n == 0 or not link:

                return await app.send_message(
                    original_chat_id,
                    text=_["call_6"],
                )

            try:

                stream = self._build_stream(
                    link,
                    video=video,
                )

                await self._play_on_assistant(
                    client,
                    chat_id,
                    stream,
                )

            except (
                ConnectionNotFound,
                TelegramServerError,
            ) as e:

                log.warning(
                    f"Live Telegram error "
                    f"in {chat_id}: {e}"
                )

                return

            except Exception as e:

                log.error(
                    f"Live playback failed "
                    f"in {chat_id}: {e}"
                )

                return await app.send_message(
                    original_chat_id,
                    text=_["call_6"],
                )

            try:

                img = await gen_thumb(
                    videoid
                )

                button = stream_markup(
                    _,
                    chat_id,
                )

                run = await app.send_photo(

                    chat_id=original_chat_id,

                    photo=img,

                    caption=_[
                        "stream_1"
                    ].format(

                        f"https://t.me/"
                        f"{app.username}"
                        f"?start=info_{videoid}",

                        title[:23],

                        check[0].get(
                            "dur",
                            "00:00",
                        ),

                        user,

                        stype,
                    ),

                    reply_markup=InlineKeyboardMarkup(
                        button
                    ),
                )

                db[chat_id][0][
                    "mystic"
                ] = run

                db[chat_id][0][
                    "markup"
                ] = "tg"

            except Exception:
                pass

        # =====================================================
        # YOUTUBE VID
        # =====================================================

        elif "vid_" in str(queued):

            mystic = None

            try:

                mystic = await app.send_message(
                    original_chat_id,
                    _["call_7"],
                )

            except Exception:
                pass

            try:

                file_path, direct = (
                    await YouTube.download(
                        videoid,
                        mystic,
                        videoid=True,
                        video=video,
                    )
                )

            except Exception as e:

                log.error(
                    f"YouTube download failed "
                    f"in {chat_id}: {e}"
                )

                if mystic:

                    try:
                        await mystic.edit_text(
                            _["call_6"],
                            disable_web_page_preview=True,
                        )
                    except Exception:
                        pass

                return

            if not file_path:

                if mystic:

                    try:
                        await mystic.edit_text(
                            _["call_6"],
                        )
                    except Exception:
                        pass

                return

            try:

                stream = self._build_stream(
                    file_path,
                    video=video,
                )

                await self._play_on_assistant(
                    client,
                    chat_id,
                    stream,
                )

            except (
                ConnectionNotFound,
                TelegramServerError,
            ) as e:

                log.warning(
                    f"YouTube Telegram error "
                    f"in {chat_id}: {e}"
                )

                return

            except Exception as e:

                log.error(
                    f"YouTube playback failed "
                    f"in {chat_id}: {e}"
                )

                return

            try:

                img = await gen_thumb(
                    videoid
                )

                button = stream_markup(
                    _,
                    chat_id,
                )

                if mystic:

                    try:
                        await mystic.delete()
                    except Exception:
                        pass

                run = await app.send_photo(

                    chat_id=original_chat_id,

                    photo=img,

                    caption=_[
                        "stream_1"
                    ].format(

                        f"https://t.me/"
                        f"{app.username}"
                        f"?start=info_{videoid}",

                        title[:23],

                        check[0].get(
                            "dur",
                            "00:00",
                        ),

                        user,

                        stype,
                    ),

                    reply_markup=InlineKeyboardMarkup(
                        button
                    ),
                )

                db[chat_id][0][
                    "mystic"
                ] = run

                db[chat_id][0][
                    "markup"
                ] = "stream"

            except Exception as e:

                log.warning(
                    f"Now playing message "
                    f"failed: {e}"
                )

        # =====================================================
        # TELEGRAM INDEX
        # =====================================================

        elif "index_" in str(queued):

            try:

                stream = self._build_stream(
                    videoid,
                    video=video,
                )

                await self._play_on_assistant(
                    client,
                    chat_id,
                    stream,
                )

            except (
                ConnectionNotFound,
                TelegramServerError,
            ) as e:

                log.warning(
                    f"Index Telegram error "
                    f"in {chat_id}: {e}"
                )

                return

            except Exception as e:

                log.error(
                    f"Index playback failed "
                    f"in {chat_id}: {e}"
                )

                return await app.send_message(
                    original_chat_id,
                    text=_["call_6"],
                )

            try:

                button = stream_markup(
                    _,
                    chat_id,
                )

                run = await app.send_photo(

                    chat_id=original_chat_id,

                    photo=config.STREAM_IMG_URL,

                    caption=_[
                        "stream_2"
                    ].format(
                        user
                    ),

                    reply_markup=InlineKeyboardMarkup(
                        button
                    ),
                )

                db[chat_id][0][
                    "mystic"
                ] = run

                db[chat_id][0][
                    "markup"
                ] = "tg"

            except Exception:
                pass

        # =====================================================
        # NORMAL FILE / STREAM
        # =====================================================

        else:

            try:

                stream = self._build_stream(
                    queued,
                    video=video,
                )

                await self._play_on_assistant(
                    client,
                    chat_id,
                    stream,
                )

            except (
                ConnectionNotFound,
                TelegramServerError,
            ) as e:

                log.warning(
                    f"Normal stream Telegram error "
                    f"in {chat_id}: {e}"
                )

                return

            except Exception as e:

                log.error(
                    f"Normal playback failed "
                    f"in {chat_id}: {e}"
                )

                return await app.send_message(
                    original_chat_id,
                    text=_["call_6"],
                )

            # -------------------------------------------------
            # TELEGRAM MEDIA
            # -------------------------------------------------

            if videoid == "telegram":

                try:

                    button = stream_markup(
                        _,
                        chat_id,
                    )

                    run = await app.send_photo(

                        chat_id=original_chat_id,

                        photo=(
                            config.TELEGRAM_AUDIO_URL
                            if str(streamtype)
                            == "audio"
                            else config.TELEGRAM_VIDEO_URL
                        ),

                        caption=_[
                            "stream_1"
                        ].format(

                            config.SUPPORT_GROUP,

                            title[:23],

                            check[0].get(
                                "dur",
                                "00:00",
                            ),

                            user,

                            stype,
                        ),

                        reply_markup=InlineKeyboardMarkup(
                            button
                        ),
                    )

                    db[chat_id][0][
                        "mystic"
                    ] = run

                    db[chat_id][0][
                        "markup"
                    ] = "tg"

                except Exception:
                    pass

            # -------------------------------------------------
            # SOUNDCLOUD
            # -------------------------------------------------

            elif videoid == "soundcloud":

                try:

                    button = stream_markup(
                        _,
                        chat_id,
                    )

                    run = await app.send_photo(

                        chat_id=original_chat_id,

                        photo=config.SOUNDCLOUD_IMG_URL,

                        caption=_[
                            "stream_1"
                        ].format(

                            config.SUPPORT_GROUP,

                            title[:23],

                            check[0].get(
                                "dur",
                                "00:00",
                            ),

                            user,

                            stype,
                        ),

                        reply_markup=InlineKeyboardMarkup(
                            button
                        ),
                    )

                    db[chat_id][0][
                        "mystic"
                    ] = run

                    db[chat_id][0][
                        "markup"
                    ] = "tg"

                except Exception:
                    pass

            # -------------------------------------------------
            # YOUTUBE / OTHER
            # -------------------------------------------------

            else:

                try:

                    img = await gen_thumb(
                        videoid
                    )

                    button = stream_markup(
                        _,
                        chat_id,
                    )

                    run = await app.send_photo(

                        chat_id=original_chat_id,

                        photo=img,

                        caption=_[
                            "stream_1"
                        ].format(

                            f"https://t.me/"
                            f"{app.username}"
                            f"?start=info_{videoid}",

                            title[:23],

                            check[0].get(
                                "dur",
                                "00:00",
                            ),

                            user,

                            stype,
                        ),

                        reply_markup=InlineKeyboardMarkup(
                            button
                        ),
                    )

                    db[chat_id][0][
                        "mystic"
                    ] = run

                    db[chat_id][0][
                        "markup"
                    ] = "stream"

                except Exception as e:

                    log.warning(
                        f"Thumbnail/message failed: {e}"
                    )

    # =====================================================
    # PING
    # =====================================================

    async def ping(self):

        values = []

        assistants = [
            (config.STRING1, self.one),
            (config.STRING2, self.two),
            (config.STRING3, self.three),
            (config.STRING4, self.four),
            (config.STRING5, self.five),
        ]

        for string, client in assistants:

            if not string:
                continue

            try:

                value = client.ping

                if callable(value):

                    result = value()

                    if asyncio.iscoroutine(
                        result
                    ):
                        result = await result

                    values.append(
                        float(result)
                    )

                else:

                    values.append(
                        float(value)
                    )

            except Exception:
                continue

        if not values:
            return "0"

        return str(
            round(
                sum(values)
                / len(values),
                3,
            )
        )

    # =====================================================
    # START ASSISTANTS
    # =====================================================

    async def start(self):

        log.info(
            "Starting PyTgCalls Clients..."
        )

        if config.STRING1:

            try:
                await self.one.start()
                log.info(
                    "Assistant 1 started."
                )
            except Exception as e:
                log.error(
                    f"Assistant 1 failed: {e}"
                )

        if config.STRING2:

            try:
                await self.two.start()
                log.info(
                    "Assistant 2 started."
                )
            except Exception as e:
                log.error(
                    f"Assistant 2 failed: {e}"
                )

        if config.STRING3:

            try:
                await self.three.start()
                log.info(
                    "Assistant 3 started."
                )
            except Exception as e:
                log.error(
                    f"Assistant 3 failed: {e}"
                )

        if config.STRING4:

            try:
                await self.four.start()
                log.info(
                    "Assistant 4 started."
                )
            except Exception as e:
                log.error(
                    f"Assistant 4 failed: {e}"
                )

        if config.STRING5:

            try:
                await self.five.start()
                log.info(
                    "Assistant 5 started."
                )
            except Exception as e:
                log.error(
                    f"Assistant 5 failed: {e}"
                )

    # =====================================================
    # UPDATE HANDLERS
    # =====================================================

    async def decorators(self):

        assistants = [
            (config.STRING1, self.one),
            (config.STRING2, self.two),
            (config.STRING3, self.three),
            (config.STRING4, self.four),
            (config.STRING5, self.five),
        ]

        for string, client in assistants:

            if not string:
                continue

            @client.on_update()
            async def _update_handler(
                _,
                update: types.Update,
                _client=client,
            ):

                try:

                    # -------------------------------------------------
                    # STREAM ENDED
                    # -------------------------------------------------

                    if isinstance(
                        update,
                        types.StreamEnded,
                    ):

                        if (
                            update.stream_type
                            == types.StreamEnded.Type.AUDIO
                        ):

                            await self.change_stream(
                                _client,
                                update.chat_id,
                            )

                    # -------------------------------------------------
                    # CHAT UPDATE
                    # -------------------------------------------------

                    elif isinstance(
                        update,
                        types.ChatUpdate,
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

                    log.warning(
                        f"Telegram update error: {e}"
                    )

                except Exception as e:

                    log.error(
                        f"Update handler error: {e}"
                    )


# =========================================================
# GLOBAL CALL INSTANCE
# =========================================================

Shivi = Call()
