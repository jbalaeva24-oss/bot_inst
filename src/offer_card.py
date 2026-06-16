"""Генерация карточки КП в стиле премиального сайта."""
import io, os, logging, re

log = logging.getLogger(__name__)

# ── Цвета ────────────────────────────────────────────────────────────────────
WHITE   = (255, 255, 255)
BGLIGHT = (248, 248, 252)   # очень светлый фон
BGCARD  = (255, 255, 255)   # карточка
BORDER  = (230, 228, 245)   # граница
PUR1    = ( 99,  91, 255)   # фиолетовый основной
PUR2    = ( 75,  68, 204)   # фиолетовый тёмный
PUR3    = (130, 120, 255)   # фиолетовый светлый
DARK    = ( 18,  17,  35)   # почти чёрный текст
GRAY1   = ( 90,  88, 110)   # серый текст
GRAY2   = (165, 163, 185)   # светлый серый
GREEN   = ( 34, 197,  94)   # зелёный для галочек
LGPUR   = (245, 244, 255)   # очень светло-фиолетовый (фон фич)


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
        str(config.BASE_DIR / "assets" / "Inter-SemiBold.ttf"),
        str(config.BASE_DIR / "assets" / "Montserrat-Regular.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception as e:
                log.warning("font %s: %s", path, e)
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
        elif ch in ('—', '–'):
            result.append('-')
        elif ch == '→':
            result.append('>')
    return ''.join(result).strip()


def _gradient_rect(img, x0, y0, x1, y1, color_top, color_bot):
    """Вертикальный градиент через построчный рисунок."""
    from PIL import ImageDraw
    d = ImageDraw.Draw(img)
    h = y1 - y0
    for i in range(h):
        t = i / max(h - 1, 1)
        r = int(color_top[0] + (color_bot[0] - color_top[0]) * t)
        g = int(color_top[1] + (color_bot[1] - color_top[1]) * t)
        b = int(color_top[2] + (color_bot[2] - color_top[2]) * t)
        d.line([(x0, y0 + i), (x1, y0 + i)], fill=(r, g, b))


def _round_rect(d, xy, r, fill, outline=None, outline_w=2):
    x0, y0, x1, y1 = xy
    d.rectangle([x0 + r, y0, x1 - r, y1], fill=fill)
    d.rectangle([x0, y0 + r, x1, y1 - r], fill=fill)
    for cx, cy in [(x0, y0), (x1 - 2*r, y0), (x0, y1 - 2*r), (x1 - 2*r, y1 - 2*r)]:
        d.ellipse([cx, cy, cx + 2*r, cy + 2*r], fill=fill)
    if outline:
        d.rounded_rectangle([x0, y0, x1, y1], radius=r, outline=outline, width=outline_w)


def make_offer_card(title: str, _unused: str, details: str, timeline: str) -> io.BytesIO:
    from PIL import Image, ImageDraw

    W, H = 1000, 600
    RADIUS = 18
    PAD = 32

    # ── Основной холст ───────────────────────────────────────────────────────
    img = Image.new("RGB", (W, H), BGLIGHT)
    d = ImageDraw.Draw(img)

    # Тень карточки (несколько прямоугольников со смещением)
    for sh in range(6, 0, -1):
        shade = 245 - sh * 3
        d.rounded_rectangle(
            [PAD + sh, PAD + sh, W - PAD + sh, H - PAD + sh],
            radius=RADIUS, fill=(shade, shade, shade + 5)
        )

    # ── Карточка (белый фон) ─────────────────────────────────────────────────
    d.rounded_rectangle([PAD, PAD, W - PAD, H - PAD], radius=RADIUS, fill=BGCARD)

    # ── Градиентный хедер ───────────────────────────────────────────────────
    HEADER_H = 175
    # Рисуем градиент поверх, потом маскируем углы
    _gradient_rect(img, PAD, PAD, W - PAD, PAD + HEADER_H, PUR1, PUR2)

    # Закруглённые верхние углы (перерисовываем)
    d = ImageDraw.Draw(img)
    # Верхние углы градиентные
    corner_img = Image.new("RGB", (W, H), BGCARD)
    _gradient_rect(corner_img, PAD, PAD, W - PAD, PAD + HEADER_H, PUR1, PUR2)
    corner_d = ImageDraw.Draw(corner_img)

    # Белые треугольники в углах (чтобы скрыть лишнее)
    d.rounded_rectangle(
        [PAD, PAD, W - PAD, PAD + HEADER_H + RADIUS],
        radius=RADIUS, fill=None, outline=None
    )

    # Перерисовываем градиент через маску
    mask = Image.new("L", (W, H), 0)
    mask_d = ImageDraw.Draw(mask)
    mask_d.rounded_rectangle([PAD, PAD, W - PAD, PAD + HEADER_H], radius=RADIUS, fill=255)
    mask_d.rectangle([PAD, PAD + HEADER_H - RADIUS, W - PAD, PAD + HEADER_H], fill=255)

    grad_layer = Image.new("RGB", (W, H), BGCARD)
    _gradient_rect(grad_layer, PAD, PAD, W - PAD, PAD + HEADER_H, PUR1, PUR2)
    img.paste(grad_layer, mask=mask)

    d = ImageDraw.Draw(img)

    # ── Декоративные круги в хедере ─────────────────────────────────────────
    d.ellipse([W - 180, PAD - 40, W + 20, PAD + 160], fill=PUR3, outline=None)
    d.ellipse([W - 130, PAD - 70, W + 50, PAD + 110], fill=PUR1, outline=None)
    # Перекрываем выход за пределы карточки
    d.rectangle([W - PAD, 0, W, H], fill=BGLIGHT)
    d.rectangle([0, 0, W, PAD], fill=BGLIGHT)

    # Снова рисуем границу карточки поверх
    d.rounded_rectangle([PAD, PAD, W - PAD, H - PAD], radius=RADIUS,
                         fill=None, outline=BORDER, width=2)

    # ── Тег в хедере ────────────────────────────────────────────────────────
    f_tag   = _font(13, bold=True)
    f_title = _font(28, bold=True)
    f_price = _font(36, bold=True)
    f_item  = _font(19)
    f_check = _font(19, bold=True)
    f_small = _font(15)
    f_time  = _font(16, bold=True)

    # Бейдж "КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ"
    tag_text = "КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ"
    tw = d.textlength(tag_text, font=f_tag) if hasattr(d, 'textlength') else 240
    badge_x, badge_y = PAD + 28, PAD + 22
    d.rounded_rectangle(
        [badge_x - 10, badge_y - 5, badge_x + tw + 10, badge_y + 20],
        radius=10, fill=(255, 255, 255, 40)
    )
    # Белый полупрозрачный эффект: просто рисуем тёмный бейдж
    d.rounded_rectangle(
        [badge_x - 10, badge_y - 5, badge_x + tw + 10, badge_y + 20],
        radius=10, fill=(80, 70, 200)
    )
    d.text((badge_x, badge_y), tag_text, font=f_tag, fill=(220, 215, 255))

    # Название пакета (без эмодзи и цены)
    raw_title = _clean(title)
    # Отделяем название от цены  "БАЗОВЫЙ САЙТ - 25 000 р"
    parts = raw_title.split(" - ", 1) if " - " in raw_title else raw_title.split("  ", 1)
    pkg_name  = parts[0].strip()
    pkg_price = parts[1].strip() if len(parts) > 1 else ""

    d.text((PAD + 28, PAD + 58), pkg_name, font=f_title, fill=WHITE)
    if pkg_price:
        d.text((PAD + 28, PAD + 100), pkg_price, font=f_price, fill=(255, 230, 100))

    # Срок в хедере справа
    if timeline:
        tl = _clean(f"Срок: {timeline}")
        d.rounded_rectangle(
            [W - PAD - 200, PAD + 105, W - PAD - 28, PAD + 138],
            radius=20, fill=(80, 70, 200)
        )
        d.text((W - PAD - 190, PAD + 111), tl, font=f_time, fill=(220, 215, 255))

    # ── Список фич ──────────────────────────────────────────────────────────
    items = [l.strip() for l in details.split("\n") if l.strip() and not l.startswith("⏱")]

    # Раскладываем в 2 колонки если фич много
    col_count = 2 if len(items) >= 5 else 1
    col_w = (W - PAD * 2 - 60) // col_count
    content_y = PAD + HEADER_H + 22
    content_x = PAD + 30

    for i, line in enumerate(items[:8]):
        clean = _clean(line.replace("✅", "").strip())
        if not clean:
            continue

        if col_count == 2:
            col = i % 2
            row = i // 2
            ix = content_x + col * (col_w + 20)
            iy = content_y + row * 46
        else:
            ix = content_x
            iy = content_y + i * 46

        if iy > H - PAD - 60:
            break

        # Фоновый блок фичи
        d.rounded_rectangle(
            [ix - 12, iy - 8, ix + col_w, iy + 30],
            radius=10, fill=LGPUR
        )
        # Зелёная галочка
        d.text((ix, iy), "+", font=f_check, fill=GREEN)
        # Текст
        d.text((ix + 26, iy + 1), clean, font=f_item, fill=DARK)

    # ── Нижняя строка ───────────────────────────────────────────────────────
    footer_y = H - PAD - 38
    d.line([(PAD + 20, footer_y - 12), (W - PAD - 20, footer_y - 12)], fill=BORDER, width=1)
    d.text((PAD + 30, footer_y),
           "Оплата: 50% старт  •  50% при сдаче  •  Гарантия результата",
           font=f_small, fill=GRAY2)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf
