import os
import aiohttp
import aiofiles

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


def trim_to_width(text: str, font, max_width: int):
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
        f"{videoid}_pink_player.png"
    )

    if os.path.exists(cache_path):
        return cache_path

    # ================= VIDEO INFO ================= #

    try:
        results = VideosSearch(
            f"https://www.youtube.com/watch?v={videoid}",
            limit=1
        )

        search_result = await results.next()

        data = search_result.get("result", [])[0]

        title = data.get("title", "Unknown Title")

        artist = data.get(
            "channel",
            {}
        ).get(
            "name",
            "Unknown Artist"
        )

        duration = data.get("duration", "03:00")

        views = data.get(
            "viewCount",
            {}
        ).get(
            "short",
            "0 Views"
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
        duration = "03:00"
        views = "0 Views"
        thumbnail = YOUTUBE_IMG_URL

    # ================= DOWNLOAD THUMB ================= #

    thumb_path = os.path.join(
        CACHE_DIR,
        f"raw_{videoid}.jpg"
    )

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as response:

                if response.status == 200:
                    async with aiofiles.open(
                        thumb_path,
                        "wb"
                    ) as f:
                        await f.write(
                            await response.read()
                        )

    except:
        return YOUTUBE_IMG_URL

    # ================= MAIN SIZE ================= #

    WIDTH = 1280
    HEIGHT = 720

    img = Image.open(thumb_path).convert("RGBA")

    # ================= BACKGROUND ================= #

    bg = img.resize((WIDTH, HEIGHT))

    bg = bg.filter(
        ImageFilter.GaussianBlur(40)
    )

    dark = Image.new(
        "RGBA",
        (WIDTH, HEIGHT),
        (0, 0, 0, 155)
    )

    bg = Image.alpha_composite(bg, dark)

    enhancer = ImageEnhance.Brightness(bg)

    bg = enhancer.enhance(0.70)

    draw = ImageDraw.Draw(bg)

    # ================= FONTS ================= #

    try:
        title_font = ImageFont.truetype(
            "ShiviMusic/assets/font2.ttf",
            60
        )

        artist_font = ImageFont.truetype(
            "ShiviMusic/assets/font.ttf",
            36
        )

        small_font = ImageFont.truetype(
            "ShiviMusic/assets/font.ttf",
            28
        )

        logo_font = ImageFont.truetype(
            "ShiviMusic/assets/font2.ttf",
            30
        )

    except:
        title_font = ImageFont.load_default()
        artist_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
        logo_font = ImageFont.load_default()

    # ================= ALBUM IMAGE ================= #

    album_size = 430

    album_x = 90
    album_y = (HEIGHT - album_size) // 2

    album = img.resize(
        (album_size, album_size),
        Image.LANCZOS
    )

    mask = Image.new(
        "L",
        (album_size, album_size),
        0
    )

    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, album_size, album_size),
        radius=45,
        fill=255
    )

    # ================= PINK NEON GLOW ================= #

    glow = Image.new(
        "RGBA",
        (album_size + 120, album_size + 120),
        (0, 0, 0, 0)
    )

    gdraw = ImageDraw.Draw(glow)

    # OUTER GLOW
    gdraw.rounded_rectangle(
        (
            20,
            20,
            album_size + 100,
            album_size + 100
        ),
        radius=60,
        fill=(255, 0, 140, 90)
    )

    # MIDDLE GLOW
    gdraw.rounded_rectangle(
        (
            35,
            35,
            album_size + 85,
            album_size + 85
        ),
        radius=55,
        fill=(255, 30, 180, 130)
    )

    # INNER GLOW
    gdraw.rounded_rectangle(
        (
            45,
            45,
            album_size + 75,
            album_size + 75
        ),
        radius=50,
        fill=(255, 140, 220, 170)
    )

    glow = glow.filter(
        ImageFilter.GaussianBlur(30)
    )

    bg.paste(
        glow,
        (album_x - 60, album_y - 60),
        glow
    )

    # ================= PASTE IMAGE ================= #

    bg.paste(
        album,
        (album_x, album_y),
        mask
    )

    # ================= MAIN BORDER ================= #

    draw.rounded_rectangle(
        (
            album_x,
            album_y,
            album_x + album_size,
            album_y + album_size
        ),
        radius=45,
        outline=(255, 80, 210, 255),
        width=10
    )

    # SECOND BORDER
    draw.rounded_rectangle(
        (
            album_x - 5,
            album_y - 5,
            album_x + album_size + 5,
            album_y + album_size + 5
        ),
        radius=50,
        outline=(255, 180, 240, 180),
        width=3
    )

    # ================= GLASS PANEL ================= #

    panel_x = 590
    panel_y = album_y

    panel_w = 610
    panel_h = album_size

    overlay = Image.new(
        "RGBA",
        (WIDTH, HEIGHT),
        (0, 0, 0, 0)
    )

    odraw = ImageDraw.Draw(overlay)

    odraw.rounded_rectangle(
        (
            panel_x,
            panel_y,
            panel_x + panel_w,
            panel_y + panel_h
        ),
        radius=35,
        fill=(255, 255, 255, 20),
        outline=(255, 120, 220, 180),
        width=3
    )

    overlay = overlay.filter(
        ImageFilter.GaussianBlur(1)
    )

    bg = Image.alpha_composite(bg, overlay)

    # ================= NOW PLAYING ================= #

    draw.text(
        (panel_x + 40, panel_y + 15),
        "NOW PLAYING",
        font=small_font,
        fill=(255, 120, 220, 255)
    )

    # ================= SONG TITLE ================= #

    clean_title = trim_to_width(
        title,
        title_font,
        520
    )

    # SHADOW
    draw.text(
        (panel_x + 44, panel_y + 49),
        clean_title,
        font=title_font,
        fill=(0, 0, 0, 180)
    )

    # MAIN TITLE
    draw.text(
        (panel_x + 40, panel_y + 45),
        clean_title,
        font=title_font,
        fill=(255, 255, 255, 255)
    )

    # ================= ARTIST ================= #

    clean_artist = trim_to_width(
        f"By {artist}",
        artist_font,
        500
    )

    draw.text(
        (panel_x + 40, panel_y + 145),
        clean_artist,
        font=artist_font,
        fill=(255, 170, 230, 255)
    )

    # ================= VIEWS ================= #

    draw.text(
        (panel_x + 40, panel_y + 210),
        f"Views : {views}",
        font=small_font,
        fill=(255, 200, 240, 220)
    )

    # ================= PROGRESS BAR ================= #

    bar_x = panel_x + 40
    bar_y = panel_y + 320

    bar_width = 480
    bar_height = 10

    # BACK BAR
    draw.rounded_rectangle(
        (
            bar_x,
            bar_y,
            bar_x + bar_width,
            bar_y + bar_height
        ),
        radius=10,
        fill=(255, 255, 255, 70)
    )

    progress = 0.42

    # MAIN BAR
    draw.rounded_rectangle(
        (
            bar_x,
            bar_y,
            bar_x + int(bar_width * progress),
            bar_y + bar_height
        ),
        radius=10,
        fill=(255, 50, 180, 255)
    )

    # SLIDER
    slider_x = bar_x + int(bar_width * progress)

    draw.ellipse(
        (
            slider_x - 12,
            bar_y - 7,
            slider_x + 12,
            bar_y + 17
        ),
        fill=(255, 255, 255, 255)
    )

    # ================= TIME ================= #

    draw.text(
        (bar_x, bar_y + 28),
        "00:25",
        font=small_font,
        fill=(255, 255, 255, 220)
    )

    draw.text(
        (bar_x + bar_width - 80, bar_y + 28),
        duration,
        font=small_font,
        fill=(255, 255, 255, 220)
    )

    # ================= PLAYER INFO ================= #

    player_text = f"Powered By {player_username}"

    draw.text(
        (panel_x + 40, panel_y + 385),
        player_text,
        font=logo_font,
        fill=(255, 120, 220, 255)
    )

    # ================= SAVE ================= #

    bg = bg.convert("RGB")

    bg.save(
        cache_path,
        quality=95
    )

    # ================= REMOVE TEMP ================= #

    try:
        os.remove(thumb_path)
    except:
        pass

    return cache_path
