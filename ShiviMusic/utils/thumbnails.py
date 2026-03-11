import os
import re
import aiohttp
import aiofiles
import random
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from py_yt import VideosSearch
from config import YOUTUBE_IMG_URL
from ShiviMusic import app

# --- Lund -- ---
FONT_PATH = "ShiviMusic/assets/font.ttf"
FONT2_PATH = "ShiviMusic/assets/font2.ttf"
CACHE_DIR = "cache"

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

# --- Loda le lo kidz ---

def create_rounded_box_mask(size, radius):
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0) + size, radius=radius, fill=255)
    return mask

def create_gradient_placeholder(width, height):
    base = Image.new('RGB', (width, height), (0, 0, 0))
    top = (random.randint(100, 255), random.randint(50, 200), random.randint(100, 255))
    bottom = (random.randint(50, 200), random.randint(100, 255), random.randint(50, 200))
    
    for y in range(height):
        r = int(top[0] + (bottom[0] - top[0]) * y / height)
        g = int(top[1] + (bottom[1] - top[1]) * y / height)
        b = int(top[2] + (bottom[2] - top[2]) * y / height)
        ImageDraw.Draw(base).line([(0, y), (width, y)], fill=(r, g, b))
    return base.convert("RGBA")

def generate_noise_texture(width, height, opacity=15):
    noise = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
    noise_img = Image.fromarray(noise, 'RGB').convert('RGBA')
    noise_img.putalpha(opacity)
    return noise_img

