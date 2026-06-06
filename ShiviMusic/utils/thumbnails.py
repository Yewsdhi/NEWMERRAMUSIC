import os
import re
import random
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from py_yt import VideosSearch
from config import YOUTUBE_IMG_URL
from KanhaMusic import app

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def _font(path_hint: str, size: int) -> ImageFont.FreeTypeFont:
    for p in [path_hint,
              "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
              "/usr/share/fonts/truetype/google-fonts/Poppins-Regular.ttf",
              "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf"]:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

ASSET = "KanhaMusic/assets"
FONT_BOLD = os.path.join(ASSET, "font.ttf")
FONT_REG  = os.path.join(ASSET, "font2.ttf")
FONT_MED  = os.path.join(ASSET, "font.ttf")

def _trim(text: str, font: ImageFont.FreeTypeFont, max_w: int) -> str:
    """Trim text to fit max_w pixels, adding ellipsis if needed."""
    ellipsis = "..."
    try:
        if font.getlength(text) <= max_w:
            return text
        for i in range(len(text) - 1, 0, -1):
            if font.getlength(text[:i] + ellipsis) <= max_w:
                return text[:i] + ellipsis
    except Exception:
        return text[:max_w // 10] + "..." if len(text) > max_w // 10 else text
    return ellipsis

async def get_thumb(videoid: str, player_username: str = None) -> str:
    if player_username is None:
        player_username = app.username

    cache_path = os.path.join(CACHE_DIR, f"{videoid}_v2player.png")
    if os.path.exists(cache_path):
        return cache_path

    # ── Fetch metadata ────────────────────────────────────────────────────────
    try:
        results = VideosSearch(
            f"https://www.youtube.com/watch?v={videoid}", limit=1
        )
        search    = await results.next()
        data      = search.get("result", [])[0]
        title     = re.sub(r"\s+", " ", data.get("title", "Unknown Title")).strip()
        duration  = data.get("duration")
        views     = data.get("viewCount", {}).get("short", "Unknown")
    except Exception:
        title, duration, views = "Unknown Title", None, "Unknown"

    is_live       = not duration or str(duration).lower() in {"live", "live now", ""}
    duration_text = "Live" if is_live else (duration or "0:00")

    # ── Download Thumbnail in Ultra HD ────────────────────────────────────────
    thumb_path = os.path.join(CACHE_DIR, f"raw_{videoid}.png")
    hd_url = f"https://img.youtube.com/vi/{videoid}/maxresdefault.jpg"
    sd_url = f"https://img.youtube.com/vi/{videoid}/mqdefault.jpg"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(hd_url) as r:
                if r.status == 200:
                    async with aiofiles.open(thumb_path, "wb") as f:
                        await f.write(await r.read())
                else:
                    async with session.get(sd_url) as r2:
                        async with aiofiles.open(thumb_path, "wb") as f2:
                            await f2.write(await r2.read())
        except Exception:
            return YOUTUBE_IMG_URL

    if not os.path.exists(thumb_path):
        return YOUTUBE_IMG_URL

    # ════════════════════════════════════════════════════════════════════════════
    # CANVAS CONFIGURATION & MEGA RANDOM COLORS POOL (50+ PREMIUM SHADES)
    # ════════════════════════════════════════════════════════════════════════════
    W, H   = 1280, 720
    WHITE  = (255, 255, 255)
    GRAY   = (155, 148, 144)

    # 50+ Vibrant and premium dynamic streaming colors pool
    RANDOM_COLORS = [
        (255, 85, 185), (0, 229, 255), (0, 230, 118), (255, 145, 0), (213, 0, 249),
        (255, 215, 0), (255, 23, 68), (41, 121, 255), (245, 0, 87), (118, 255, 3),
        (233, 30, 99), (156, 39, 176), (103, 58, 183), (63, 81, 181), (33, 150, 243),
        (0, 188, 212), (0, 150, 136), (76, 175, 80), (139, 195, 74), (205, 220, 57),
        (255, 235, 59), (255, 193, 7), (255, 152, 0), (255, 87, 34), (244, 67, 54),
        (255, 110, 196), (0, 245, 255), (0, 255, 127), (255, 165, 0), (224, 33, 255),
        (255, 218, 185), (255, 69, 0), (30, 144, 255), (255, 20, 147), (0, 255, 255),
        (127, 255, 0), (255, 0, 255), (0, 255, 0), (255, 255, 0), (255, 0, 0),
        (0, 0, 255), (138, 43, 226), (210, 105, 30), (255, 127, 80), (100, 149, 237),
        (0, 206, 209), (255, 20, 147), (75, 0, 130), (255, 105, 180), (50, 205, 50)
    ]
    THEME_COLOR = random.choice(RANDOM_COLORS)

    src = Image.open(thumb_path).convert("RGB")
    sw, sh = src.size

    # ── Background: Very Light Blur & High Visibility ───────────────────────
    # Blur radius ko 25 se ghata kar sirf 6 kiya taaki piche ka thumbnail ekdum saaf dikhe
    bg = src.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(6))
    # Brightness badha kar 0.80 kiya taaki image bilkul blackish na dikhe, full clear ho
    bg = ImageEnhance.Brightness(bg).enhance(0.80).convert("RGBA")

    # Ultra-Smooth minimal corner fade shadow layer
    vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd  = ImageDraw.Draw(vig)
    for i in range(70):
        a = max(0, int(95 * (1 - i / 70) ** 1.8))  
        vd.rectangle((i, i, W - 1 - i, H - 1 - i), outline=(0, 0, 0, a))
    canvas = Image.alpha_composite(bg, vig)

    # Fonts Loading
    f_title = _font(FONT_BOLD, 50)
    f_badge = _font(FONT_BOLD, 22)
    f_label = _font(FONT_MED,  30)
    f_value = _font(FONT_MED,  30)
    f_time  = _font(FONT_REG,  26)

    # ════════════════════════════════════════════════════════════════════════════
    # FRONT CARD DESIGN WITH THICK BORDER & OUTER SOFT DROP SHADOW
    # ════════════════════════════════════════════════════════════════════════════
    CX, CY = 60, 120
    CW, CH = 489, 479
    RADIUS  = 26

    # 1. Realistic Outer Soft Drop Shadow
    shadow_lyr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow_lyr)
    s_draw.rounded_rectangle(
        (CX - 15, CY - 15, CX + CW + 15, CY + CH + 15),
        radius=RADIUS + 10, fill=(0, 0, 0, 180)
    )
    shadow_lyr = shadow_lyr.filter(ImageFilter.GaussianBlur(30))
    canvas = Image.alpha_composite(canvas, shadow_lyr)

    # 2. Solid Base Layer
    fill_lyr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(fill_lyr).rounded_rectangle(
        (CX, CY, CX + CW, CY + CH), radius=RADIUS, fill=(20, 8, 3, 255)
    )
    canvas = Image.alpha_composite(canvas, fill_lyr)

    # Image Crop Logic
    scale = CH / sh
    nw = int(sw * scale)
    resized = src.resize((nw, CH), Image.LANCZOS).convert("RGBA")
    ox = max(0, (nw - CW) // 2)  
    cropped = resized.crop((ox, 0, ox + CW, CH))

    t_mask = Image.new("L", (CW, CH), 0)
    ImageDraw.Draw(t_mask).rounded_rectangle((0, 0, CW - 1, CH - 1), radius=RADIUS, fill=255)
    thumb_lyr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    thumb_lyr.paste(cropped, (CX, CY), t_mask)
    canvas = Image.alpha_composite(canvas, thumb_lyr)

    # 3. Super Thick Solid Border Frame Overlay (Width=6 for heavy card look)
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gl)
    r, g, b = THEME_COLOR
    gd.rounded_rectangle(
        (CX, CY, CX + CW, CY + CH), 
        radius=RADIUS, outline=(r, g, b, 255), width=6
    )
    canvas = Image.alpha_composite(canvas, gl)
    draw = ImageDraw.Draw(canvas)

    # ════════════════════════════════════════════════════════════════════════════
    # RIGHT DETAILS PANEL
    # ════════════════════════════════════════════════════════════════════════════
    RX = 618

    # ── NOW PLAYING Pill Badge ───────────────────────────────────────────────
    bt     = "NOW PLAYING"
    btw    = int(f_badge.getlength(bt))
    bpad_x = (224 - btw) // 2
    draw.rounded_rectangle((624, 127, 848, 173), radius=23, fill=THEME_COLOR)
    draw.text((624 + bpad_x, 139), bt, font=f_badge, fill=(15, 15, 15))

    # ── Title Text & Underline Line Space Separator ──────────────────────────
    title_x   = RX
    title_y   = 200
    title_str = _trim(title, f_title, 610)
    draw.text((title_x, title_y), title_str, font=f_title, fill=WHITE)
    
    line_y = title_y + 68 
    draw.line((title_x, line_y, 1235, line_y), fill=THEME_COLOR, width=2)

    # ── Statistics Layout Info Rows ──────────────────────────────────────────
    VX   = RX + 194
    views_str = views if "view" in str(views).lower() else f"{views} views"
    rows = [
        ("Duration:", duration_text,                  284),
        ("Views:",    views_str,                      336),
        ("Player:",   f"@{player_username}",          388),
    ]
    for lbl, val, ry in rows:
        draw.text((RX,  ry), lbl, font=f_label, fill=GRAY)
        draw.text((VX,  ry), val, font=f_value, fill=THEME_COLOR)

    # ── Progress Track Slider bar ────────────────────────────────────────────
    BX1, BX2, BH, BY = RX, 1232, 6, 462
    dot_x = BX1 + int((BX2 - BX1) * 0.15)   
    draw.rounded_rectangle((BX1, BY, BX2, BY + BH), radius=3, fill=(70, 70, 70))
    draw.rounded_rectangle((BX1, BY, dot_x, BY + BH), radius=3, fill=THEME_COLOR)
    cbar = BY + BH // 2
    draw.ellipse((dot_x - 11, cbar - 11, dot_x + 11, cbar + 11), fill=WHITE)

    # ── Playback Timestamps ──────────────────────────────────────────────────
    draw.text((BX1, 496), "00:00", font=f_time, fill=WHITE)
    draw.text((BX2 - int(f_time.getlength(duration_text)), 496),
              duration_text, font=f_time, fill=WHITE)

    try:
        os.remove(thumb_path)
    except Exception:
        pass

    canvas.convert("RGB").save(cache_path)
    return cache_path
