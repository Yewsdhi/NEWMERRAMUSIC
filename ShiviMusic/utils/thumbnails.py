# Copyright (c) 2025 TheHamkerAlone
# Licensed under the MIT License.
# This file is part of ShiviMusic.

import os
import asyncio
import numpy as np
import aiohttp

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from ShiviMusic import config

try:
    from ShiviMusic.helpers import Track
except ImportError:
    Track = object

try:
    from unidecode import unidecode
except ImportError:
    def unidecode(text):
        return text


# ============================================================
# SHIVIMUSIC PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ShiviMusic/assets/
ASSETS_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..", "assets")
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
            f"⚠️ Font not found: {path}"
        )

    except Exception as e:
        print(
            f"⚠️ Font loading error: {e}"
        )

    return ImageFont.load_default()


# ============================================================
# THUMBNAIL
# ============================================================

class Thumbnail:

    def __init__(self):

        self.size = (1280, 720)

        # ====================================================
        # SHIVIMUSIC FONTS
        # ====================================================

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
            "cache",
            exist_ok=True,
        )

        if not os.path.exists(FONT_PATH):
            print(
                f"⚠️ Missing: {FONT_PATH}"
            )

        if not os.path.exists(FONT2_PATH):
            print(
                f"⚠️ Missing: {FONT2_PATH}"
            )

        if not os.path.exists(TEMPLATE_PATH):
            print(
                f"⚠️ Missing: {TEMPLATE_PATH}"
            )

        return True

    # ========================================================
    # DOWNLOAD THUMB
    # ========================================================

    async def save_thumb(
        self,
        output_path: str,
        url: str,
    ):

        if not url:
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

                if not str(url).startswith(
                    ("http://", "https://")
                ):
                    return output_path

                async with aiohttp.ClientSession(
                    headers=headers,
                    timeout=timeout,
                ) as session:

                    async with session.get(
                        url
                    ) as response:

                        if response.status == 200:

                            data = await response.read()

                            if data:

                                with open(
                                    output_path,
                                    "wb",
                                ) as file:
                                    file.write(data)

                                return output_path

            except Exception as e:

                if attempt == 2:
                    print(
                        "❌ Thumbnail download "
                        f"error: {e}"
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

        text = str(text or "")

        try:

            if draw.textbbox(
                (0, 0),
                text,
                font=font,
            )[2] <= max_width:
                return text

        except Exception:
            return text

        low = 1
        high = len(text)
        result = "…"

        while low <= high:

            middle = (
                low + high
            ) // 2

            candidate = (
                text[:middle].rstrip()
                + "…"
            )

            try:

                width = draw.textbbox(
                    (0, 0),
                    candidate,
                    font=font,
                )[2]

                if width <= max_width:

                    result = candidate
                    low = middle + 1

                else:
                    high = middle - 1

            except Exception:
                break

        return result

    # ========================================================
    # GENERATE THUMBNAIL
    # ========================================================

    async def generate(
        self,
        song: Track,
    ):

        temp_path = None

        try:

            os.makedirs(
                "cache",
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

                song_id = (
                    getattr(
                        song,
                        "vidid",
                        None,
                    )
                    or getattr(
                        song,
                        "videoid",
                        None,
                    )
                    or "unknown"
                )

            song_id = str(
                song_id
            )

            song_id = "".join(
                char
                if char.isalnum()
                or char in "-_"
                else "_"
                for char in song_id
            )

            temp_path = (
                f"cache/temp_{song_id}.jpg"
            )

            final_path = (
                f"cache/{song_id}.png"
            )

            if os.path.exists(
                final_path
            ):
                return final_path

            # ------------------------------------------------
            # THUMB URL
            # ------------------------------------------------

            thumb_url = getattr(
                song,
                "thumbnail",
                None,
            )

            if not thumb_url:

                thumb_url = getattr(
                    song,
                    "thumb",
                    None,
                )

            if not thumb_url:

                return getattr(
                    config,
                    "DEFAULT_THUMB",
                    "",
                )

            await self.save_thumb(
                temp_path,
                thumb_url,
            )

            # ------------------------------------------------
            # OPEN IMAGE
            # ------------------------------------------------

            try:

                if not os.path.exists(
                    temp_path
                ):
                    raise FileNotFoundError(
                        "Thumbnail not downloaded"
                    )

                source = Image.open(
                    temp_path
                ).convert("RGBA")

            except Exception:

                source = Image.new(
                    "RGBA",
                    self.size,
                    (30, 30, 30, 255),
                )

            width, height = self.size

            # =================================================
            # BLURRED BACKGROUND
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
                self.size,
                Image.Resampling.LANCZOS,
            )

            background = background.filter(
                ImageFilter.GaussianBlur(25)
            )

            dark_overlay = Image.new(
                "RGBA",
                self.size,
                (0, 0, 0, 100),
            )

            background = Image.alpha_composite(
                background,
                dark_overlay,
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
                        self.size,
                        Image.Resampling.LANCZOS,
                    )

                    template_array = np.array(
                        template
                    ).astype(float)

                    red = template_array[:, :, 0]
                    green = template_array[:, :, 1]
                    blue = template_array[:, :, 2]

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

                    template_array[:, :, 3] = alpha

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
                        "⚠️ Template error: "
                        f"{e}"
                    )

            # =================================================
            # COVER
            # =================================================

            cover_x = 100
            cover_y = 104

            cover_width = 512
            cover_height = 512

            radius = 38

            shadow = Image.new(
                "RGBA",
                self.size,
                (0, 0, 0, 0),
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
                radius=radius + 4,
                fill=(0, 0, 0, 140),
            )

            shadow = shadow.filter(
                ImageFilter.GaussianBlur(18)
            )

            background = Image.alpha_composite(
                background,
                shadow,
            )

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
                radius=radius,
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
            # CHANNEL / ARTIST
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

            bbox = draw.textbbox(
                (0, 0),
                brand,
                font=self.tag_font,
            )

            brand_width = (
                bbox[2] - bbox[0]
            )

            brand_height = (
                bbox[3] - bbox[1]
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

            # Shadow
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
            # CLEAN TEMP
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

            return getattr(
                config,
                "DEFAULT_THUMB",
                "",
            )


# ============================================================
# GLOBAL INSTANCE
# ============================================================

thumb = Thumbnail()
thumbnail = thumb
