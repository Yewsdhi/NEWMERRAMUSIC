# Copyright (c) 2025 TheHamkerAlone
# Licensed under the MIT License.
# This file is part of ShiviMusic.

import os
import asyncio
import numpy as np
import aiohttp

from PIL import (
    Image,
    ImageDraw,
    ImageFilter,
    ImageFont,
)

# ============================================================
# CONFIG FIX
# ============================================================

try:
    import config
except ImportError:
    config = None


# ============================================================
# TRACK IMPORT
# ============================================================

try:
    from ShiviMusic.helpers import Track
except ImportError:
    try:
        from ShiviMusic.utils.database import Track
    except ImportError:
        Track = object


# ============================================================
# UNIDECODE
# ============================================================

try:
    from unidecode import unidecode
except ImportError:
    def unidecode(text):
        return str(text)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

# /app/ShiviMusic/assets/
ASSETS_DIR = os.path.abspath(
    os.path.join(
        BASE_DIR,
        "..",
        "assets",
    )
)

FONT_PATH = os.path.join(
    ASSETS_DIR,
    "font.ttf",
)

FONT2_PATH = os.path.join(
    ASSETS_DIR,
    "font2.ttf",
)

TEMPLATE_PATH = os.path.join(
    ASSETS_DIR,
    "template.png",
)

CACHE_DIR = os.path.abspath(
    os.path.join(
        os.getcwd(),
        "cache",
    )
)


# ============================================================
# DEFAULT THUMB
# ============================================================

def get_default_thumb():
    if config is not None:
        return getattr(
            config,
            "DEFAULT_THUMB",
            "",
        )

    return ""


# ============================================================
# SAFE FONT
# ============================================================

def safe_font(path, size):

    try:

        if os.path.exists(path):

            return ImageFont.truetype(
                path,
                size,
            )

        print(
            f"⚠️ ShiviMusic font not found: {path}"
        )

    except Exception as e:

        print(
            f"⚠️ ShiviMusic font error: {e}"
        )

    return ImageFont.load_default()


# ============================================================
# THUMBNAIL CLASS
# ============================================================

