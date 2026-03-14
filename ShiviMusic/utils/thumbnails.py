# ======================================================
# ©️ 2025-26 Neon Player Thumbnail Generator
# ======================================================

import os
import re
import random
import aiofiles
import aiohttp

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from py_yt import VideosSearch

from config import YOUTUBE_IMG_URL
from ShiviMusic import app

# ================== CACHE ==================

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

THUMB_VERSION = "neon_v1"

# ================== PANEL ==================

PANEL_W, PANEL_H = 763, 545
PANEL_X = (1280 - PANEL_W) // 2
PANEL_Y = 88

TRANSPARENCY = 170
INNER_OFFSET = 36

# ================== THUMB ==================

THUMB_W, THUMB_H = 542, 273
THUMB_X = PANEL_X + (PANEL_W - THUMB_W) // 2
THUMB_Y = PANEL_Y + INNER_OFFSET

# ================== TEXT ==================

TITLE_X = 377
TITLE_Y = THUMB_Y + THUMB_H + 10

META_Y = TITLE_Y + 45

# ================== PLAYER BAR ==================

BAR_X, BAR_Y = 388, META_Y + 45
BAR_RED_LEN = 280
BAR_TOTAL_LEN = 480

# ================== ICONS ==================

ICONS_W, ICONS_H = 415, 45
ICONS_X = PANEL_X + (PANEL_W - ICONS_W) // 2
ICONS_Y = BAR_Y + 48

MAX_TITLE_WIDTH = 580

# ================== COLORS ==================

SHUKLA_COLOR = [
    (188,250,152),
    (110,180,245),
    (242,179,240),
    (249,255,158),
    (164,163,240),
    (135,250,244),
]

NEON_PINK = (255,0,170)
NEON_BLUE = (0,255,255)

# ======================================================

