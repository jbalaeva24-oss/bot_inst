"""Генерация премиальной картинки-КП через Pillow."""
import io, os, logging, re

log = logging.getLogger(__name__)

# Цветовая схема — тёмно-синяя с золотом
BG       = (10, 10, 20)
BG2      = (18, 18, 35)
GOLD     = (212, 175, 55)
GOLD2    = (255, 215, 80)
WHITE    = (255, 255, 255)
LGRAY    = (200, 200, 220)
MGRAY    = (140, 140, 165)
DARKLINE = (35, 35, 60)


def _font(size: int, bold: bool = False):
    from PIL import ImageFont
    import config
    candidates = []
    if bold:
        candidates += [
            str(config.BASE_DIR / "assets" / "Inter-Bold.ttf"),
            str(config.BASE_DIR / "assets" / "Montserrat-Bold.ttf"),
        ]
    candidates += [
        str(config.BASE_DIR / "assets" / "Inter-Regular.ttf"),
        str(config.BASE_DIR / "assets" / "Montserrat-Regular.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception as e:
                log.warning("font load %s: %s", path, e)
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def _clean(text: str) -> str:
    result = []
    for ch in text:
        cp = ord(ch)
        if (32 <= cp <= 126) or (0x400 <= cp <= 0x4FF) or cp == 0x20BD:
            result.append(ch)
        elif ch in ('→', '—', '–', '·'):
            result.append(ch if ch == '→' else '-')
    return ''.join(result).strip()


def _draw_rounded_rect(d, xy, r, fill):
    from PIL import ImageDraw
    x0, y0, x1, y1 = xy
    d.rectangle([x0 + r, y0, x1 - r, y1], fill=fill)
    d.rectangle([x0, y0 + r, x1, y1 - r], fill=fill)
    d.ellipse([x0, y0, x0 + 2*r, y0 + 2*r], fill=fill)
    d.ellipse([x1 - 2*r, y0, x1, y0 + 2*r], fill=fill)
    d.ellipse([x0, y1 - 2*r, x0 + 2*r, y1], fill=fill)
    d.ellipse([x1 - 2*r, y1 - 2*r, x1, y1], fill=fill)


def make_offer_card(title: str, _unused: str, details: str, timeline: str) -> io.BytesIO:
    from PIL import Image, ImageDraw
    W, H = 960, 580

    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # Фоновый прямоугольник чуть светлее
    d.rectangle([0, 0, W, H], fill=BG)

    # Левая золотая полоса (3px)
    d.rectangle([0, 0, 4, H], fill=GOLD)

    # Шапка с градиентным эффектом (3 полосы)
    for i, alpha in enumerate([35, 28, 20]):
        shade = tuple(min(255, c + alpha) for c in BG)
        d.rectangle([5, i * 30, W, 90 - i * 5], fill=shade)

    # Золотая декор-линия под шапкой
    d.rectangle([5, 90, W, 92], fill=GOLD)

    # Загружаем шрифты
    f_title  = _font(29, bold=True)
    f_badge  = _font(16, bold=True)
    f_item   = _font(20)
    f_small  = _font(17)

    # Значок-тег "КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ"
    tag_text = "КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ"
    _draw_rounded_rect(d, [20, 12, 340, 36], 6, DARKLINE)
    d.text((30, 14), _clean(tag_text), font=f_badge, fill=GOLD)

    # Заголовок (title)
    clean_title = _clean(title)
    d.text((20, 44), clean_title, font=f_title, fill=WHITE)

    # Пункты списка
    y = 108
    items = [l.strip() for l in details.split("\n") if l.strip()]
    items = [l for l in items if not l.startswith("⏱")]

    for line in items:
        if y > H - 80:
            break
        clean = _clean(line)
        if not clean:
            continue

        # Определяем иконку строки
        has_check = any(c in line for c in ("✅", "+", "•"))
        dot_color = GOLD if has_check else MGRAY
        text_color = LGRAY

        # Золотая точка-маркер
        d.ellipse([20, y + 7, 28, 15 + y], fill=dot_color)
        d.text((38, y), clean, font=f_item, fill=text_color)
        y += 34

    # Разделитель перед футером
    d.rectangle([5, H - 60, W, H - 58], fill=DARKLINE)

    # Футер с тёмным фоном
    d.rectangle([0, H - 57, W, H], fill=BG2)

    # Срок
    timeline_clean = _clean(f"Срок: {timeline}") if timeline else ""
    d.text((20, H - 40), timeline_clean, font=f_small, fill=MGRAY)

    # Золотой декор-уголок справа снизу
    for i in range(4):
        d.rectangle([W - 4 + i, H - 57, W, H], fill=GOLD)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf
