# ======================================================
# ©️ 2025-26 All Rights Reserved by Kirti 😎
#
# 🧑‍💻 Developer : t.me/lll_APNA_BADNAM_BABY_lll
# 🔗 Source link : https://github.com/Badnam019
# 📢 Telegram channel : t.me/lll_APNA_BADNAM_BABY_lll
# ======================================================

import os
import re
import random
import aiofiles
import aiohttp

from PIL import (
    Image,
    ImageDraw,
    ImageEnhance,
    ImageFilter,
    ImageFont
)

from youtubesearchpython.__future__ import VideosSearch
from config import YOUTUBE_IMG_URL
from ShiviMusic import app

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

TITLE_X = 355
TITLE_Y = THUMB_Y + THUMB_H + 12

META_Y = TITLE_Y + 48

BAR_X, BAR_Y = 388, META_Y + 50
BAR_RED_LEN = 280
BAR_TOTAL_LEN = 480

ICONS_W, ICONS_H = 415, 45
ICONS_X = PANEL_X + (PANEL_W - ICONS_W) // 2
ICONS_Y = BAR_Y + 48

MAX_TITLE_WIDTH = 580

SHREYA_COLOR = [
    (255, 182, 193),
    (255, 105, 180),
    (255, 20, 147),
    (199, 125, 255),
    (160, 120, 255),
    (255, 255, 255),
]

def trim_to_width(
    text: str,
    font: ImageFont.FreeTypeFont,
    max_w: int
) -> str:

    ellipsis = "…"

    try:
        if font.getlength(text) <= max_w:
            return text

        for i in range(len(text) - 1, 0, -1):
            if font.getlength(text[:i] + ellipsis) <= max_w:
                return text[:i] + ellipsis

    except AttributeError:
        return (
            text[:max_w // 10] + "…"
            if len(text) > max_w // 10
            else text
        )

    return ellipsis


async def get_thumb(
    videoid: str,
    player_username: str = None
) -> str:

    if player_username is None:
        player_username = app.username

    cache_path = os.path.join(
        CACHE_DIR,
        f"{videoid}_pink.png"
    )

    if os.path.exists(cache_path):
        return cache_path

    try:
        results = VideosSearch(
            f"https://www.youtube.com/watch?v={videoid}",
            limit=1
        )

        search_result = await results.next()

        data = search_result.get("result", [])[0]

        title = re.sub(
            r"\W+",
            " ",
            data.get(
                "title",
                "Unsupported Title"
            )
        ).title()

        thumbnail = data.get(
            "thumbnails",
            [{}]
        )[0].get(
            "url",
            YOUTUBE_IMG_URL
        )

        duration = data.get("duration")

        views = data.get(
            "viewCount",
            {}
        ).get(
            "short",
            "Unknown Views"
        )

    except Exception:
        title = "Unsupported Title"
        thumbnail = YOUTUBE_IMG_URL
        duration = None
        views = "Unknown Views"

    is_live = (
        not duration
        or str(duration).strip().lower()
        in {"", "live", "live now"}
    )

    duration_text = (
        "Live"
        if is_live
        else duration or "Unknown"
    )

    thumb_path = os.path.join(
        CACHE_DIR,
        f"thumb_{videoid}.png"
    )

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:

                if resp.status == 200:
                    async with aiofiles.open(
                        thumb_path,
                        "wb"
                    ) as f:
                        await f.write(
                            await resp.read()
                        )

    except Exception:
        return YOUTUBE_IMG_URL

    base = (
        Image.open(thumb_path)
        .resize((1280, 720))
        .convert("RGBA")
    )

    bg = ImageEnhance.Brightness(
        base.filter(
            ImageFilter.GaussianBlur(18)
        )
    ).enhance(0.55)

    panel_area = bg.crop(
        (
            PANEL_X,
            PANEL_Y,
            PANEL_X + PANEL_W,
            PANEL_Y + PANEL_H
        )
    )

    random_color = random.choice(SHREYA_COLOR)

    overlay = Image.new(
        "RGBA",
        (PANEL_W, PANEL_H),
        (*random_color, TRANSPARENCY)
    )

    frosted = Image.alpha_composite(
        panel_area,
        overlay
    )

    mask = Image.new(
        "L",
        (PANEL_W, PANEL_H),
        0
    )

    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, PANEL_W, PANEL_H),
        50,
        fill=255
    )

    bg.paste(
        frosted,
        (PANEL_X, PANEL_Y),
        mask
    )

    draw = ImageDraw.Draw(bg)

    try:
        title_font = ImageFont.truetype(
            "ShiviMusic/assets/f.ttf",
            30
        )

        regular_font = ImageFont.truetype(
            "ShiviMusic/assets/font.ttf",
            18
        )

        top_font = ImageFont.truetype(
            "ShiviMusic/assets/font.ttf",
            25
        )

    except OSError:
        title_font = regular_font = top_font = ImageFont.load_default()

    # ======================================================
    # PINK BORDER THUMBNAIL
    # ======================================================

    BORDER_SIZE = 8

    thumb = (
        base.resize((THUMB_W, THUMB_H))
        .convert("RGBA")
    )

    thumb_mask = Image.new(
        "L",
        (THUMB_W, THUMB_H),
        0
    )

    ImageDraw.Draw(thumb_mask).rounded_rectangle(
        (0, 0, THUMB_W, THUMB_H),
        25,
        fill=255
    )

    glow = Image.new(
        "RGBA",
        (THUMB_W + 30, THUMB_H + 30),
        (255, 255, 255, 0)
    )

    glow_draw = ImageDraw.Draw(glow)

    for i in range(15):
        glow_draw.rounded_rectangle(
            (
                15 - i,
                15 - i,
                THUMB_W + 15 + i,
                THUMB_H + 15 + i
            ),
            radius=30,
            outline=(255, 20, 147, 20)
        )

    bg.paste(
        glow,
        (THUMB_X - 15, THUMB_Y - 15),
        glow
    )

    thumb_layer = Image.new(
        "RGBA",
        (
            THUMB_W + BORDER_SIZE * 2,
            THUMB_H + BORDER_SIZE * 2
        ),
        (255, 20, 147, 255)
    )

    ImageDraw.Draw(
        thumb_layer
    ).rounded_rectangle(
        (
            0,
            0,
            THUMB_W + BORDER_SIZE * 2,
            THUMB_H + BORDER_SIZE * 2
        ),
        radius=28,
        fill=(255, 20, 147, 255)
    )

    thumb_layer.paste(
        thumb,
        (BORDER_SIZE, BORDER_SIZE),
        thumb_mask
    )

    bg.paste(
        thumb_layer,
        (
            THUMB_X - BORDER_SIZE,
            THUMB_Y - BORDER_SIZE
        ),
        thumb_layer
    )

    # ======================================================
    # TITLE
    # ======================================================

    final_title = trim_to_width(
        title,
        title_font,
        MAX_TITLE_WIDTH
    )

    draw.text(
        (TITLE_X, TITLE_Y),
        final_title,
        fill="white",
        font=title_font,
        stroke_width=1,
        stroke_fill="black"
    )

    # ======================================================
    # META
    # ======================================================

    left_text = f"YouTube • {views}"
    right_text = f"Player • @{player_username}"

    left_w = regular_font.getlength(left_text)
    right_w = regular_font.getlength(right_text)

    gap = 30

    total_width = left_w + gap + right_w

    start_x = PANEL_X + (
        PANEL_W - total_width
    ) // 2

    draw.text(
        (start_x, META_Y),
        left_text,
        fill=(255, 255, 255),
        font=regular_font
    )

    draw.text(
        (start_x + left_w + gap, META_Y),
        right_text,
        fill=(255, 20, 147),
        font=regular_font
    )

    # ======================================================
    # MUSIC BAR
    # ======================================================

    draw.line(
        [
            (BAR_X, BAR_Y),
            (BAR_X + BAR_RED_LEN, BAR_Y)
        ],
        fill=(255, 20, 147),
        width=8
    )

    draw.line(
        [
            (BAR_X + BAR_RED_LEN, BAR_Y),
            (BAR_X + BAR_TOTAL_LEN, BAR_Y)
        ],
        fill=(180, 180, 180),
        width=6
    )

    draw.ellipse(
        [
            (BAR_X + BAR_RED_LEN - 10, BAR_Y - 10),
            (BAR_X + BAR_RED_LEN + 10, BAR_Y + 10)
        ],
        fill=(255, 20, 147)
    )

    draw.text(
        (BAR_X, BAR_Y + 15),
        "00:00",
        fill="white",
        font=regular_font
    )

    draw.text(
        (
            BAR_X + BAR_TOTAL_LEN -
            (90 if is_live else 60),
            BAR_Y + 15
        ),
        duration_text,
        fill=(255, 20, 147)
        if is_live
        else "white",
        font=regular_font
    )

    # ======================================================
    # PLAYER ICONS
    # ======================================================

    icons_path = "ShiviMusic/assets/play_icons.png"

    if os.path.isfile(icons_path):

        ic = (
            Image.open(icons_path)
            .resize((ICONS_W, ICONS_H))
            .convert("RGBA")
        )

        r, g, b, a = ic.split()

        pink_icons = Image.merge(
            "RGBA",
            (
                r.point(lambda _: 255),
                g.point(lambda _: 20),
                b.point(lambda _: 147),
                a
            )
        )

        bg.paste(
            pink_icons,
            (ICONS_X, ICONS_Y),
            pink_icons
        )

    # ======================================================
    # TOP TEXTS
    # ======================================================

    padding = 25

    left_top = "IG :- kirti_bots"

    draw.text(
        (padding, padding),
        left_top,
        fill=(255, 255, 255),
        font=top_font
    )

    right_top = "DEV :- badnam_bots"

    right_w = top_font.getlength(right_top)

    draw.text(
        (
            1280 - right_w - padding,
            padding
        ),
        right_top,
        fill=(255, 255, 255),
        font=top_font
    )

    # ======================================================
    # SAVE
    # ======================================================

    try:
        os.remove(thumb_path)
    except OSError:
        pass

    bg.save(cache_path)

    return cache_path

# ======================================================
# ©️ 2025-26 All Rights Reserved by Kirti 😎
# ======================================================
