import os
import re
import aiohttp
import aiofiles
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from py_yt import VideosSearch
from config import YOUTUBE_IMG_URL

# ══════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════
CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

W, H = 1280, 720

FONT_BOLD   = "ShiviMusic/assets/font2.ttf"
FONT_NORMAL = "ShiviMusic/assets/font.ttf"

# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════
def _font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()


def _trim(draw, text, font, max_w):
    if not text:
        return "Unknown"
    try:
        if draw.textlength(text, font=font) <= max_w:
            return text
        while len(text) > 1 and draw.textlength(text + "...", font=font) > max_w:
            text = text[:-1]
        return text + "..."
    except:
        return text[:28] + "..."


def _clean_views(raw):
    if not raw:
        return "N/A"
    cleaned = re.sub(r"\s*views?\s*", "", raw, flags=re.IGNORECASE)
    return f"{cleaned} views"


# ══════════════════════════════════════════════════════════════
# THUMB MAKER
# ══════════════════════════════════════════════════════════════
def _make_thumb(raw_path, title, channel, duration, views, cache_path):

    try:
        art_orig = Image.open(raw_path).convert("RGB")
    except:
        art_orig = Image.new("RGB", (400, 400), (30, 20, 15))

    # Background
    bg = art_orig.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(50))
    dark = Image.new("RGB", (W, H), (8, 5, 3))
    bg = Image.blend(bg, dark, 0.72).convert("RGBA")

    # Card
    CARD_L, CARD_T = 112, 135
    CARD_W, CARD_H = 400, 450

    art = art_orig.resize((CARD_W, CARD_H), Image.LANCZOS).convert("RGBA")

    mask = Image.new("L", (CARD_W, CARD_H), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, CARD_W, CARD_H], 22, fill=255)
    art.putalpha(mask)

    bg.paste(art, (CARD_L, CARD_T), art)

    # 🟡 YELLOW BORDER
    BORDER = 6
    border = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(border)

    bdraw.rounded_rectangle(
        [
            CARD_L - BORDER,
            CARD_T - BORDER,
            CARD_L + CARD_W + BORDER,
            CARD_T + CARD_H + BORDER
        ],
        radius=22 + BORDER,
        outline=(255, 215, 0, 255),  # GOLD YELLOW
        width=BORDER
    )

    bg.alpha_composite(border)

    draw = ImageDraw.Draw(bg)

    RX = 612
    MAX_TW = 600

    f_title = _font(FONT_BOLD, 60)
    f_sub   = _font(FONT_NORMAL, 37)
    f_time  = _font(FONT_BOLD, 31)

    # Text
    draw.text((RX, 240), _trim(draw, title, f_title, MAX_TW),
              font=f_title, fill=(255, 255, 255))

    draw.text((RX, 330), f"Artist: {channel}",
              font=f_sub, fill=(180, 180, 180))

    draw.text((RX, 380), f"Views: {views}",
              font=f_sub, fill=(180, 180, 180))

    # 🟢 GREEN PROGRESS BAR
    BAR_Y = 480
    draw.rectangle([RX, BAR_Y, RX + 600, BAR_Y + 6], fill=(80, 80, 80))
    draw.rectangle([RX, BAR_Y, RX + 300, BAR_Y + 6], fill=(0, 255, 150))  # GREEN

    # Time
    draw.text((RX, 500), "01:20", font=f_time, fill=(180, 180, 180))
    draw.text((RX + 500, 500), duration, font=f_time, fill=(180, 180, 180))

    # 🟢 BRANDING (GREEN)
    brand = "Powered by Kirti Bots"
    f_brand = _font(FONT_NORMAL, 28)

    try:
        tw = int(draw.textlength(brand, font=f_brand))
    except:
        tw = 200

    x = W - tw - 20
    y = H - 50

    # Shadow
    draw.text((x + 2, y + 2), brand, font=f_brand, fill=(0, 0, 0, 180))

    # Main text (GREEN)
    draw.text((x, y), brand, font=f_brand, fill=(0, 255, 150, 255))

    bg.convert("RGB").save(cache_path, "PNG")
    return cache_path


# ══════════════════════════════════════════════════════════════
# MAIN FUNCTION
# ══════════════════════════════════════════════════════════════
async def get_thumb(videoid: str):

    cache_path = os.path.join(CACHE_DIR, f"{videoid}.png")

    if os.path.exists(cache_path):
        return cache_path

    try:
        results = VideosSearch(f"https://www.youtube.com/watch?v={videoid}", limit=1)
        search = await results.next()
        data = search["result"][0]

        title = data.get("title", "Unknown")
        thumb = data["thumbnails"][-1]["url"]
        duration = data.get("duration", "0:00")
        channel = data["channel"]["name"]
        views = _clean_views(data.get("viewCount", {}).get("short", "N/A"))

    except:
        return YOUTUBE_IMG_URL

    raw_path = os.path.join(CACHE_DIR, f"raw_{videoid}.jpg")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(thumb) as resp:
                if resp.status != 200:
                    return YOUTUBE_IMG_URL

                async with aiofiles.open(raw_path, "wb") as f:
                    await f.write(await resp.read())

    except:
        return YOUTUBE_IMG_URL

    try:
        result = _make_thumb(raw_path, title, channel, duration, views, cache_path)
    except:
        result = YOUTUBE_IMG_URL

    try:
        if os.path.exists(raw_path):
            os.remove(raw_path)
    except:
        pass

    return result
