import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from config import YOUTUBE_IMG_URL

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

PANEL_W, PANEL_H = 763, 545
PANEL_X = (1280 - PANEL_W) // 2
PANEL_Y = 88
TRANSPARENCY = 170
INNER_OFFSET = 36

THUMB_W, THUMB_H = 542, 273
THUMB_X = PANEL_X + (PANEL_W - THUMB_W) // 2
THUMB_Y = PANEL_Y + INNER_OFFSET

TITLE_X = 377
META_X = 377
TITLE_Y = THUMB_Y + THUMB_H + 10
META_Y = TITLE_Y + 45

BAR_X, BAR_Y = 388, META_Y + 45
BAR_RED_LEN = 280
BAR_TOTAL_LEN = 480

ICONS_W, ICONS_H = 415, 45
ICONS_X = PANEL_X + (PANEL_W - ICONS_W) // 2
ICONS_Y = BAR_Y + 48

MAX_TITLE_WIDTH = 580


def trim_to_width(text: str, font, max_w: int) -> str:
    ellipsis = "…"
    if font.getlength(text) <= max_w:
        return text
    for i in range(len(text) - 1, 0, -1):
        if font.getlength(text[:i] + ellipsis) <= max_w:
            return text[:i] + ellipsis
    return ellipsis


async def _download(session, url: str):
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=20)) as resp:
            if resp.status == 200:
                data = await resp.read()
                if data:
                    return data
    except Exception:
        pass
    return None


async def get_thumb(videoid, user_id=None):
    # Use a new cache version so old/wrong cached thumbnails are not reused.
    videoid = str(videoid or "").strip()
    cache_path = os.path.join(CACHE_DIR, f"{videoid}_v5.png")

    if videoid and os.path.isfile(cache_path):
        return cache_path

    # Always use the EXACT YouTube video ID. The previous code searched the
    # video URL through VideosSearch, which could return a different song.
    thumbnail_urls = []
    if videoid:
        thumbnail_urls = [
            f"https://i.ytimg.com/vi/{videoid}/maxresdefault.jpg",
            f"https://i.ytimg.com/vi/{videoid}/sddefault.jpg",
            f"https://i.ytimg.com/vi/{videoid}/hqdefault.jpg",
        ]

    thumb_data = None
    async with aiohttp.ClientSession() as session:
        for url in thumbnail_urls:
            thumb_data = await _download(session, url)
            if thumb_data:
                break

        if not thumb_data:
            thumb_data = await _download(session, YOUTUBE_IMG_URL)

    if not thumb_data:
        return YOUTUBE_IMG_URL

    thumb_path = os.path.join(CACHE_DIR, f"thumb_{videoid or 'default'}_v5.jpg")
    try:
        async with aiofiles.open(thumb_path, "wb") as f:
            await f.write(thumb_data)

        base = Image.open(thumb_path).convert("RGBA").resize((1280, 720))
    except Exception:
        try:
            os.remove(thumb_path)
        except OSError:
            pass
        return YOUTUBE_IMG_URL

    try:
        os.remove(thumb_path)
    except OSError:
        pass

    # Exact video thumbnail is used as the full background and card image.
    bg = ImageEnhance.Brightness(
        base.filter(ImageFilter.BoxBlur(10))
    ).enhance(0.6)

    panel_area = bg.crop(
        (PANEL_X, PANEL_Y, PANEL_X + PANEL_W, PANEL_Y + PANEL_H)
    )
    overlay = Image.new(
        "RGBA",
        (PANEL_W, PANEL_H),
        (255, 255, 255, TRANSPARENCY),
    )
    frosted = Image.alpha_composite(panel_area, overlay)

    mask = Image.new("L", (PANEL_W, PANEL_H), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, PANEL_W, PANEL_H),
        50,
        fill=255,
    )
    bg.paste(frosted, (PANEL_X, PANEL_Y), mask)

    draw = ImageDraw.Draw(bg)

    try:
        title_font = ImageFont.truetype(
            "ShiviMusic/assets/font2.ttf", 32
        )
        regular_font = ImageFont.truetype(
            "ShiviMusic/assets/font.ttf", 18
        )
    except OSError:
        title_font = regular_font = ImageFont.load_default()

    thumb = base.resize((THUMB_W, THUMB_H))
    tmask = Image.new("L", thumb.size, 0)
    ImageDraw.Draw(tmask).rounded_rectangle(
        (0, 0, THUMB_W, THUMB_H),
        20,
        fill=255,
    )
    bg.paste(thumb, (THUMB_X, THUMB_Y), tmask)

    # Video ID is reliable; avoid searching YouTube again and showing
    # another video's title/thumbnail.
    display_title = "YouTube Music"
    if videoid:
        display_title = f"YouTube • {videoid[:11]}"

    draw.text(
        (TITLE_X, TITLE_Y),
        trim_to_width(display_title, title_font, MAX_TITLE_WIDTH),
        fill="black",
        font=title_font,
    )
    draw.text(
        (META_X, META_Y),
        "YouTube",
        fill="black",
        font=regular_font,
    )

    draw.line(
        [(BAR_X, BAR_Y), (BAR_X + BAR_RED_LEN, BAR_Y)],
        fill="red",
        width=6,
    )
    draw.line(
        [(BAR_X + BAR_RED_LEN, BAR_Y), (BAR_X + BAR_TOTAL_LEN, BAR_Y)],
        fill="gray",
        width=5,
    )
    draw.ellipse(
        [
            (BAR_X + BAR_RED_LEN - 7, BAR_Y - 7),
            (BAR_X + BAR_RED_LEN + 7, BAR_Y + 7),
        ],
        fill="red",
    )

    draw.text(
        (BAR_X, BAR_Y + 15),
        "00:00",
        fill="black",
        font=regular_font,
    )

    icons_path = "ShiviMusic/assets/play_icons.png"
    if os.path.isfile(icons_path):
        try:
            ic = Image.open(icons_path).resize(
                (ICONS_W, ICONS_H)
            ).convert("RGBA")
            r, g, b, a = ic.split()
            black_ic = Image.merge(
                "RGBA",
                (
                    r.point(lambda *_: 0),
                    g.point(lambda *_: 0),
                    b.point(lambda *_: 0),
                    a,
                ),
            )
            bg.paste(
                black_ic,
                (ICONS_X, ICONS_Y),
                black_ic,
            )
        except Exception:
            pass

    try:
        bg.save(cache_path, "PNG")
        return cache_path
    except Exception:
        return YOUTUBE_IMG_URL