def trim_to_width(text,font,max_w):

    ellipsis="…"

    try:

        if font.getlength(text)<=max_w:
            return text

        for i in range(len(text)-1,0,-1):

            if font.getlength(text[:i]+ellipsis)<=max_w:
                return text[:i]+ellipsis

    except AttributeError:

        return text[:max_w//10]+"…" if len(text)>max_w//10 else text

    return ellipsis

# ======================================================

async def get_thumb(videoid,player_username=None):

    if player_username is None:
        player_username = app.username

    cache_path = os.path.join(CACHE_DIR,f"{videoid}_{THUMB_VERSION}.png")

    if os.path.exists(cache_path):
        return cache_path

# ================== YOUTUBE INFO ==================

    try:

        results = VideosSearch(
            f"https://www.youtube.com/watch?v={videoid}",
            limit=1
        )

        search = await results.next()

        res = search.get("result",[])

        if not res:
            raise Exception

        data = res[0]

        title = re.sub(r"\W+"," ",data.get("title","Unknown")).title()

        thumbnail = data.get("thumbnails",[{}])[0].get(
            "url",
            YOUTUBE_IMG_URL
        )

        duration = data.get("duration")

        views = data.get("viewCount",{}).get(
            "short",
            "Unknown Views"
        )

    except Exception:

        title = "Unsupported Title"
        thumbnail = YOUTUBE_IMG_URL
        duration = None
        views = "Unknown Views"

# ================== LIVE CHECK ==================

    is_live = not duration or str(duration).lower() in {"","live","live now"}

    duration_text = "LIVE" if is_live else duration

# ================== DOWNLOAD THUMB ==================

    thumb_path = os.path.join(CACHE_DIR,f"{videoid}.png")

    try:

        async with aiohttp.ClientSession() as session:

            async with session.get(thumbnail) as resp:

                if resp.status==200:

                    async with aiofiles.open(thumb_path,"wb") as f:

                        await f.write(await resp.read())

    except Exception:

        return YOUTUBE_IMG_URL

# ================== IMAGE LOAD ==================

    base = Image.open(thumb_path).resize((1280,720)).convert("RGBA")

    bg = ImageEnhance.Brightness(
        base.filter(ImageFilter.BoxBlur(10))
    ).enhance(0.6)

# ================== PANEL ==================

    panel = bg.crop((PANEL_X,PANEL_Y,PANEL_X+PANEL_W,PANEL_Y+PANEL_H))

    color = random.choice(SHUKLA_COLOR)

    overlay = Image.new(
        "RGBA",
        (PANEL_W,PANEL_H),
        (*color,TRANSPARENCY)
    )

    frosted = Image.alpha_composite(panel,overlay)

    mask = Image.new("L",(PANEL_W,PANEL_H),0)

    ImageDraw.Draw(mask).rounded_rectangle(
        (0,0,PANEL_W,PANEL_H),
        50,
        fill=255
    )

    bg.paste(frosted,(PANEL_X,PANEL_Y),mask)

    draw = ImageDraw.Draw(bg)

# ================== FONTS ==================

    try:

        title_font = ImageFont.truetype(
            "ShiviMusic/assets/f.ttf",
            32
        )

        font = ImageFont.truetype(
            "ShiviMusic/assets/font.ttf",
            20
        )

    except:

        title_font = font = ImageFont.load_default()

# ================== THUMB ==================

    thumb = base.resize((THUMB_W,THUMB_H))

    bg.paste(thumb,(THUMB_X,THUMB_Y))

# ================== TITLE ==================

    title = trim_to_width(title,title_font,MAX_TITLE_WIDTH)

# glow effect
    for i in range(4,0,-1):

        draw.text(
            (TITLE_X+i,TITLE_Y+i),
            title,
            fill=NEON_BLUE,
            font=title_font
        )

    draw.text(
        (TITLE_X,TITLE_Y),
        title,
        fill=(255,255,255),
        font=title_font
    )

# ================== META ==================

    meta = f"YouTube | {views}"

    draw.text(
        (TITLE_X,META_Y),
        meta,
        fill=(255,255,255),
        font=font
    )

# ================== NEON PLAYER ==================

# background bar

    draw.line(
        [(BAR_X,BAR_Y),(BAR_X+BAR_TOTAL_LEN,BAR_Y)],
        fill=(40,40,40),
        width=8
    )

# glow

    for g in range(10,0,-2):

        draw.line(
            [(BAR_X,BAR_Y),(BAR_X+BAR_RED_LEN,BAR_Y)],
            fill=NEON_BLUE,
            width=g
        )

# main bar

    draw.line(
        [(BAR_X,BAR_Y),(BAR_X+BAR_RED_LEN,BAR_Y)],
        fill=NEON_PINK,
        width=6
    )

# circle

    draw.ellipse(

        [
            (BAR_X+BAR_RED_LEN-10,BAR_Y-10),
            (BAR_X+BAR_RED_LEN+10,BAR_Y+10)
        ],

        fill=NEON_BLUE

    )

# ================== TIME ==================

    draw.text(
        (BAR_X,BAR_Y+15),
        "00:00",
        fill="white",
        font=font
    )

    draw.text(
        (BAR_X+BAR_TOTAL_LEN-60,BAR_Y+15),
        duration_text,
        fill="white",
        font=font
    )

# ================== ICONS ==================

    icons = "ShiviMusic/assets/play_icons.png"

    if os.path.isfile(icons):

        ic = Image.open(icons).resize(
            (ICONS_W,ICONS_H)
        ).convert("RGBA")

        r,g,b,a = ic.split()

        neon_ic = Image.merge(

            "RGBA",

            (
                r.point(lambda _:0),
                g.point(lambda _:255),
                b.point(lambda _:255),
                a
            )

        )

        bg.paste(neon_ic,(ICONS_X,ICONS_Y),neon_ic)

# ================== DEV TEXT ==================

    draw.text(
        (25,25),
        "DEV : @Kirti_update",
        fill=(255,255,0),
        font=font
    )

# ================== SAVE ==================

    try:
        os.remove(thumb_path)
    except:
        pass

    bg.save(cache_path)

    return cache_path

# ======================================================
# END
# ======================================================
