import os
import aiohttp
import aiofiles
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from py_yt import VideosSearch
from config import YOUTUBE_IMG_URL

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)


async def spotify_thumb(videoid):

    cache = f"{CACHE_DIR}/{videoid}_spotify.png"
    if os.path.exists(cache):
        return cache

    try:
        search = VideosSearch(
            f"https://www.youtube.com/watch?v={videoid}",
            limit=1
        )

        data = (await search.next())["result"][0]

        title = data["title"]
        thumb = data["thumbnails"][0]["url"]
        duration = data.get("duration", "Unknown")
        views = data.get("viewCount", {}).get("short", "0")

    except:
        title = "Unknown Song"
        thumb = YOUTUBE_IMG_URL
        duration = "0:00"
        views = "0"

    thumb_path = f"{CACHE_DIR}/yt_{videoid}.png"

    async with aiohttp.ClientSession() as session:
        async with session.get(thumb) as r:
            if r.status == 200:
                async with aiofiles.open(thumb_path, "wb") as f:
                    await f.write(await r.read())

    # ---------------- BG ---------------- #

    bg = Image.new("RGB", (1280, 720), (15, 20, 18))

    overlay = Image.new("RGBA", (1280, 720), (0, 255, 120, 40))
    bg = Image.alpha_composite(bg.convert("RGBA"), overlay)

    # ---------------- ALBUM COVER ---------------- #

    album = Image.open(thumb_path).resize((420, 420)).convert("RGBA")

    mask = Image.new("L", (420, 420), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.rounded_rectangle((0,0,420,420), 40, fill=255)

    album_round = Image.new("RGBA",(420,420))
    album_round.paste(album,(0,0),mask)

    bg.paste(album_round,(120,150),album_round)

    draw = ImageDraw.Draw(bg)

    # ---------------- FONTS ---------------- #

    try:
        title_font = ImageFont.truetype("ShiviMusic/assets/font.ttf",48)
        meta_font = ImageFont.truetype("ShiviMusic/assets/font.ttf",28)
    except:
        title_font = meta_font = ImageFont.load_default()

    # ---------------- TITLE ---------------- #

    draw.text(
        (620,220),
        title[:40],
        fill=(255,255,255),
        font=title_font
    )

    meta = f"Views : {views}\nDuration : {duration}"

    draw.multiline_text(
        (620,300),
        meta,
        fill=(200,200,200),
        spacing=8,
        font=meta_font
    )

    # ---------------- PROGRESS BAR ---------------- #

    bar_x = 620
    bar_y = 420
    bar_w = 420

    draw.rounded_rectangle(
        (bar_x,bar_y,bar_x+bar_w,bar_y+14),
        8,
        fill=(70,70,70)
    )

    draw.rounded_rectangle(
        (bar_x,bar_y,bar_x+bar_w//2,bar_y+14),
        8,
        fill=(30,215,96)
    )

    # ---------------- SPOTIFY LOGO STYLE ---------------- #

    draw.text(
        (620,470),
        "Spotify Style Player",
        fill=(30,215,96),
        font=meta_font
    )

    draw.text(
        (1050,680),
        "BADNAM OP",
        fill=(255,255,255),
        font=meta_font
    )

    bg.save(cache)

    os.remove(thumb_path)

    return cache
