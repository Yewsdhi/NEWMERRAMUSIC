import os, aiofiles, aiohttp
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
        new = text[:i] + ellipsis

        if font.getlength(new) <= max_width:
            return new

    return ellipsis


async def get_thumb(videoid: str, player_username: str = None) -> str:

    if player_username is None:
        player_username = app.username

    cache_path = os.path.join(
        CACHE_DIR,
        f"{videoid}_neon.png"
    )

    if os.path.exists(cache_path):
        return cache_path

    # =========================
    # FETCH YOUTUBE DATA
    # =========================
    try:
        results = VideosSearch(
            f"https://www.youtube.com/watch?v={videoid}",
            limit=1
        )

        search_result = await results.next()

        data = search_result.get("result", [])[0]

        title = data.get(
            "title",
            "Unknown Title"
        )

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
        duration = "03:00"
        views = "1M views"
        thumbnail = YOUTUBE_IMG_URL

    # =========================
    # DOWNLOAD THUMBNAIL
    # =========================
    thumb_path = os.path.join(
        CACHE_DIR,
        f"{videoid}.jpg"
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

    except:
        return YOUTUBE_IMG_URL

    # =========================
    # MAIN SIZE
    # =========================
    W, H = 1280, 720

    try:
        original = Image.open(
            thumb_path
        ).convert("RGBA")

    except:
        return YOUTUBE_IMG_URL

    # =========================
    # BACKGROUND
    # =========================
    bg = original.resize((W, H))

    bg = bg.filter(
        ImageFilter.GaussianBlur(35)
    )

    enhancer = ImageEnhance.Brightness(bg)

    bg = enhancer.enhance(0.30)

    dark_layer = Image.new(
        "RGBA",
        (W, H),
        (0, 0, 0, 120)
    )

    bg = Image.alpha_composite(
        bg,
        dark_layer
    )

    draw = ImageDraw.Draw(bg)

    # =========================
    # FONTS
    # =========================
    try:
        bold_font = "ShiviMusic/assets/font2.ttf"
        regular_font = "ShiviMusic/assets/font.ttf"

        title_font = ImageFont.truetype(
            bold_font,
            60
        )

        artist_font = ImageFont.truetype(
            regular_font,
            38
        )

        info_font = ImageFont.truetype(
            regular_font,
            30
        )

        small_font = ImageFont.truetype(
            regular_font,
            24
        )

    except:
        title_font = artist_font = info_font = (
            small_font
        ) = ImageFont.load_default()

    # =========================
    # ALBUM COVER
    # =========================
    cover_size = 420

    cover_x = 90
    cover_y = (H - cover_size) // 2

    album = original.resize(
        (cover_size, cover_size),
        Image.LANCZOS
    )

    # Rounded Mask
    mask = Image.new(
        "L",
        (cover_size, cover_size),
        0
    )

    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, cover_size, cover_size),
        radius=45,
        fill=255
    )

    # Shadow
    shadow = Image.new(
        "RGBA",
        (cover_size + 80, cover_size + 80),
        (0, 0, 0, 0)
    )

    ImageDraw.Draw(shadow).rounded_rectangle(
        (
            40,
            40,
            cover_size + 40,
            cover_size + 40
        ),
        radius=50,
        fill=(0, 0, 0, 180)
    )

    shadow = shadow.filter(
        ImageFilter.GaussianBlur(30)
    )

    bg.paste(
        shadow,
        (cover_x - 40, cover_y - 40),
        shadow
    )

    # Paste Album
    bg.paste(
        album,
        (cover_x, cover_y),
        mask
    )

    # =========================
    # NEON BORDER
    # =========================
    neon_colors = [
        (0, 255, 255, 180),   # Cyan
        (255, 0, 255, 160),   # Pink
        (0, 200, 255, 150),
    ]

    for i in range(28, 0, -4):

        glow_overlay = Image.new(
            "RGBA",
            (W, H),
            (0, 0, 0, 0)
        )

        glow_draw = ImageDraw.Draw(
            glow_overlay
        )

        glow_draw.rounded_rectangle(
            (
                cover_x - i,
                cover_y - i,
                cover_x + cover_size + i,
                cover_y + cover_size + i
            ),
            radius=55,
            outline=neon_colors[
                i % len(neon_colors)
            ],
            width=6
        )

        glow_overlay = glow_overlay.filter(
            ImageFilter.GaussianBlur(12)
        )

        bg = Image.alpha_composite(
            bg,
            glow_overlay
        )

    # Main Border
    draw.rounded_rectangle(
        (
            cover_x,
            cover_y,
            cover_x + cover_size,
            cover_y + cover_size
        ),
        radius=45,
        outline=(0, 255, 255),
        width=8
    )

    # Inner Border
    draw.rounded_rectangle(
        (
            cover_x + 8,
            cover_y + 8,
            cover_x + cover_size - 8,
            cover_y + cover_size - 8
        ),
        radius=38,
        outline=(255, 0, 255),
        width=3
    )

    # =========================
    # GLASS PANEL
    # =========================
    panel_x = 580
    panel_y = cover_y
    panel_w = 620
    panel_h = cover_size

    overlay = Image.new(
        "RGBA",
        (W, H),
        (0, 0, 0, 0)
    )

    o_draw = ImageDraw.Draw(overlay)

    o_draw.rounded_rectangle(
        (
            panel_x,
            panel_y,
            panel_x + panel_w,
            panel_y + panel_h
        ),
        radius=35,
        fill=(255, 255, 255, 25)
    )

    bg = Image.alpha_composite(
        bg,
        overlay
    )

    # Panel Border
    draw.rounded_rectangle(
        (
            panel_x,
            panel_y,
            panel_x + panel_w,
            panel_y + panel_h
        ),
        radius=35,
        outline=(255, 255, 255, 40),
        width=2
    )

    # =========================
    # TEXT
    # =========================
    title = trim_to_width(
        title,
        title_font,
        540
    )

    artist = trim_to_width(
        artist,
        artist_font,
        500
    )

    # Neon Glow Text Effect
    for offset in range(8, 0, -2):
        draw.text(
            (620-offset, cover_y + 45-offset),
            title,
            font=title_font,
            fill=(0, 255, 255, 40)
        )

    draw.text(
        (620, cover_y + 45),
        title,
        font=title_font,
        fill=(255, 255, 255)
    )

    draw.text(
        (620, cover_y + 145),
        f"Artist : {artist}",
        font=artist_font,
        fill=(220, 220, 220)
    )

    draw.text(
        (620, cover_y + 210),
        f"Views : {views}",
        font=info_font,
        fill=(190, 190, 190)
    )

    draw.text(
        (620, cover_y + 255),
        f"Duration : {duration}",
        font=info_font,
        fill=(190, 190, 190)
    )

    # =========================
    # MUSIC BAR
    # =========================
    bar_x = 620
    bar_y = cover_y + 340

    bar_w = 500
    bar_h = 10

    # Background Bar
    draw.rounded_rectangle(
        (
            bar_x,
            bar_y,
            bar_x + bar_w,
            bar_y + bar_h
        ),
        radius=10,
        fill=(255, 255, 255, 60)
    )

    progress = 0.45

    # Neon Progress
    draw.rounded_rectangle(
        (
            bar_x,
            bar_y,
            bar_x + int(bar_w * progress),
            bar_y + bar_h
        ),
        radius=10,
        fill=(0, 255, 255)
    )

    # Knob Glow
    knob_x = bar_x + int(bar_w * progress)

    for r in range(20, 5, -5):
        draw.ellipse(
            (
                knob_x - r,
                bar_y - r + 5,
                knob_x + r,
                bar_y + r + 5
            ),
            fill=(0, 255, 255, 20)
        )

    draw.ellipse(
        (
            knob_x - 10,
            bar_y - 5,
            knob_x + 10,
            bar_y + 15
        ),
        fill=(255, 255, 255)
    )

    # Time Text
    draw.text(
        (bar_x, bar_y + 25),
        "00:25",
        font=small_font,
        fill=(255, 255, 255)
    )

    draw.text(
        (bar_x + bar_w - 70, bar_y + 25),
        duration,
        font=small_font,
        fill=(255, 255, 255)
    )

    # =========================
    # TOP TEXT
    # =========================
    top_text = "NOW PLAYING"

    top_w = draw.textlength(
        top_text,
        font=artist_font
    )

    draw.text(
        ((W - top_w) / 2, 35),
        top_text,
        font=artist_font,
        fill=(0, 255, 255)
    )

    # =========================
    # FOOTER
    # =========================
    footer_text = f"Powered By @{player_username}"

    footer_w = draw.textlength(
        footer_text,
        font=small_font
    )

    draw.text(
        (
            W - footer_w - 40,
            H - 50
        ),
        footer_text,
        font=small_font,
        fill=(255, 0, 255)
    )

    # =========================
    # SAVE FINAL
    # =========================
    final = bg.convert("RGB")

    final.save(
        cache_path,
        quality=95
    )

    try:
        os.remove(thumb_path)
    except:
        pass

    return cache_path
