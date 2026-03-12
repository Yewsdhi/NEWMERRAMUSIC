import os
import re
import random
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from py_yt import VideosSearch
from config import YOUTUBE_IMG_URL
from ShiviMusic import app

WIDTH = 1280
HEIGHT = 720


def format_time(sec):
    m = sec // 60
    s = sec % 60
    return f"{m:02d}:{s:02d}"


def generate_player(title, channel, botname, duration, current, thumb_url):

    bg = Image.new("RGB", (WIDTH, HEIGHT), (255, 140, 0))
    draw = ImageDraw.Draw(bg)

    # download thumbnail
    r = requests.get(thumb_url)
    with open("thumb.jpg", "wb") as f:
        f.write(r.content)

    thumb = Image.open("thumb.jpg").resize((360, 360))
    bg.paste(thumb, (850, 170))

    try:
        title_font = ImageFont.truetype("ShiviMusic/assets/font.ttf", 80)
        small_font = ImageFont.truetype("ShiviMusic/assets/font.ttf", 45)
    except:
        title_font = small_font = ImageFont.load_default()

    # title
    draw.text((120, 220), title, fill="black", font=title_font)

    # channel
    draw.text(
        (120, 340),
        f"Channel: {channel}",
        fill="black",
        font=small_font
    )

    # bot
    draw.text(
        (120, 410),
        f"Playing on: @{botname}",
        fill="black",
        font=small_font
    )

    # progress bar
    bar_x = 120
    bar_y = 520
    bar_w = 650
    bar_h = 16

    progress = int((current / duration) * bar_w)

    draw.rectangle(
        (bar_x, bar_y, bar_x + bar_w, bar_y + bar_h),
        fill=(220, 220, 220)
    )

    draw.rectangle(
        (bar_x, bar_y, bar_x + progress, bar_y + bar_h),
        fill=(0, 0, 0)
    )

    draw.ellipse(
        (
            bar_x + progress - 10,
            bar_y - 6,
            bar_x + progress + 10,
            bar_y + 10
        ),
        fill="black"
    )

    draw.text(
        (120, 560),
        format_time(current),
        fill="black",
        font=small_font
    )

    draw.text(
        (720, 560),
        format_time(duration),
        fill="black",
        font=small_font
    )

    bg.save("player.png")

    return "player.png"
