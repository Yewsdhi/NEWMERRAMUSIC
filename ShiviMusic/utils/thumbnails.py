import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from py_yt import VideosSearch
from ShiviMusic import app
from config import YOUTUBE_IMG_URL

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# ---------------- IMAGE SIZE ---------------- #

def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    return image.resize((newWidth, newHeight))


# ---------------- TITLE TRUNCATE ---------------- #

def truncate(text):
    words = text.split(" ")
    text1 = ""
    text2 = ""

    for word in words:
        if len(text1) + len(word) < 30:
            text1 += " " + word
        elif len(text2) + len(word) < 30:
            text2 += " " + word

    return [text1.strip(), text2.strip()]


# ---------------- CIRCLE CROP ---------------- #

def crop_center_circle(img, size=400, border=20):
    img = img.resize((size, size))

    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)

    result = Image.new("RGBA", (size, size))
    result.paste(img, (0, 0), mask)

    return result


# ---------------- THUMB GENERATOR ---------------- #

async def get_thumb(videoid):

    final_path = f"{CACHE_DIR}/{videoid}_v4.png"

    if os.path.exists(final_path):
        return final_path

    url = f"https://www.youtube.com/watch?v={videoid}"
    results = VideosSearch(url, limit=1)

    data = (await results.next())["result"][0]

    title = re.sub("\W+", " ", data.get("title", "Unknown Title")).title()
    duration = data.get("duration", "Unknown")
    thumbnail = data["thumbnails"][0]["url"].split("?")[0]
    views = data.get("viewCount", {}).get("short", "Unknown Views")
    channel = data.get("channel", {}).get("name", "Unknown Channel")

    thumb_path = f"{CACHE_DIR}/{videoid}.png"

    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail) as resp:
            if resp.status == 200:
                async with aiofiles.open(thumb_path, mode="wb") as f:
                    await f.write(await resp.read())

    youtube = Image.open(thumb_path)

    image1 = changeImageSize(1280, 720, youtube)
    image2 = image1.convert("RGBA")

    background = image2.filter(ImageFilter.BoxBlur(20))
    background = ImageEnhance.Brightness(background).enhance(0.6)

    draw = ImageDraw.Draw(background)

    # ---------- FONTS ---------- #

    try:
        title_font = ImageFont.truetype("ShiviMusic/assets/assets/font3.ttf", 45)
        normal_font = ImageFont.truetype("ShiviMusic/assets/assets/font.ttf", 30)
    except:
        title_font = ImageFont.load_default()
        normal_font = ImageFont.load_default()

    # ---------- CIRCLE THUMB ---------- #

    circle = crop_center_circle(youtube, 400)
    background.paste(circle, (120, 160), circle)

    # ---------- TEXT ---------- #

    text_x = 565

    title1 = truncate(title)

    draw.text((text_x, 180), title1[0], fill="white", font=title_font)
    draw.text((text_x, 230), title1[1], fill="white", font=title_font)

    draw.text((text_x, 320), f"{channel} | {views}", fill="white", font=normal_font)

    # ---------- PROGRESS BAR ---------- #

    draw.line((text_x, 380, text_x + 350, 380), fill="red", width=9)
    draw.line((text_x + 350, 380, text_x + 580, 380), fill="white", width=8)

    draw.text((text_x, 400), "00:00", fill="white", font=normal_font)
    draw.text((1080, 400), duration, fill="white", font=normal_font)

    # ---------- WATERMARK ---------- #

    watermark = "Powered by Badnam OP"

    bbox = draw.textbbox((0, 0), watermark, font=normal_font)
    text_width = bbox[2] - bbox[0]

    x = 1280 - text_width - 20
    y = 680

    draw.text((x, y), watermark, fill=(255, 0, 0), font=normal_font)

    # ---------- SAVE ---------- #

    background.save(final_path)

    try:
        os.remove(thumb_path)
    except:
        pass

    return final_path
