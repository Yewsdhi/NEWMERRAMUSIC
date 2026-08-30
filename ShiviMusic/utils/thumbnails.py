import os
import aiofiles
import aiohttp

from PIL import (
    Image,
    ImageDraw,
    ImageEnhance,
    ImageFilter,
    ImageFont,
)

from config import YOUTUBE_IMG_URL


# =========================================================
# CONFIG
# =========================================================

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

BAR_X = 388
BAR_Y = META_Y + 45

BAR_RED_LEN = 280
BAR_TOTAL_LEN = 480

ICONS_W, ICONS_H = 415, 45
ICONS_X = PANEL_X + (PANEL_W - ICONS_W) // 2
ICONS_Y = BAR_Y + 48

MAX_TITLE_WIDTH = 580

CACHE_VERSION = "v6"


# =========================================================
# TEXT HELPER
# =========================================================

def trim_to_width(text: str, font, max_w: int) -> str:
    text = str(text or "").strip()

    if not text:
        return ""

    ellipsis = "…"

    try:
        if font.getlength(text) <= max_w:
            return text

        for i in range(len(text) - 1, 0, -1):
            candidate = text[:i].rstrip() + ellipsis

            if font.getlength(candidate) <= max_w:
                return candidate

    except Exception:
        pass

    return text[:40] + ellipsis


# =========================================================
# HTTP DOWNLOAD
# =========================================================

async def _download(session, url: str):
    try:
        timeout = aiohttp.ClientTimeout(total=20)

        async with session.get(
            url,
            timeout=timeout,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/120 Safari/537.36"
                )
            },
        ) as resp:

            if resp.status == 200:
                data = await resp.read()

                if data:
                    return data

    except Exception:
        pass

    return None


# =========================================================
# GET YOUTUBE METADATA
# =========================================================

async def _get_youtube_metadata(session, videoid: str):
    """
    Gets metadata for the EXACT YouTube video.

    No YouTube search is performed.
    This prevents another video's title from appearing.
    """

    if not videoid:
        return None, None

    url = (
        "https://www.youtube.com/oembed"
        f"?url=https://www.youtube.com/watch?v={videoid}"
        "&format=json"
    )

    try:
        timeout = aiohttp.ClientTimeout(total=10)

        async with session.get(
            url,
            timeout=timeout,
            headers={
                "User-Agent": "Mozilla/5.0"
            },
        ) as resp:

            if resp.status != 200:
                return None, None

            data = await resp.json(content_type=None)

            title = data.get("title")
            author = data.get("author_name")

            if title:
                title = str(title).strip()

            if author:
                author = str(author).strip()

            return title, author

    except Exception:
        return None, None


# =========================================================
# LOAD FONT
# =========================================================

def _load_fonts():

    try:
        title_font = ImageFont.truetype(
            "ShiviMusic/assets/font2.ttf",
            32,
        )

        regular_font = ImageFont.truetype(
            "ShiviMusic/assets/font.ttf",
            18,
        )

        return title_font, regular_font

    except OSError:
        default = ImageFont.load_default()
        return default, default


# =========================================================
# LOAD ICONS
# =========================================================

def _paste_icons(bg):

    icons_path = "ShiviMusic/assets/play_icons.png"

    if not os.path.isfile(icons_path):
        return

    try:
        ic = Image.open(icons_path).resize(
            (ICONS_W, ICONS_H)
        ).convert("RGBA")

        r, g, b, a = ic.split()

        black_ic = Image.merge(
            "RGBA",
            (
                r.point(lambda _: 0),
                g.point(lambda _: 0),
                b.point(lambda _: 0),
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


# =========================================================
# MAIN THUMBNAIL FUNCTION
# =========================================================

async def get_thumb(
    videoid,
    user_id=None,
    title=None,
    artist=None,
):
    """
    Generate music player thumbnail.

    videoid:
        Exact YouTube video ID.

    title:
        Optional song title.
        If not supplied, exact YouTube video metadata is fetched.

    artist:
        Optional artist/channel name.
    """

    videoid = str(videoid or "").strip()

    # -----------------------------------------------------
    # CACHE
    # -----------------------------------------------------

    cache_name = (
        f"{videoid}_{CACHE_VERSION}.png"
        if videoid
        else f"default_{CACHE_VERSION}.png"
    )

    cache_path = os.path.join(
        CACHE_DIR,
        cache_name,
    )

    if os.path.isfile(cache_path):
        return cache_path

    # -----------------------------------------------------
    # THUMBNAIL URLS
    # -----------------------------------------------------

    thumbnail_urls = []

    if videoid:
        thumbnail_urls = [
            f"https://i.ytimg.com/vi/{videoid}/maxresdefault.jpg",
            f"https://i.ytimg.com/vi/{videoid}/sddefault.jpg",
            f"https://i.ytimg.com/vi/{videoid}/hqdefault.jpg",
        ]

    thumb_data = None

    # -----------------------------------------------------
    # DOWNLOAD THUMB + METADATA
    # -----------------------------------------------------

    async with aiohttp.ClientSession() as session:

        # Exact thumbnail
        for url in thumbnail_urls:

            thumb_data = await _download(
                session,
                url,
            )

            if thumb_data:
                break

        # Fallback image
        if not thumb_data:
            thumb_data = await _download(
                session,
                YOUTUBE_IMG_URL,
            )

        # -------------------------------------------------
        # GET EXACT SONG TITLE
        # -------------------------------------------------

        youtube_title = None
        youtube_artist = None

        if videoid and not title:

            (
                youtube_title,
                youtube_artist,
            ) = await _get_youtube_metadata(
                session,
                videoid,
            )

    # -----------------------------------------------------
    # IF THUMBNAIL FAILED
    # -----------------------------------------------------

    if not thumb_data:
        return YOUTUBE_IMG_URL

    # -----------------------------------------------------
    # SAVE TEMP IMAGE
    # -----------------------------------------------------

    temp_name = (
        f"thumb_{videoid or 'default'}_{CACHE_VERSION}.jpg"
    )

    thumb_path = os.path.join(
        CACHE_DIR,
        temp_name,
    )

    try:

        async with aiofiles.open(
            thumb_path,
            "wb",
        ) as f:

            await f.write(thumb_data)

        base = (
            Image.open(thumb_path)
            .convert("RGBA")
            .resize((1280, 720))
        )

    except Exception:

        try:
            os.remove(thumb_path)
        except OSError:
            pass

        return YOUTUBE_IMG_URL

    # -----------------------------------------------------
    # REMOVE TEMP IMAGE
    # -----------------------------------------------------

    try:
        os.remove(thumb_path)
    except OSError:
        pass

    # =====================================================
    # BACKGROUND
    # =====================================================

    bg = ImageEnhance.Brightness(
        base.filter(
            ImageFilter.BoxBlur(10)
        )
    ).enhance(0.6)

    # =====================================================
    # FROSTED PANEL
    # =====================================================

    panel_area = bg.crop(
        (
            PANEL_X,
            PANEL_Y,
            PANEL_X + PANEL_W,
            PANEL_Y + PANEL_H,
        )
    )

    overlay = Image.new(
        "RGBA",
        (PANEL_W, PANEL_H),
        (
            255,
            255,
            255,
            TRANSPARENCY,
        ),
    )

    frosted = Image.alpha_composite(
        panel_area,
        overlay,
    )

    mask = Image.new(
        "L",
        (PANEL_W, PANEL_H),
        0,
    )

    ImageDraw.Draw(mask).rounded_rectangle(
        (
            0,
            0,
            PANEL_W,
            PANEL_H,
        ),
        50,
        fill=255,
    )

    bg.paste(
        frosted,
        (
            PANEL_X,
            PANEL_Y,
        ),
        mask,
    )

    draw = ImageDraw.Draw(bg)

    # =====================================================
    # FONTS
    # =====================================================

    title_font, regular_font = _load_fonts()

    # =====================================================
    # MAIN THUMBNAIL
    # =====================================================

    thumb = base.resize(
        (
            THUMB_W,
            THUMB_H,
        )
    )

    tmask = Image.new(
        "L",
        thumb.size,
        0,
    )

    ImageDraw.Draw(tmask).rounded_rectangle(
        (
            0,
            0,
            THUMB_W,
            THUMB_H,
        ),
        20,
        fill=255,
    )

    bg.paste(
        thumb,
        (
            THUMB_X,
            THUMB_Y,
        ),
        tmask,
    )

    # =====================================================
    # SONG TITLE
    # =====================================================

    # Priority:
    #
    # 1. title passed by bot
    # 2. exact YouTube oEmbed title
    # 3. safe fallback
    #
    display_title = (
        str(title).strip()
        if title
        else youtube_title
    )

    if not display_title:
        display_title = "YouTube Music"

    display_title = trim_to_width(
        display_title,
        title_font,
        MAX_TITLE_WIDTH,
    )

    draw.text(
        (
            TITLE_X,
            TITLE_Y,
        ),
        display_title,
        fill="black",
        font=title_font,
    )

    # =====================================================
    # ARTIST / SOURCE
    # =====================================================

    display_artist = (
        str(artist).strip()
        if artist
        else youtube_artist
    )

    if not display_artist:
        display_artist = "YouTube"

    display_artist = trim_to_width(
        display_artist,
        regular_font,
        MAX_TITLE_WIDTH,
    )

    draw.text(
        (
            META_X,
            META_Y,
        ),
        display_artist,
        fill="black",
        font=regular_font,
    )

    # =====================================================
    # PROGRESS BAR
    # =====================================================

    draw.line(
        [
            (
                BAR_X,
                BAR_Y,
            ),
            (
                BAR_X + BAR_RED_LEN,
                BAR_Y,
            ),
        ],
        fill="red",
        width=6,
    )

    draw.line(
        [
            (
                BAR_X + BAR_RED_LEN,
                BAR_Y,
            ),
            (
                BAR_X + BAR_TOTAL_LEN,
                BAR_Y,
            ),
        ],
        fill="gray",
        width=5,
    )

    draw.ellipse(
        [
            (
                BAR_X + BAR_RED_LEN - 7,
                BAR_Y - 7,
            ),
            (
                BAR_X + BAR_RED_LEN + 7,
                BAR_Y + 7,
            ),
        ],
        fill="red",
    )

    # =====================================================
    # TIME
    # =====================================================

    draw.text(
        (
            BAR_X,
            BAR_Y + 15,
        ),
        "00:00",
        fill="black",
        font=regular_font,
    )

    # =====================================================
    # PLAYER ICONS
    # =====================================================

    _paste_icons(bg)

    # =====================================================
    # SAVE
    # =====================================================

    try:

        bg.save(
            cache_path,
            "PNG",
            optimize=True,
        )

        return cache_path

    except Exception:

        return YOUTUBE_IMG_URL
