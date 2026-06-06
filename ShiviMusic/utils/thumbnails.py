import asyncio
import logging
import os
from io import BytesIO

import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

from anony import config
from anony.helpers._dataclass import Track

LOGGER = logging.getLogger(__name__)

# File paths aur fixed dimensions
CONTROLS_IMAGE_PATH = "anony/helpers/trashed-1781345124-controls.png"
YOUTUBE_IMG_URL = "https://i.ytimg.com/vi/default.jpg"
CANVAS_SIZE = (1280, 720)
ALBUM_ART_SIZE = (512, 512)

def _load_fonts():
    try:
        return {
            "title": ImageFont.truetype("anony/helpers/font.ttf", 44),       
            "subtitle": ImageFont.truetype("anony/helpers/cfont.ttf", 26),    
        }
    except Exception as e:
        LOGGER.error("Font loading error: %s, using default fonts", e)
        return {
            "title": ImageFont.load_default(),
            "subtitle": ImageFont.load_default(),
        }

FONTS = _load_fonts()


def _clean_text(text: str, limit: int = 24) -> str:
    if not text:
        return "Unknown"
    text = text.strip()
    return f"{text[:limit]}..." if len(text) > limit else text


async def _process_background(img: Image.Image) -> Image.Image:
    """Perfect background: Blur thoda kam kiya aur brightness badhayi taaki thumbnail thoda dikhe"""
    bg = ImageOps.fit(img, CANVAS_SIZE, Image.Resampling.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(radius=22))  # Moderate blur taaki pic pehchan me aaye
    bg = ImageEnhance.Brightness(bg).enhance(0.42)       # Brightness badha di taaki peeche ka look visible ho
    return bg


def _create_card_shadow(size: tuple, radius: int, border_blur: int = 15) -> Image.Image:
    """Card ke peeche soft glow/shadow effect banane ke liye mask function"""
    # Card ke size se thoda bada canvas banate hain shadow ke liye
    shadow_size = (size[0] + border_blur * 2, size[1] + border_blur * 2)
    shadow = Image.new("RGBA", shadow_size, (0, 0, 0, 0))
    
    # Shadow ka kala ya dark colored layer draw karna
    draw = ImageDraw.Draw(shadow)
    draw.rounded_rectangle(
        (border_blur, border_blur, border_blur + size[0], border_blur + size[1]), 
        radius=radius, 
        fill=(0, 0, 0, 160) # Opacity balanced for soft glow
    )
    
    # Blur filter se edge ko smooth aur glowing banana
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=border_blur))
    return shadow


async def _fetch_image(session: aiohttp.ClientSession, url: str) -> Image.Image:
    try:
        if not url:
            raise ValueError("No thumbnail URL")
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
            resp.raise_for_status()
            return Image.open(BytesIO(await resp.read())).convert("RGBA")
    except Exception as e:
        LOGGER.error("Image fetch error for %s: %s", url, e)

    try:
        async with session.get(YOUTUBE_IMG_URL, timeout=aiohttp.ClientTimeout(total=5)) as resp:
            resp.raise_for_status()
            return Image.open(BytesIO(await resp.read())).convert("RGBA")
    except Exception as fallback_err:
        LOGGER.error("YouTube fallback error: %s", fallback_err)

    return Image.new("RGBA", CANVAS_SIZE, (30, 30, 30, 255))


def _make_rounded_thumbnail(image: Image.Image, size: tuple) -> Image.Image:
    thumb = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size[0], size[1]), radius=36, fill=255)
    thumb.putalpha(mask)
    return thumb


class Thumbnail:
    def __init__(self):
        self.session: aiohttp.ClientSession | None = None

    async def start(self) -> None:
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        if self.session:
            await self.session.close()
            self.session = None

    async def generate(self, song: Track) -> str:
        try:
            os.makedirs("cache", exist_ok=True)
            output = f"cache/{song.id}.png"
            if os.path.exists(output):
                return output

            # 1. Metatdata management
            thumbnail_url = (song.thumbnail or "").split("?")[0]
            title = _clean_text(song.title or "Unknown Title", limit=24)
            artist = _clean_text(song.channel_name or "Unknown Artist", limit=28)

            # 2. Basic layers loading
            raw_thumb = await _fetch_image(self.session, thumbnail_url)
            bg = await _process_background(raw_thumb)
            album_art = _make_rounded_thumbnail(raw_thumb, ALBUM_ART_SIZE)

            # 3. Shadow effect handling (Main poster ke peeche paste hoga)
            shadow_blur = 18
            shadow_img = _create_card_shadow(ALBUM_ART_SIZE, radius=36, border_blur=shadow_blur)
            # Offset mapping taaki shadow center se generate ho
            bg.paste(shadow_img, (95 - shadow_blur, 104 - shadow_blur), shadow_img)

            # 4. Front Album Art Paste
            bg.paste(album_art, (95, 104), album_art)

            # 5. Right Side Content Mapping
            draw = ImageDraw.Draw(bg)
            draw.text((675, 130), title, fill=(255, 255, 255, 255), font=FONTS["title"])
            draw.text((675, 202), artist, fill=(180, 180, 180, 255), font=FONTS["subtitle"])

            # 6. Player UI Control Block
            try:
                if os.path.exists(CONTROLS_IMAGE_PATH):
                    controls = Image.open(CONTROLS_IMAGE_PATH).convert("RGBA")
                    
                    target_width = 540
                    aspect_ratio = controls.width / controls.height
                    target_height = int(target_width / aspect_ratio)
                    
                    controls_resized = controls.resize((target_width, target_height), Image.Resampling.LANCZOS)
                    bg.paste(controls_resized, (660, 270), controls_resized)
                    
                    controls.close()
                    controls_resized.close()
            except Exception as ctrl_err:
                LOGGER.error("Controls bar drawing glitch: %s", ctrl_err)

            # Final rendering enhancements
            bg = ImageEnhance.Contrast(bg).enhance(1.06)
            bg = ImageEnhance.Color(bg).enhance(1.08)

            # Stream save execution
            await asyncio.to_thread(bg.save, output, format="PNG", optimize=True)

            # Garbage Collection
            raw_thumb.close()
            album_art.close()
            shadow_img.close()
            bg.close()

            return output if os.path.exists(output) else config.DEFAULT_THUMB

        except Exception as e:
            LOGGER.error("Thumbnail pipeline failed execution: %s", e)
            return config.DEFAULT_THUMB
