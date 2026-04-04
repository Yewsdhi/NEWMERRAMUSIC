import os
import re
import math
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageFont
from py_yt import VideosSearch
from config import YOUTUBE_IMG_URL
from ShiviMusic import app

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

W, H = 1280, 720

BG_ORANGE = (254, 155, 51)
RAY_DARK = (255, 140, 25)
CARD_WHITE = (255, 251, 239)
SHADOW_COLOR = (0, 0, 0)

CARD_X, CARD_Y = 720, 110
CARD_R, CARD_B = 1200, 590
CARD_BORDER_W = 6
SHADOW_OFFSET = 18


def trim_to_width(text, font, max_w):
    ellipsis = "…"
    while True:
        if font.getlength(text) <= max_w:
            return text
        text = text[:-1]
        if len(text) <= 1:
            return ellipsis


def _sunburst_thumb(raw, title, channel, duration, player, out):

    bg = Image.new("RGB", (W, H), BG_ORANGE)
    draw = ImageDraw.Draw(bg)

    cx, cy = W // 2, H // 2
    R = max(W, H) * 1.5

    for i in range(30):
        a0 = math.radians(i * 12)
        a1 = math.radians((i + 1) * 12)

        pts = [
            (cx, cy),
            (cx + R * math.cos(a0), cy + R * math.sin(a0)),
            (cx + R * math.cos(a1), cy + R * math.sin(a1)),
        ]

        draw.polygon(pts, fill=RAY_DARK if i % 2 else BG_ORANGE)

    # Fonts
    try:
        f_title = ImageFont.truetype("ShiviMusic/assets/font.ttf", 80)
        f_meta = ImageFont.truetype("ShiviMusic/assets/font.ttf", 36)
        f_small = ImageFont.truetype("ShiviMusic/assets/font.ttf", 28)
    except:
        f_title = f_meta = f_small = ImageFont.load_default()

    # Text
    draw.text((60, 200), trim_to_width(title, f_title, 600), fill=(0, 0, 0), font=f_title)
    draw.text((60, 300), f"Channel: {channel}", fill=(0, 0, 0), font=f_meta)
    draw.text((60, 350), f"Player: @{player}", fill=(0, 0, 0), font=f_meta)

    # Progress bar
    draw.rounded_rectangle((80, 480, 600, 500), 10, fill=(220, 220, 220))
    draw.rounded_rectangle((80, 480, 340, 500), 10, fill=(0, 0, 0))

    draw.text((80, 510), "0:00", fill=(0, 0, 0), font=f_small)
    draw.text((520, 510), duration, fill=(0, 0, 0), font=f_small)

    # Shadow
    draw.rectangle(
        (CARD_X + SHADOW_OFFSET, CARD_Y + SHADOW_OFFSET, CARD_R + SHADOW_OFFSET, CARD_B + SHADOW_OFFSET),
        fill=SHADOW_COLOR,
    )

    # Card
    draw.rectangle((CARD_X, CARD_Y, CARD_R, CARD_B), fill=CARD_WHITE)

    # Thumbnail
    try:
        img = Image.open(raw).resize(
            (CARD_R - CARD_X - CARD_BORDER_W * 2,
             CARD_B - CARD_Y - CARD_BORDER_W * 2)
        )
        bg.paste(img, (CARD_X + CARD_BORDER_W, CARD_Y + CARD_BORDER_W))
    except:
        pass

    # ───────── RIGHT SIDE VERTICAL ─────────
    brand_text = "KIRTI_BOTS"
    try:
        brand_font = ImageFont.truetype("ShiviMusic/assets/font.ttf", 40)
    except:
        brand_font = ImageFont.load_default()

    txt_img = Image.new("RGBA", (300, 100), (0, 0, 0, 0))
    txt_draw = ImageDraw.Draw(txt_img)

    txt_draw.text((2, 2), brand_text, font=brand_font, fill=(255, 150, 0))
    txt_draw.text((0, 0), brand_text, font=brand_font, fill=(0, 0, 0))

    rotated = txt_img.rotate(90, expand=True)
    bg.paste(rotated, (W - 80, H // 2 - rotated.height // 2), rotated)

    # ───────── LEFT SIDE "POWERED BY" ─────────
    power_text = "Powered by Kirti Bots"

    try:
        power_font = ImageFont.truetype("ShiviMusic/assets/font.ttf", 28)
    except:
        power_font = ImageFont.load_default()

    draw.text((20, H - 50), power_text, fill=(0, 0, 0), font=power_font)

    bg.save(out)
    return out


async def get_thumb(videoid: str, player_username: str = None):

    if not player_username:
        player_username = app.username

    cache_path = f"{CACHE_DIR}/{videoid}.png"
    if os.path.exists(cache_path):
        return cache_path

    try:
        search = VideosSearch(videoid, limit=1)
        data = (await search.next())["result"][0]

        title = re.sub(r"\W+", " ", data["title"]).title()
        thumb = data["thumbnails"][0]["url"]
        duration = data.get("duration", "Unknown")
        channel = data["channel"]["name"]

    except:
        return YOUTUBE_IMG_URL

    raw = f"{CACHE_DIR}/raw.jpg"

    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(thumb) as r:
                if r.status == 200:
                    async with aiofiles.open(raw, "wb") as f:
                        await f.write(await r.read())
    except:
        return YOUTUBE_IMG_URL

    try:
        result = _sunburst_thumb(raw, title, channel, duration, player_username, cache_path)
    except:
        result = YOUTUBE_IMG_URL
