"""Generate PWA icons."""
from PIL import Image, ImageDraw, ImageFont
import os

def make_icon(size, path):
    img = Image.new('RGBA', (size, size), (37, 99, 235, 255))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', size // 3)
    except:
        font = ImageFont.load_default()
    text = '✓'
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (size - tw) // 2 - bbox[0]
    y = (size - th) // 2 - bbox[1]
    draw.text((x, y), text, fill='white', font=font)
    img.save(path)
    print(f'Created {path} ({size}x{size})')

os.makedirs('/home/pi/dochazka/static', exist_ok=True)
make_icon(192, '/home/pi/dochazka/static/icon-192.png')
make_icon(512, '/home/pi/dochazka/static/icon-512.png')