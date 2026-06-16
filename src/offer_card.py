"""Генерация картинки-КП через Pillow."""
import io
from pathlib import Path
import config

FONT_DIR = config.BASE_DIR / "assets"

# Цвета
BG = (15, 15, 25)
ACCENT = (99, 91, 255)
WHITE = (255, 255, 255)
GRAY = (160, 160, 180)
GREEN = (50, 200, 100)


def _font(name: str, size: int):
    from PIL import ImageFont
    for fname in [f"Montserrat-{name}.ttf", f"Inter-{name}.ttf"]:
        p = FONT_DIR / fname
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def make_offer_card(title: str, price_line: str, details: str, timeline: str) -> io.BytesIO:
    from PIL import Image, ImageDraw
    W, H = 900, 600
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # Фоновый прямоугольник-акцент слева
    d.rectangle([0, 0, 6, H], fill=ACCENT)

    # Заголовок
    f_bold = _font("Bold", 36)
    f_semi = _font("SemiBold", 24)
    f_reg  = _font("Regular", 20)
    f_small = _font("Regular", 18)

    d.text((40, 40), title, font=f_bold, fill=WHITE)

    # Цена
    d.text((40, 100), price_line, font=f_semi, fill=ACCENT)

    # Разделитель
    d.rectangle([40, 145, W - 40, 147], fill=(40, 40, 60))

    # Детали — разбиваем по строкам
    y = 165
    for line in details.split("\n"):
        if not line.strip():
            y += 10
            continue
        color = GREEN if line.startswith("✅") else GRAY
        d.text((40, y), line, font=f_reg, fill=color)
        y += 32

    # Срок внизу
    d.rectangle([40, H - 70, W - 40, H - 68], fill=(40, 40, 60))
    d.text((40, H - 55), f"⏱  {timeline}", font=f_small, fill=GRAY)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    buf.seek(0)
    return buf
