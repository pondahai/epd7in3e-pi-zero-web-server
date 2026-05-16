import os
from PIL import Image, ImageEnhance

# 7.3inch e-Paper (E) Palette
# 0:Black, 1:White, 2:Yellow, 3:Red, 4:Black(Orange?), 5:Blue, 6:Green
EPD_PALETTE = [
    0, 0, 0,      # 0: Black
    255, 255, 255, # 1: White
    255, 255, 0,   # 2: Yellow
    255, 0, 0,     # 3: Red
    255, 128, 0,   # 4: Orange
    0, 0, 255,     # 5: Blue
    0, 255, 0      # 6: Green
]

def get_palette_image():
    pal_image = Image.new("P", (1, 1))
    # Fill up to 256 colors
    full_palette = EPD_PALETTE + [0, 0, 0] * (256 - len(EPD_PALETTE) // 3)
    pal_image.putpalette(full_palette)
    return pal_image

def process_image(input_path, output_path):
    # Open image
    img = Image.open(input_path)
    
    # 針對超大圖片進行初步縮放以節省記憶體
    if img.width > 2000 or img.height > 2000:
        img.thumbnail((1600, 1600))
    
    # 確保轉換為 RGB (處理 RGBA 或 P 模式)
    img = img.convert("RGB")
    
    # Resize to fit 800x480
    img = img.resize((800, 480), Image.Resampling.LANCZOS)
    
    # --- 影像增強處理 ---
    # 提高飽和度 (1.6倍)
    img = ImageEnhance.Color(img).enhance(1.6)
    
    # 提高對比度 (1.4倍)
    img = ImageEnhance.Contrast(img).enhance(1.4)
    
    # 稍微提高銳利度
    img = ImageEnhance.Sharpness(img).enhance(1.2)
    # ------------------
    
    # Quantize with Floyd-Steinberg dithering
    pal_img = get_palette_image()
    converted = img.quantize(palette=pal_img, dither=Image.Dither.FLOYDSTEINBERG)
    
    # Save preview image
    preview = converted.convert("RGB")
    # 強制指定儲存格式為 JPEG
    preview.save(output_path, format="JPEG", quality=90)
    return output_path
