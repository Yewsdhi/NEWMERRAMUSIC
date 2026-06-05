import os
import re
import random
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from py_yt import VideosSearch
from config import YOUTUBE_IMG_URL
from ShiviMusic import app

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)


def trim_to_width(text: str, font: ImageFont.FreeTypeFont, max_w: int) -> str:
    ellipsis = "…"
    try:
        if font.getlength(text) <= max_w:
            return text
        for i in range(len(text) - 1, 0, -1):
            if font.getlength(text[:i] + ellipsis) <= max_w:
                return text[:i] + ellipsis
    except:
        return text[: max_w // 10] + "…" if len(text) > max_w // 10 else text
    return ellipsis


def draw_rounded_rect_border(draw, xy, radius, border_width, color):
    """Draw a rounded rectangle border (outline only, no fill)."""
    x1, y1, x2, y2 = xy
    for i in range(border_width):
        draw.rounded_rectangle(
            (x1 - i, y1 - i, x2 + i, y2 + i),
            radius=radius + i,
            outline=color,
        )


async def get_thumb(videoid: str, player_username: str = None) -> str:
    if player_username is None:
        player_username = app.username

    cache_path = os.path.join(CACHE_DIR, f"{videoid}_player.png")
    if os.path.exists(cache_path):
        return cache_path

    # ── fetch metadata ────────────────────────────────────────────────────────
    try:
        results = VideosSearch(
            f"https://www.youtube.com/watch?v={videoid}", limit=1
        )
        search = await results.next()
        data = search.get("result", [])[0]
        title = re.sub(r"\W+", " ", data.get("title", "Unknown Title")).title()
        thumbnail = data.get("thumbnails", [{}])[0].get("url", YOUTUBE_IMG_URL)
        duration = data.get("duration")
        views = data.get("viewCount", {}).get("short", "Unknown Views")
    except:
        title, thumbnail, duration, views = (
            "Unknown Title",
            YOUTUBE_IMG_URL,
            None,
            "Unknown",
        )

    is_live = not duration or str(duration).lower() in {"live", "live now", ""}
    duration_text = "Live" if is_live else duration or "0:00"

    # ── download thumbnail ────────────────────────────────────────────────────
    thumb_path = os.path.join(CACHE_DIR, f"thumb_{videoid}.png")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as r:
                if r.status == 200:
                    async with aiofiles.open(thumb_path, "wb") as f:
                        await f.write(await r.read())
    except:
        return YOUTUBE_IMG_URL

    # ════════════════════════════════════════════════════════════════════════════
    # CANVAS  1280 × 720  dark background
    # ════════════════════════════════════════════════════════════════════════════
    W, H = 1280, 720
    PINK = (255, 80, 180)          # hot-pink accent
    PINK_DARK = (220, 60, 150)
    WHITE = (255, 255, 255)
    GRAY = (180, 180, 180)
    DARK = (30, 30, 30)

    # ── blurred background ────────────────────────────────────────────────────
    bg_raw = Image.open(thumb_path).resize((W, H)).convert("RGB")
    bg_blur = bg_raw.filter(ImageFilter.GaussianBlur(40))
    # darken
    enhancer = ImageEnhance.Brightness(bg_blur)
    bg_blur = enhancer.enhance(0.35)
    canvas = bg_blur.convert("RGBA")

    # vignette overlay (dark edges)
    vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette)
    for i in range(120):
        alpha = int(180 * (i / 120) ** 2)
        vd.rectangle((i, i, W - i, H - i), outline=(0, 0, 0, 0))
    # simple dark border vignette
    for i in range(80):
        a = int(160 - i * 2)
        if a < 0:
            a = 0
        vd.rectangle(
            (i, i, W - i - 1, H - i - 1), outline=(0, 0, 0, a)
        )
    canvas = Image.alpha_composite(canvas, vignette)

    draw = ImageDraw.Draw(canvas)

    # ── fonts ─────────────────────────────────────────────────────────────────
    FONT_PATH = "ShiviMusic/assets/font.ttf"
    FONT2_PATH = "ShiviMusic/assets/font2.ttf"
    try:
        font_title   = ImageFont.truetype(FONT_PATH, 46)
        font_label   = ImageFont.truetype(FONT_PATH, 32)
        font_value   = ImageFont.truetype(FONT_PATH, 32)
        font_badge   = ImageFont.truetype(FONT_PATH, 26)
        font_time    = ImageFont.truetype(FONT_PATH, 26)
        font_brand   = ImageFont.truetype(FONT2_PATH, 28)
    except:
        font_title = font_label = font_value = font_badge = font_time = font_brand = (
            ImageFont.load_default()
        )

    # ════════════════════════════════════════════════════════════════════════════
    # LEFT PANEL  — rounded-rectangle thumbnail with pink border
    # ════════════════════════════════════════════════════════════════════════════
    THUMB_X, THUMB_Y = 70, 130       # top-left of the frame
    THUMB_W, THUMB_H = 470, 460      # frame size
    RADIUS = 32
    BORDER = 10

    # load & crop thumbnail to fill the frame
    raw_thumb = Image.open(thumb_path).convert("RGBA")
    raw_thumb = raw_thumb.resize((THUMB_W, THUMB_H), Image.LANCZOS)

    # rounded mask for the photo
    thumb_mask = Image.new("L", (THUMB_W, THUMB_H), 0)
    ImageDraw.Draw(thumb_mask).rounded_rectangle(
        (0, 0, THUMB_W - 1, THUMB_H - 1), radius=RADIUS, fill=255
    )
    thumb_rounded = Image.new("RGBA", (THUMB_W, THUMB_H), (0, 0, 0, 0))
    thumb_rounded.paste(raw_thumb, (0, 0), thumb_mask)

    canvas.paste(thumb_rounded, (THUMB_X, THUMB_Y), thumb_rounded)

    # pink border (drawn after pasting so it sits on top)
    for i in range(BORDER):
        draw.rounded_rectangle(
            (
                THUMB_X - BORDER + i,
                THUMB_Y - BORDER + i,
                THUMB_X + THUMB_W + BORDER - i - 1,
                THUMB_Y + THUMB_H + BORDER - i - 1,
            ),
            radius=RADIUS + BORDER - i,
            outline=PINK,
        )

    # ════════════════════════════════════════════════════════════════════════════
    # RIGHT PANEL  — info
    # ════════════════════════════════════════════════════════════════════════════
    INFO_X = 620   # left edge of text area
    INFO_TOP = 130

    # ── "NOW PLAYING" pill badge ──────────────────────────────────────────────
    badge_text = "NOW PLAYING"
    bw = int(font_badge.getlength(badge_text)) + 52
    bh = 46
    badge_x, badge_y = INFO_X, INFO_TOP

    # pill background
    draw.rounded_rectangle(
        (badge_x, badge_y, badge_x + bw, badge_y + bh),
        radius=bh // 2,
        fill=PINK,
    )
    # centered text
    btext_x = badge_x + (bw - font_badge.getlength(badge_text)) // 2
    btext_y = badge_y + (bh - 26) // 2 - 1
    draw.text((btext_x, btext_y), badge_text, font=font_badge, fill=(20, 20, 20))

    # ── title ─────────────────────────────────────────────────────────────────
    title_y = badge_y + bh + 24
    max_title_w = 610
    title_text = trim_to_width(title, font_title, max_title_w)
    draw.text((INFO_X, title_y), title_text, font=font_title, fill=WHITE)

    # pink underline (thin separator line)
    title_h = font_title.getbbox(title_text)[3] - font_title.getbbox(title_text)[1]
    line_y = title_y + title_h + 10
    draw.line((INFO_X, line_y, INFO_X + max_title_w, line_y), fill=PINK, width=2)

    # ── metadata rows ─────────────────────────────────────────────────────────
    meta_start_y = line_y + 26
    LINE_GAP = 52

    rows = [
        ("Duration:", duration_text),
        ("Views:", f"{views} views" if "view" not in str(views).lower() else views),
        ("Player:", f"@{player_username}"),
    ]

    VALUE_X = INFO_X + 195   # alignment column for values

    for i, (label, value) in enumerate(rows):
        row_y = meta_start_y + i * LINE_GAP
        draw.text((INFO_X, row_y), label, font=font_label, fill=GRAY)
        draw.text((VALUE_X, row_y), value, font=font_value, fill=PINK)

    # ── progress bar ─────────────────────────────────────────────────────────
    bar_y = meta_start_y + len(rows) * LINE_GAP + 18
    bar_x1 = INFO_X
    bar_x2 = INFO_X + 610
    bar_h = 8
    bar_radius = bar_h // 2

    # progress = roughly half (matches reference visual)
    progress_ratio = 0.12   # small dot near start like in reference
    dot_x = bar_x1 + int((bar_x2 - bar_x1) * progress_ratio)

    # track (gray)
    draw.rounded_rectangle(
        (bar_x1, bar_y, bar_x2, bar_y + bar_h),
        radius=bar_radius,
        fill=(100, 100, 100, 180),
    )
    # filled (pink)
    if dot_x > bar_x1 + bar_h:
        draw.rounded_rectangle(
            (bar_x1, bar_y, dot_x, bar_y + bar_h),
            radius=bar_radius,
            fill=PINK,
        )
    # scrubber dot (white circle)
    dot_r = 10
    draw.ellipse(
        (dot_x - dot_r, bar_y + bar_h // 2 - dot_r, dot_x + dot_r, bar_y + bar_h // 2 + dot_r),
        fill=WHITE,
    )

    # ── timestamps ────────────────────────────────────────────────────────────
    time_y = bar_y + bar_h + 14
    draw.text((bar_x1, time_y), "00:00", font=font_time, fill=WHITE)
    end_w = font_time.getlength(duration_text)
    draw.text((bar_x2 - end_w, time_y), duration_text, font=font_time, fill=WHITE)

    # ── brand watermark ───────────────────────────────────────────────────────
    brand = "Dev:- @kirtibots"
    bw_len = font_brand.getlength(brand)
    draw.text((W - bw_len - 40, H - 46), brand, font=font_brand, fill=WHITE)

    # ── save ──────────────────────────────────────────────────────────────────
    try:
        os.remove(thumb_path)
    except:
        pass

    canvas = canvas.convert("RGB")
    canvas.save(cache_path, "PNG")
    return cache_path
