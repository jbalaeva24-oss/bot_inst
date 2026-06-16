"""Генерация картинки-КП через Pillow."""
import io
import re

BG     = (15, 15, 25)
ACCENT = (99, 91, 255)
WHITE  = (255, 255, 255)
GRAY   = (170, 170, 190)
GREEN  = (60, 210, 110)
DARK   = (30, 30, 50)


def _strip_emoji(text: str) -> str:
    return re.sub(r'[^\x00-\x7FА-яЁёA-Za-z0-9 .,!?:;—\-+%₽\n/()»«]', '', text).strip()


def _font(size: int):
    from PIL import ImageFont
    try:
        # Пробуем системные шрифты Railway (Linux)
        for path in [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        ]:
            import os
            if os.path.exists(path):
                return ImageFont.truetype(path, size)
    except Exception:
        pass
    return ImageFont.load_default()


def make_offer_card(title: str, _unused: str, details: str, timeline: str) -> io.BytesIO:
    from PIL import Image, ImageDraw
    W, H = 900, 580
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # Акцентная полоса слева
    d.rectangle([0, 0, 8, H], fill=ACCENT)

    # Верхний блок фон
    d.rectangle([0, 0, W, 90], fill=DARK)

    f_title  = _font(30)
    f_body   = _font(20)
    f_small  = _font(17)

    # Заголовок
    d.text((30, 25), _strip_emoji(title), font=f_title, fill=WHITE)

    # Разделитель
    d.rectangle([30, 95, W - 30, 97], fill=ACCENT)

    # Детали
    y = 115
    for line in details.split("\n"):
        line = line.strip()
        if not line:
            y += 8
            continue
        clean = _strip_emoji(line)
        if not clean:
            continue
        is_check = line.startswith("✅")
        color = GREEN if is_check else GRAY
        prefix = "+ " if is_check else "  "
        d.text((30, y), prefix + clean, font=f_body, fill=color)
        y += 30

    # Нижняя полоса со сроком
    d.rectangle([0, H - 55, W, H], fill=DARK)
    d.rectangle([0, H - 57, W, H - 55], fill=ACCENT)
    tl = _strip_emoji(timeline) or timeline
    d.text((30, H - 38), f"Срок: {tl}", font=f_small, fill=GRAY)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf
