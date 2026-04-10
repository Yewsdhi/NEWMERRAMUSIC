import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from youtubesearchpython.__future__ import VideosSearch

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ✦ IMAGE RESIZE (HD QUALITY)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def changeImageSize(maxWidth, maxHeight, image):
    return image.resize((maxWidth, maxHeight), Image.LANCZOS)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ✦ TITLE SPLITTER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def truncate(text):
    words = text.split(" ")
    text1, text2 = "", ""

    for word in words:
        if len(text1) + len(word) < 30:
            text1 += " " + word
        elif len(text2) + len(word) < 30:
            text2 += " " + word

    return [text1.strip(), text2.strip()]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ✦ CIRCLE CROP (SMOOTH)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def crop_center_circle(img, output_size=400):
    img = img.resize((output_size, output_size), Image.LANCZOS)

    mask = Image.new("L", (output_size, output_size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, output_size, output_size), fill=255)

    result = Image.new("RGBA", (output_size, output_size))
    result.paste(img, (0, 0), mask)
    return result


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ✦ MAIN THUMB FUNCTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def get_thumb(videoid):
    cache_path = f"cache/{videoid}.png"

    if os.path.isfile(cache_path):
        return cache_path

    url = f"https://www.youtube.com/watch?v={videoid}"
    search = VideosSearch(url, limit=1)
    data = await search.next()

    result = data["result"][0]

    # ━━━ SAFE DATA FETCH ━━━
    title = result.get("title", "Unknown Title")
    title = re.sub(r"\W+", " ", title).title()

    duration = result.get("duration", "0:00")
    views = result.get("viewCount", {}).get("short", "0 Views")
    channel = result.get("channel", {}).get("name", "Unknown")

    thumbnail = result["thumbnails"][0]["url"].split("?")[0]

    # ━━━ DOWNLOAD IMAGE ━━━
    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail) as resp:
            if resp.status != 200:
                return None
            img_data = await resp.read()

    temp_path = f"cache/temp_{videoid}.png"

    async with aiofiles.open(temp_path, "wb") as f:
        await f.write(img_data)

    # ━━━ IMAGE PROCESSING ━━━
    youtube = Image.open(temp_path).convert("RGBA")

    bg = changeImageSize(1280, 720, youtube)
    bg = bg.filter(ImageFilter.GaussianBlur(25))
    bg = ImageEnhance.Brightness(bg).enhance(0.5)

    draw = ImageDraw.Draw(bg)

    # ━━━ FONTS ━━━
    font_title = ImageFont.truetype("ShiviMusic/assets/assets/font3.ttf", 45)
    font_small = ImageFont.truetype("ShiviMusic/assets/assets/font2.ttf", 30)

    # ━━━ CIRCLE THUMB ━━━
    circle = crop_center_circle(youtube)
    bg.paste(circle, (100, 160), circle)

    # ━━━ TEXT ━━━
    text_x = 550
    t1, t2 = truncate(title)

    draw.text((text_x, 180), t1, fill="white", font=font_title)
    draw.text((text_x, 230), t2, fill="white", font=font_title)

    draw.text((text_x, 320), f"{channel} • {views}", fill="white", font=font_small)

    # ━━━ PROGRESS BAR ━━━
    bar_length = 600
    progress = int(bar_length * 0.6)

    draw.line((text_x, 380, text_x + progress, 380), fill="red", width=8)
    draw.line((text_x + progress, 380, text_x + bar_length, 380), fill="white", width=6)

    draw.ellipse(
        (text_x + progress - 8, 372, text_x + progress + 8, 388),
        fill="red"
    )

    draw.text((text_x, 400), "00:00", fill="white", font=font_small)
    draw.text((1100, 400), duration, fill="white", font=font_small)

    # ━━━ SAVE FINAL ━━━
    bg.save(cache_path)

    try:
        os.remove(temp_path)
    except:
        pass

    return cache_path
