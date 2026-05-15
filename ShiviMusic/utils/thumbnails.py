import os
import aiofiles
import aiohttp

from PIL import (
    Image,
    ImageDraw,
    ImageEnhance,
    ImageFilter,
    ImageFont
)

from py_yt import VideosSearch

from config import YOUTUBE_IMG_URL
from ShiviMusic import app

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)


def trim_to_width(text, font, max_width):
    ellipsis = "..."

    if font.getlength(text) <= max_width:
        return text

    for i in range(len(text), 0, -1):
        new_text = text[:i] + ellipsis

        if font.getlength(new_text) <= max_width:
            return new_text

    return ellipsis


async def get_thumb(videoid: str, player_username: str = None):

    if player_username is None:
        player_username = app.username

    cache_path = os.path.join(
        CACHE_DIR,
        f"{videoid}_premium.png"
    )

    if os.path.exists(cache_path):
        return cache_path

    # ================= DEFAULT VALUES ================= #

    title = "Unknown Title"
    artist = "Unknown Artist"
    duration = "00:00"
    views = "0 Views"
    thumbnail = YOUTUBE_IMG_URL

    # ================= FETCH YOUTUBE DATA ================= #

    try:
        results = VideosSearch(
            f"https://www.youtube.com/watch?v={videoid}",
            limit=1
        )

        data = (await results.next())["result"][0]

        title = data.get("title", title)

        artist = (
            data.get("channel", {})
            .get("name", artist)
        )

        duration = data.get("duration", duration)

        views = (
            data.get("viewCount", {})
            .get("short", views)
        )

        thumbnail = (
            data.get("thumbnails", [{}])[0]
            .get("url", thumbnail)
        )

    except Exception as e:
        print(f"YT SEARCH ERROR : {e}")

    # ================= DOWNLOAD THUMBNAIL ================= #

    thumb_path = os.path.join(
        CACHE_DIR,
        f"{videoid}.jpg"
    )

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as response:

                if response.status != 200:
                    return None

                async with aiofiles.open(
                    thumb_path,
                    "wb"
                ) as f:
                    await f.write(await response.read())

    except Exception as e:
        print(f"THUMB DOWNLOAD ERROR : {e}")
        return None

    # ================= OPEN IMAGE ================= #

    try:
        img = Image.open(thumb_path).convert("RGBA")

    except Exception as e:
        print(f"IMAGE OPEN ERROR : {e}")
        return None

    # ================= CANVAS ================= #

    W, H = 1280, 720

    bg = img.resize((W, H))

    bg = bg.filter(
        ImageFilter.GaussianBlur(radius=45)
    )

    bg = ImageEnhance.Brightness(bg).enhance(0.32)

    draw = ImageDraw.Draw(bg)

    # ================= FONTS ================= #

    try:
        title_font = ImageFont.truetype(
            "ShiviMusic/assets/font2.ttf",
            58
        )

        artist_font = ImageFont.truetype(
            "ShiviMusic/assets/font.ttf",
            38
        )

        small_font = ImageFont.truetype(
            "ShiviMusic/assets/font.ttf",
            30
        )

    except:
        title_font = artist_font = small_font = (
            ImageFont.load_default()
        )

    # ===================================================== #
    #                PREMIUM MODERN ALBUM FRAME             #
    # ===================================================== #

    frame_w = 450
    frame_h = 450

    frame_x = 100
    frame_y = (H - frame_h) // 2

    album = img.resize(
        (frame_w, frame_h),
        Image.LANCZOS
    )

    # ================= ROUNDED MASK ================= #

    mask = Image.new(
        "L",
        (frame_w, frame_h),
        0
    )

    mask_draw = ImageDraw.Draw(mask)

    mask_draw.rounded_rectangle(
        (0, 0, frame_w, frame_h),
        radius=45,
        fill=255
    )

    # ================= SHADOW ================= #

    shadow = Image.new(
        "RGBA",
        (frame_w + 100, frame_h + 100),
        (0, 0, 0, 0)
    )

    shadow_draw = ImageDraw.Draw(shadow)

    shadow_draw.rounded_rectangle(
        (50, 50, frame_w + 50, frame_h + 50),
        radius=55,
        fill=(0, 0, 0, 180)
    )

    shadow = shadow.filter(
        ImageFilter.GaussianBlur(30)
    )

    bg.paste(
        shadow,
        (frame_x - 50, frame_y - 50),
        shadow
    )

    # ================= NEON BORDER ================= #

    border = Image.new(
        "RGBA",
        (frame_w + 40, frame_h + 40),
        (0, 0, 0, 0)
    )

    border_draw = ImageDraw.Draw(border)

    # Outer Green Glow

    border_draw.rounded_rectangle(
        (8, 8, frame_w + 32, frame_h + 32),
        radius=55,
        outline=(120, 255, 0, 180),
        width=14
    )

    # Yellow Main Border

    border_draw.rounded_rectangle(
        (16, 16, frame_w + 24, frame_h + 24),
        radius=48,
        outline=(255, 220, 0, 255),
        width=6
    )

    border = border.filter(
        ImageFilter.GaussianBlur(4)
    )

    bg.paste(
        border,
        (frame_x - 20, frame_y - 20),
        border
    )

    # ================= MAIN IMAGE ================= #

    bg.paste(
        album,
        (frame_x, frame_y),
        mask
    )

    # ================= GLOSS EFFECT ================= #

    gloss = Image.new(
        "RGBA",
        (frame_w, frame_h),
        (255, 255, 255, 0)
    )

    gloss_draw = ImageDraw.Draw(gloss)

    gloss_draw.rounded_rectangle(
        (0, 0, frame_w, frame_h // 2),
        radius=45,
        fill=(255, 255, 255, 35)
    )

    gloss = gloss.filter(
        ImageFilter.GaussianBlur(18)
    )

    bg.paste(
        gloss,
        (frame_x, frame_y),
        gloss
    )

    # ================= GLASS PANEL ================= #

    text_x = 620

    overlay = Image.new(
        "RGBA",
        (W, H),
        (0, 0, 0, 0)
    )

    overlay_draw = ImageDraw.Draw(overlay)

    overlay_draw.rounded_rectangle(
        (
            text_x - 40,
            frame_y,
            W - 60,
            frame_y + frame_h
        ),
        radius=35,
        fill=(255, 255, 255, 22)
    )

    bg.alpha_composite(overlay)

    # ================= TEXT ================= #

    clean_title = trim_to_width(
        title,
        title_font,
        560
    )

    draw.text(
        (text_x, frame_y + 40),
        clean_title,
        font=title_font,
        fill=(255, 255, 255)
    )

    clean_artist = trim_to_width(
        f"By {artist}",
        artist_font,
        520
    )

    draw.text(
        (text_x, frame_y + 130),
        clean_artist,
        font=artist_font,
        fill=(210, 210, 210)
    )

    draw.text(
        (text_x, frame_y + 200),
        f"Views : {views}",
        font=small_font,
        fill=(180, 180, 180)
    )

    # ================= PLAYER BAR ================= #

    bar_x = text_x
    bar_y = frame_y + 320

    bar_width = 500
    bar_height = 10

    draw.rounded_rectangle(
        (
            bar_x,
            bar_y,
            bar_x + bar_width,
            bar_y + bar_height
        ),
        radius=10,
        fill=(255, 255, 255, 60)
    )

    progress = 0.45

    draw.rounded_rectangle(
        (
            bar_x,
            bar_y,
            bar_x + (bar_width * progress),
            bar_y + bar_height
        ),
        radius=10,
        fill=(120, 255, 0)
    )

    circle_x = bar_x + (bar_width * progress)

    draw.ellipse(
        (
            circle_x - 12,
            bar_y - 7,
            circle_x + 12,
            bar_y + 17
        ),
        fill=(255, 255, 255)
    )

    draw.text(
        (bar_x, bar_y + 30),
        "00:25",
        font=small_font,
        fill=(255, 255, 255)
    )

    draw.text(
        (bar_x + bar_width - 90, bar_y + 30),
        duration,
        font=small_font,
        fill=(255, 255, 255)
    )

    # ================= PLAYER USERNAME ================= #

    draw.text(
        (text_x, frame_y + 410),
        f"@{player_username}",
        font=small_font,
        fill=(120, 255, 0)
    )

    # ================= SAVE FINAL ================= #

    bg = bg.convert("RGB")

    bg.save(
        cache_path,
        quality=95
    )

    # ================= CLEANUP ================= #

    try:
        os.remove(thumb_path)
    except:
        pass

    return cache_path