class Thumbnail:

    def __init__(self):

        self.size = (
            1280,
            720,
        )

        # ----------------------------------------------------
        # SHIVIMUSIC FONTS
        # ----------------------------------------------------

        self.title_font = safe_font(
            FONT_PATH,
            44,
        )

        self.meta_font = safe_font(
            FONT_PATH,
            26,
        )

        self.tag_font = safe_font(
            FONT2_PATH,
            28,
        )

    # ========================================================
    # START
    # ========================================================

    async def start(self):

        os.makedirs(
            CACHE_DIR,
            exist_ok=True,
        )

        if not os.path.exists(
            FONT_PATH
        ):
            print(
                f"⚠️ Missing font: {FONT_PATH}"
            )

        if not os.path.exists(
            FONT2_PATH
        ):
            print(
                f"⚠️ Missing font2: {FONT2_PATH}"
            )

        if not os.path.exists(
            TEMPLATE_PATH
        ):
            print(
                f"⚠️ Missing template: {TEMPLATE_PATH}"
            )

        return True

    # ========================================================
    # DOWNLOAD THUMBNAIL
    # ========================================================

    async def save_thumb(
        self,
        output_path,
        url,
    ):

        if not url:
            return output_path

        if not str(url).startswith(
            (
                "http://",
                "https://",
            )
        ):
            return output_path

        headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/131.0 Safari/537.36"
            )
        }

        timeout = aiohttp.ClientTimeout(
            total=20
        )

        for attempt in range(3):

            try:

                async with aiohttp.ClientSession(
                    headers=headers,
                    timeout=timeout,
                ) as session:

                    async with session.get(
                        str(url)
                    ) as response:

                        if response.status == 200:

                            data = await response.read()

                            if data:

                                with open(
                                    output_path,
                                    "wb",
                                ) as file:

                                    file.write(
                                        data
                                    )

                                return output_path

                        else:

                            print(
                                "⚠️ Thumbnail HTTP "
                                f"status: {response.status}"
                            )

            except Exception as e:

                if attempt == 2:

                    print(
                        "❌ Thumbnail download "
                        f"failed: {e}"
                    )

                await asyncio.sleep(1)

        return output_path

    # ========================================================
    # ELLIPSIZE
    # ========================================================

    @staticmethod
    def ellipsize(
        draw,
        text,
        font,
        max_width,
    ):

        text = str(
            text or ""
        )

        try:

            bbox = draw.textbbox(
                (0, 0),
                text,
                font=font,
            )

            if bbox[2] <= max_width:
                return text

        except Exception:

            return text

        low = 1
        high = len(text)
        result = "…"

        while low <= high:

            mid = (
                low + high
            ) // 2

            candidate = (
                text[:mid].rstrip()
                + "…"
            )

            try:

                bbox = draw.textbbox(
                    (0, 0),
                    candidate,
                    font=font,
                )

                if bbox[2] <= max_width:

                    result = candidate
                    low = mid + 1

                else:

                    high = mid - 1

            except Exception:

                break

        return result

    # ========================================================
    # GENERATE
    # ========================================================

    async def generate(
        self,
        song,
    ):

        temp_path = None

        try:

            os.makedirs(
                CACHE_DIR,
                exist_ok=True,
            )

            # ------------------------------------------------
            # SONG ID
            # ------------------------------------------------

            song_id = getattr(
                song,
                "id",
                None,
            )

            if not song_id:

                song_id = getattr(
                    song,
                    "vidid",
                    None,
                )

            if not song_id:

                song_id = getattr(
                    song,
                    "videoid",
                    None,
                )

            if not song_id:

                song_id = "unknown"

            song_id = str(
                song_id
            )

            song_id = "".join(
                char
                if (
                    char.isalnum()
                    or char in "-_"
                )
                else "_"
                for char in song_id
            )

            temp_path = os.path.join(
                CACHE_DIR,
                f"temp_{song_id}.jpg",
            )

            final_path = os.path.join(
                CACHE_DIR,
                f"{song_id}.png",
            )

            # ------------------------------------------------
            # CACHE
            # ------------------------------------------------

            if os.path.exists(
                final_path
            ):
                return final_path

            # ------------------------------------------------
            # THUMBNAIL URL
            # ------------------------------------------------

            thumbnail_url = getattr(
                song,
                "thumbnail",
                None,
            )

            if not thumbnail_url:

                thumbnail_url = getattr(
                    song,
                    "thumb",
                    None,
                )

            if not thumbnail_url:

                return get_default_thumb()

            await self.save_thumb(
                temp_path,
                thumbnail_url,
            )

            # ------------------------------------------------
            # OPEN IMAGE
            # ------------------------------------------------

            try:

                if not os.path.exists(
                    temp_path
                ):
                    raise FileNotFoundError(
                        "Thumbnail download failed"
                    )

                source = Image.open(
                    temp_path
                ).convert("RGBA")

            except Exception as e:

                print(
                    f"⚠️ Thumbnail image error: {e}"
                )

                source = Image.new(
                    "RGBA",
                    self.size,
                    (
                        30,
                        30,
                        30,
                        255,
                    ),
                )

            width, height = self.size

            # =================================================
            # BACKGROUND
            # =================================================

            target_ratio = (
                width / height
            )

            source_ratio = (
                source.width
                / source.height
            )

            if source_ratio > target_ratio:

                crop_width = int(
                    source.height
                    * target_ratio
                )

                offset = (
                    source.width
                    - crop_width
                ) // 2

                background = source.crop(
                    (
                        offset,
                        0,
                        offset + crop_width,
                        source.height,
                    )
                )

            else:

                crop_height = int(
                    source.width
                    / target_ratio
                )

                offset = (
                    source.height
                    - crop_height
                ) // 2

                background = source.crop(
                    (
                        0,
                        offset,
                        source.width,
                        offset + crop_height,
                    )
                )

            background = background.resize(
                (
                    width,
                    height,
                ),
                Image.Resampling.LANCZOS,
            )

            background = background.filter(
                ImageFilter.GaussianBlur(
                    25
                )
            )

            overlay = Image.new(
                "RGBA",
                (
                    width,
                    height,
                ),
                (
                    0,
                    0,
                    0,
                    100,
                ),
            )

            background = Image.alpha_composite(
                background,
                overlay,
            )

            # =================================================
            # TEMPLATE
            # =================================================

            if os.path.exists(
                TEMPLATE_PATH
            ):

                try:

                    template = Image.open(
                        TEMPLATE_PATH
                    ).convert("RGBA")

                    template = template.resize(
                        (
                            width,
                            height,
                        ),
                        Image.Resampling.LANCZOS,
                    )

                    template_array = np.array(
                        template
                    ).astype(float)

                    red = (
                        template_array[:, :, 0]
                    )

                    green = (
                        template_array[:, :, 1]
                    )

                    blue = (
                        template_array[:, :, 2]
                    )

                    distance = np.maximum(
                        np.maximum(
                            np.abs(
                                red - 147.5
                            ),
                            np.abs(
                                green - 147.5
                            ),
                        ),
                        np.abs(
                            blue - 147.5
                        ),
                    )

                    alpha = np.clip(
                        (
                            distance - 8
                        )
                        / 17.0
                        * 255,
                        0,
                        255,
                    )

                    alpha[:, :640] = 0

                    template_array[
                        :,
                        :,
                        3
                    ] = alpha

                    template = Image.fromarray(
                        template_array.astype(
                            np.uint8
                        )
                    )

                    background = Image.alpha_composite(
                        background,
                        template,
                    )

                except Exception as e:

                    print(
                        f"⚠️ Template error: {e}"
                    )

            # =================================================
            # COVER
            # =================================================

            cover_x = 100
            cover_y = 104

            cover_width = 512
            cover_height = 512

            cover_radius = 38

            # ------------------------------------------------
            # SHADOW
            # ------------------------------------------------

            shadow = Image.new(
                "RGBA",
                (
                    width,
                    height,
                ),
                (
                    0,
                    0,
                    0,
                    0,
                ),
            )

            shadow_draw = ImageDraw.Draw(
                shadow
            )

            shadow_draw.rounded_rectangle(
                (
                    cover_x + 6,
                    cover_y + 8,
                    cover_x
                    + cover_width
                    + 6,
                    cover_y
                    + cover_height
                    + 8,
                ),
                radius=cover_radius + 4,
                fill=(
                    0,
                    0,
                    0,
                    140,
                ),
            )

            shadow = shadow.filter(
                ImageFilter.GaussianBlur(
                    18
                )
            )

            background = Image.alpha_composite(
                background,
                shadow,
            )

            # ------------------------------------------------
            # COVER IMAGE
            # ------------------------------------------------

            cover = source.resize(
                (
                    cover_width,
                    cover_height,
                ),
                Image.Resampling.LANCZOS,
            )

            mask = Image.new(
                "L",
                (
                    cover_width,
                    cover_height,
                ),
                0,
            )

            ImageDraw.Draw(
                mask
            ).rounded_rectangle(
                (
                    0,
                    0,
                    cover_width,
                    cover_height,
                ),
                radius=cover_radius,
                fill=255,
            )

            background.paste(
                cover,
                (
                    cover_x,
                    cover_y,
                ),
                mask,
            )

            # =================================================
            # TEXT
            # =================================================

            draw = ImageDraw.Draw(
                background
            )

            text_x = 715
            max_width = 320

            # ------------------------------------------------
            # TITLE
            # ------------------------------------------------

            title = getattr(
                song,
                "title",
                "Unknown Song",
            )

            title = unidecode(
                str(title)
            )

            title = self.ellipsize(
                draw,
                title,
                self.title_font,
                max_width,
            )

            title_y = (
                cover_y + 12
            )

            draw.text(
                (
                    text_x,
                    title_y,
                ),
                title,
                fill=(
                    255,
                    255,
                    255,
                    255,
                ),
                font=self.title_font,
            )

            # ------------------------------------------------
            # ARTIST
            # ------------------------------------------------

            artist = getattr(
                song,
                "channel_name",
                None,
            )

            if not artist:

                artist = getattr(
                    song,
                    "artist",
                    None,
                )

            if not artist:

                artist = getattr(
                    song,
                    "channel",
                    None,
                )

            if not artist:

                artist = "ShiviMusic"

            artist = unidecode(
                str(artist)
            )

            artist = self.ellipsize(
                draw,
                artist,
                self.meta_font,
                max_width + 60,
            )

            artist_y = (
                title_y + 52
            )

            draw.text(
                (
                    text_x,
                    artist_y,
                ),
                artist,
                fill=(
                    200,
                    200,
                    200,
                    255,
                ),
                font=self.meta_font,
            )

            # =================================================
            # SHIVIMUSIC BRANDING
            # =================================================

            brand = "ShiviMusic"

            brand_bbox = draw.textbbox(
                (0, 0),
                brand,
                font=self.tag_font,
            )

            brand_width = (
                brand_bbox[2]
                - brand_bbox[0]
            )

            brand_height = (
                brand_bbox[3]
                - brand_bbox[1]
            )

            brand_x = (
                width
                - brand_width
                - 40
            )

            brand_y = (
                height
                - brand_height
                - 30
            )

            # Branding shadow
            draw.text(
                (
                    brand_x + 2,
                    brand_y + 2,
                ),
                brand,
                fill=(
                    0,
                    0,
                    0,
                    160,
                ),
                font=self.tag_font,
            )

            # Branding
            draw.text(
                (
                    brand_x,
                    brand_y,
                ),
                brand,
                fill=(
                    255,
                    255,
                    255,
                    235,
                ),
                font=self.tag_font,
            )

            # =================================================
            # SAVE
            # =================================================

            background = background.convert(
                "RGB"
            )

            background.save(
                final_path,
                "PNG",
                optimize=True,
            )

            # ------------------------------------------------
            # DELETE TEMP
            # ------------------------------------------------

            try:

                if (
                    temp_path
                    and os.path.exists(
                        temp_path
                    )
                ):
                    os.remove(
                        temp_path
                    )

            except Exception:
                pass

            return final_path

        except Exception as e:

            print(
                "❌ ShiviMusic Thumbnail "
                f"Error: {e}"
            )

            try:

                if (
                    temp_path
                    and os.path.exists(
                        temp_path
                    )
                ):
                    os.remove(
                        temp_path
                    )

            except Exception:
                pass

            return get_default_thumb()


# ============================================================
# GLOBAL INSTANCE
# ============================================================

thumb = Thumbnail()
thumbnail = thumb


# ============================================================
# COMPATIBILITY FUNCTION
# ============================================================
# call.py mein:
#
# from ShiviMusic.utils.thumbnails import get_thumb
#
# use ho sake isliye get_thumb bhi diya hai.
# ============================================================

async def get_thumb(song):

    return await thumb.generate(song)
