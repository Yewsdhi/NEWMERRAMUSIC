# -----------------------------------------------
# 🔸 ShashankMusic Project
# 🔹 Developed & Maintained by: Shashank Shukla
# 📅 Copyright © 2025 – All Rights Reserved
# 💖 White + Pink Premium Thumbnail System
# -----------------------------------------------

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


def trim_to_width(text: str, font, max_width: int) -> str:
    ellipsis = "..."

    if font.getlength(text) <= max_width:
        return text

    for i in range(len(text), 0, -1):
        new_text = text[:i] + ellipsis

        if font.getlength(new_text) <= max_width:
            return new_text

    return ellipsis


async def get_thumb(videoid: str, player_username: str = None) -> str:
    if player_username is None:
        player_username = app.username

    cache_path = os.path.join(
        CACHE_DIR,
        f"{videoid}_pink.png"
    )

    if os.path.exists(cache_path):
        return cache_path

    # ---------------------------------- #
    # FETCH YOUTUBE DATA
    # ---------------------------------- #

    try:
        results = VideosSearch(
            f"https://www.youtube.com/watch?v={videoid}",
            limit=1
        )

        search = await results.next()
        data = search.get("result", [])[0]

        title = data.get("title", "Unknown Title")

        artist = data.get(
            "channel",
            {}
        ).get(
            "name",
            "Unknown Artist"
        )

        duration = data.get(
            "duration",
            "00:00"
        )

        views = data.get(
            "viewCount",
            {}
        ).get(
            "short",
            "0 views"
        )

        thumbnail = data.get(
            "thumbnails",
            [{}]
        )[0].get(
            "url",
            YOUTUBE_IMG_URL
        )

    except Exception:
        title = "Unknown Title"
        artist = "Unknown Artist"
        duration = "00:00"
        views = "0 views"
        thumbnail = YOUTUBE_IMG_URL

    # ---------------------------------- #
    # DOWNLOAD THUMBNAIL
    # ---------------------------------- #

    thumb_path = os.path.join(
        CACHE_DIR,
        f"raw_{videoid}.jpg"
    )

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:

                if resp.status == 200:
                    async with aiofiles.open(
                        thumb_path,
                        "wb"
                    ) as f:
                        await f.write(await resp.read())
                else:
                    return YOUTUBE_IMG_URL

    except Exception:
        return YOUTUBE_IMG_URL

    # ---------------------------------- #
    # IMAGE SETUP
    # ---------------------------------- #

    W, H = 1280, 720

    img = Image.open(thumb_path).convert("RGBA")

    bg = img.resize((W, H))

    bg = bg.filter(
        ImageFilter.GaussianBlur(radius=35)
    )

    bg = ImageEnhance.Brightness(bg).enhance(0.9)

    # White overlay
    white_layer = Image.new(
        "RGBA",
        (W, H),
        (255, 255, 255, 255)
    )

    bg = Image.blend(
        bg,
        white_layer,
        0.55
    )

    bg = bg.filter(
        ImageFilter.GaussianBlur(2)
    )

    draw = ImageDraw.Draw(bg)

    # ---------------------------------- #
    # FONTS
    # ---------------------------------- #

    try:
        bold_font = "ShiviMusic/assets/font2.ttf"
        medium_font = "ShiviMusic/assets/font.ttf"

        title_font = ImageFont.truetype(
            bold_font,
            62
        )

        artist_font = ImageFont.truetype(
            medium_font,
            38
        )

        small_font = ImageFont.truetype(
            medium_font,
            30
        )

    except Exception:
        title_font = ImageFont.load_default()
        artist_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # ---------------------------------- #
    # ALBUM FRAME
    # ---------------------------------- #

    frame_w = 460
    frame_h = 460

    frame_x = 90
    frame_y = (H - frame_h) // 2

    album = img.resize(
        (frame_w, frame_h),
        Image.LANCZOS
    )

    mask = Image.new(
        "L",
        (frame_w, frame_h),
        0
    )

    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, frame_w, frame_h),
        radius=40,
        fill=255
    )

    # ---------------------------------- #
    # PINK GLOW
    # ---------------------------------- #

    glow = Image.new(
        "RGBA",
        (frame_w + 140, frame_h + 140),
        (0, 0, 0, 0)
    )

    glow_draw = ImageDraw.Draw(glow)

    glow_draw.rounded_rectangle(
        (50, 50, frame_w + 90, frame_h + 90),
        radius=55,
        outline=(255, 20, 147, 255),
        width=14
    )

    glow = glow.filter(
        ImageFilter.GaussianBlur(25)
    )

    bg.paste(
        glow,
        (frame_x - 70, frame_y - 70),
        glow
    )

    bg.paste(
        album,
        (frame_x, frame_y),
        mask
    )

    # White border
    draw.rounded_rectangle(
        (
            frame_x,
            frame_y,
            frame_x + frame_w,
            frame_y + frame_h
        ),
        radius=40,
        outline=(255, 255, 255),
        width=6
    )

    # ---------------------------------- #
    # GLASS PANEL
    # ---------------------------------- #

    panel_x = 610

    glass = Image.new(
        "RGBA",
        (W, H),
        (0, 0, 0, 0)
    )

    glass_draw = ImageDraw.Draw(glass)

    glass_draw.rounded_rectangle(
        (
            panel_x - 40,
            frame_y,
            W - 70,
            frame_y + frame_h
        ),
        radius=35,
        fill=(255, 255, 255, 85)
    )

    bg = Image.alpha_composite(bg, glass)

    draw = ImageDraw.Draw(bg)

    # ---------------------------------- #
    # TITLE
    # ---------------------------------- #

    clean_title = trim_to_width(
        title,
        title_font,
        560
    )

    # Pink glow text
    for offset in range(8, 0, -2):
        draw.text(
            (
                panel_x + offset,
                frame_y + 35 + offset
            ),
            clean_title,
            font=title_font,
            fill=(255, 105, 180, 40)
        )

    draw.text(
        (panel_x, frame_y + 35),
        clean_title,
        font=title_font,
        fill=(255, 20, 147)
    )

    # ---------------------------------- #
    # ARTIST
    # ---------------------------------- #

    clean_artist = trim_to_width(
        f"By {artist}",
        artist_font,
        520
    )

    draw.text(
        (panel_x, frame_y + 125),
        clean_artist,
        font=artist_font,
        fill=(255, 105, 180)
    )

    # ---------------------------------- #
    # VIEWS
    # ---------------------------------- #

    draw.text(
        (panel_x, frame_y + 190),
        f"Views : {views}",
        font=small_font,
        fill=(255, 105, 180)
    )

    # ---------------------------------- #
    # PLAYER BAR
    # ---------------------------------- #

    bar_x = panel_x
    bar_y = frame_y + 320

    bar_w = 500
    bar_h = 12

    draw.rounded_rectangle(
        (
            bar_x,
            bar_y,
            bar_x + bar_w,
            bar_y + bar_h
        ),
        radius=20,
        fill=(255, 255, 255, 120)
    )

    progress = 0.45

    draw.rounded_rectangle(
        (
            bar_x,
            bar_y,
            bar_x + int(bar_w * progress),
            bar_y + bar_h
        ),
        radius=20,
        fill=(255, 20, 147)
    )

    # Progress circle
    cx = bar_x + int(bar_w * progress)

    draw.ellipse(
        (
            cx - 13,
            bar_y - 8,
            cx + 13,
            bar_y + 18
        ),
        fill=(255, 20, 147)
    )

    # ---------------------------------- #
    # TIME TEXT
    # ---------------------------------- #

    draw.text(
        (bar_x, bar_y + 28),
        "00:25",
        font=small_font,
        fill=(255, 20, 147)
    )

    draw.text(
        (bar_x + bar_w - 90, bar_y + 28),
        duration,
        font=small_font,
        fill=(255, 20, 147)
    )

    # ---------------------------------- #
    # SAVE IMAGE
    # ---------------------------------- #

    bg = bg.convert("RGB")

    bg.save(
        cache_path,
        quality=95
    )

    # ---------------------------------- #
    # CLEANUP
    # ---------------------------------- #

    try:
        os.remove(thumb_path)

    except Exception:
        pass

    return cache_path