async def gen_thumb(videoid):
    output_path = f"{CACHE_DIR}/{videoid}_glass_fix.png"
    if os.path.isfile(output_path):
        return output_path

    url = f"https://www.youtube.com/watch?v={videoid}"

    try:
        # --- 1. GET VIDEO DETAILS ---
        search = VideosSearch(url, limit=1)
        try:
            results = await search.next()
        except TypeError:
            results = search.result()

        if not results or "result" not in results or not results["result"]:
            return YOUTUBE_IMG_URL

        r0 = results["result"][0]
        title = r0.get("title", "Unknown Title")
        duration = r0.get("duration", "00:00")
        
        view_info = r0.get("viewCount", {})
        if isinstance(view_info, dict):
            views = view_info.get("short", "0").split(" ")[0] 
        else:
            views = str(view_info)

        channel_info = r0.get("channel", {})
        if isinstance(channel_info, dict):
            channel_name = channel_info.get("name", "Unknown Channel")
        else:
            channel_name = str(channel_info)

        thumb_field = r0.get("thumbnails") or r0.get("thumbnail") or []
        thumbnail_url = ""
        if isinstance(thumb_field, list) and thumb_field:
            thumbnail_url = thumb_field[-1].get("url", "").split("?")[0]
        elif isinstance(thumb_field, dict):
            thumbnail_url = thumb_field.get("url", "").split("?")[0]
        
        if not thumbnail_url:
            return YOUTUBE_IMG_URL

        # --- 2. DOWNLOAD IMAGE ---
        raw_path = f"{CACHE_DIR}/raw_{videoid}.jpg"
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail_url) as resp:
                if resp.status == 200:
                    async with aiofiles.open(raw_path, "wb") as f:
                        await f.write(await resp.read())
                else:
                    return YOUTUBE_IMG_URL

        # --- 3. CREATE THUMBNAIL ---
        canvas_w, canvas_h = 1920, 1080
        
        try:
            original_img = Image.open(raw_path).convert("RGBA")
        except:
            original_img = create_gradient_placeholder(500, 500)

        # > VIBRANT BACKGROUND
        bg_img = original_img.copy().resize((canvas_w, canvas_h), Image.Resampling.LANCZOS)
        bg_img = ImageEnhance.Color(bg_img).enhance(1.4) 
        bg_img = bg_img.filter(ImageFilter.GaussianBlur(radius=80)) 
        bg_img = ImageEnhance.Brightness(bg_img).enhance(0.6) 
        
        canvas = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 255))
        canvas.paste(bg_img, (0, 0))
        
        # Noise Texture
        noise_tex = generate_noise_texture(canvas_w, canvas_h, opacity=20)
        canvas.paste(noise_tex, (0,0), noise_tex)

        # > THEME COLOR
        try:
            theme_color = original_img.resize((1, 1)).getpixel((0, 0))
            theme_color = tuple(min(c + 80, 255) for c in theme_color)
        except:
            theme_color = (random.randint(100, 255), random.randint(100, 255), random.randint(200, 255))

        # > CARD DIMENSIONS
        card_w, card_h = 1100, 380
        card_x = (canvas_w - card_w) // 2
        card_y = (canvas_h - card_h) // 2
        card_radius = 40

        # > GLOW (Backlight)
        glow_layer = Image.new('RGBA', (canvas_w, canvas_h), (0,0,0,0))
        glow_draw = ImageDraw.Draw(glow_layer)
        for i in range(30):
            offset = (30 - i) * 3
            opacity = (i + 1) * 2
            glow_col = (theme_color[0], theme_color[1], theme_color[2], opacity)
            glow_draw.rounded_rectangle(
                [card_x - offset, card_y - offset, card_x + card_w + offset, card_y + card_h + offset],
                radius=card_radius + offset, outline=glow_col, width=5
            )
        canvas.paste(glow_layer, (0,0), glow_layer)

        
        card_img = Image.new('RGBA', (card_w, card_h), (0,0,0,0))
        card_draw = ImageDraw.Draw(card_img)
        
        
        card_draw.rounded_rectangle(
            [0, 0, card_w, card_h], 
            radius=card_radius, 
            fill=(10, 10, 15, 160), 
            outline=(255, 255, 255, 40), 
            width=2
        )
        
        # --- 4. CONTENT ---
        try:
            title_font = ImageFont.truetype(FONT_PATH, 45)
            artist_font = ImageFont.truetype(FONT2_PATH, 30)
            meta_font = ImageFont.truetype(FONT2_PATH, 24)
            time_font = ImageFont.truetype(FONT2_PATH, 22)
            powered_font = ImageFont.truetype(FONT2_PATH, 30)
        except:
            title_font = artist_font = meta_font = time_font = powered_font = ImageFont.load_default()

        # > Album Art
        thumb_size = 300
        thumb_pad = 40
        thumb_x = thumb_pad
        thumb_y = (card_h - thumb_size) // 2
        
        label_thumb = original_img.resize((thumb_size, thumb_size), Image.Resampling.LANCZOS)
        label_mask = create_rounded_box_mask((thumb_size, thumb_size), radius=25)
        card_img.paste(label_thumb, (thumb_x, thumb_y), label_mask)

        # > Text
        text_x = thumb_x + thumb_size + 45
        text_y = thumb_y + 15
        
        clean_title = re.sub(r'[^\w\s\-\.\,\!\?\'\"]', '', title)
        if len(clean_title) > 28: clean_title = clean_title[:25] + "..."
        card_draw.text((text_x, text_y), clean_title, font=title_font, fill=(255, 255, 255))
        
        text_y += 60
        if len(channel_name) > 35: channel_name = channel_name[:32] + "..."
        card_draw.text((text_x, text_y), channel_name, font=artist_font, fill=(220, 220, 220))
        
        text_y += 50
        meta_text = f"👁 {views} Views • ⏱ {duration}"
        card_draw.text((text_x, text_y), meta_text, font=meta_font, fill=(180, 180, 180))

        # > Progress Bar
        bar_x = text_x
        bar_y = text_y + 80
        bar_w = card_w - bar_x - 40
        bar_h = 8
        
       
        card_draw.rounded_rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + bar_h], radius=bar_h//2, fill=(200, 200, 200, 50))
        active_w = int(bar_w * 0.3)
        card_draw.rounded_rectangle([bar_x, bar_y, bar_x + active_w, bar_y + bar_h], radius=bar_h//2, fill=(255, 255, 255))
       
        kx = bar_x + active_w
        ky = bar_y + bar_h // 2
        card_draw.ellipse([kx - 8, ky - 8, kx + 8, ky + 8], fill=theme_color)

        # Timestamps
        card_draw.text((bar_x, bar_y + 15), "00:00", font=time_font, fill=(255, 255, 255))
        try:
            d_len = card_draw.textlength(duration, font=time_font)
        except:
            d_len = 40
        card_draw.text((bar_x + bar_w - d_len, bar_y + 15), duration, font=time_font, fill=(255, 255, 255))

        canvas.paste(card_img, (card_x, card_y), card_img)

        # > Powered By
        draw = ImageDraw.Draw(canvas)
        powered_text = "SHIVI MUSIC"
        try:
            pow_w = draw.textlength(powered_text, font=powered_font)
        except:
            pow_w = 300
        
        pow_x = canvas_w - pow_w - 60
        pow_y = canvas_h - 80
        
        draw.text((pow_x + 2, pow_y + 2), powered_text, font=powered_font, fill=(0,0,0,200))
        draw.text((pow_x, pow_y), powered_text, font=powered_font, fill=(255, 255, 255, 200))

        # Save
        canvas = canvas.convert('RGB')
        canvas.save(output_path, format="PNG", quality=100)
        
        if os.path.exists(raw_path):
            os.remove(raw_path)
            
        return output_path

    except Exception as e:
        print(f"[gen_thumb Error] {e}")
        import traceback
        traceback.print_exc()
        return YOUTUBE_IMG_URL

