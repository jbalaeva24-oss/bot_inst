"""
Карточка КП — премиальный тёмный дизайн с паттерном.
Стиль: GK Pokraska — тёмный фон, золото, точечный узор.
"""
import io, os, logging, math

log = logging.getLogger(__name__)

GOLD   = (196, 148,  58)
GOLD_L = (230, 185,  90)
GOLD_D = (140, 104,  32)
DARK   = ( 18,  15,  10)
DARK2  = ( 28,  24,  16)
DARK3  = ( 40,  35,  22)
WHITE  = (255, 255, 255)
OFFWH  = (235, 230, 215)
LGRAY  = (170, 160, 135)
GREEN  = ( 52, 211, 120)


def _font(size: int, bold: bool = False):
    from PIL import ImageFont
    import config
    cands = []
    if bold:
        cands += [str(config.BASE_DIR / "assets" / "Inter-Bold.ttf"),
                  str(config.BASE_DIR / "assets" / "Montserrat-Bold.ttf")]
    cands += [str(config.BASE_DIR / "assets" / "Inter-SemiBold.ttf"),
              str(config.BASE_DIR / "assets" / "Inter-Regular.ttf"),
              str(config.BASE_DIR / "assets" / "Montserrat-Regular.ttf"),
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for p in cands:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def _clean(text: str) -> str:
    out = []
    for ch in text:
        cp = ord(ch)
        if (32 <= cp <= 126) or (0x400 <= cp <= 0x4FF) or cp == 0x20BD:
            out.append(ch)
        elif ch in ('—', '–'):
            out.append('-')
    return ''.join(out).strip()


def _vgrad(img, x0, y0, x1, y1, top_c, bot_c):
    from PIL import ImageDraw
    d = ImageDraw.Draw(img)
    h = y1 - y0
    for i in range(h):
        t = i / max(h - 1, 1)
        c = tuple(int(top_c[j] + (bot_c[j] - top_c[j]) * t) for j in range(3))
        d.line([(x0, y0 + i), (x1, y0 + i)], fill=c)


def _dot_pattern(img, x0, y0, x1, y1, step=28, r=1, color=(50, 44, 28)):
    from PIL import ImageDraw
    d = ImageDraw.Draw(img)
    for gx in range(x0, x1, step):
        for gy in range(y0, y1, step):
            d.ellipse([gx - r, gy - r, gx + r, gy + r], fill=color)


def _gold_check(d, cx, cy, radius=10, lw=2):
    """Золотой круг с галочкой."""
    d.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
              outline=GOLD, width=lw)
    # галочка
    d.line([(cx - 5, cy), (cx - 1, cy + 5)], fill=GOLD, width=lw)
    d.line([(cx - 1, cy + 5), (cx + 6, cy - 4)], fill=GOLD, width=lw)


def _diamond_deco(d, cx, cy, size, color, width=2):
    """Декоративный ромб."""
    pts = [(cx, cy - size), (cx + size, cy), (cx, cy + size), (cx - size, cy)]
    d.polygon(pts, outline=color, fill=None)
    inner = int(size * 0.55)
    pts2 = [(cx, cy - inner), (cx + inner, cy), (cx, cy + inner), (cx - inner, cy)]
    d.polygon(pts2, outline=color, fill=None)


def make_offer_card(title: str, _unused: str, details: str, timeline: str) -> io.BytesIO:
    from PIL import Image, ImageDraw

    W, H = 1040, 600

    # ── 1. Фоновый градиент ──────────────────────────────────────────────────
    img = Image.new("RGB", (W, H), DARK)
    _vgrad(img, 0, 0, W, H, (24, 20, 13), (12, 10, 6))

    d = ImageDraw.Draw(img)

    # ── 2. Точечный паттерн на весь фон ──────────────────────────────────────
    _dot_pattern(img, 0, 0, W, H, step=30, r=1, color=(48, 42, 26))

    # ── 3. Большой декоративный круг (фоновый) ───────────────────────────────
    cx_deco, cy_deco = W - 160, 60
    for ri in range(180, 0, -30):
        alpha = max(8, 28 - ri // 10)
        shade = tuple(min(255, DARK2[j] + alpha) for j in range(3))
        d.ellipse([cx_deco - ri, cy_deco - ri, cx_deco + ri, cy_deco + ri],
                  outline=shade, width=1)

    # ── 4. Левая вертикальная золотая полоса ─────────────────────────────────
    for xi in range(6):
        t = xi / 5
        shade = tuple(int(GOLD[j] * (1 - t * 0.4)) for j in range(3))
        d.rectangle([xi, 0, xi, H], fill=shade)

    # ── 5. Верхняя горизонтальная золотая линия ───────────────────────────────
    d.rectangle([0, 0, W, 3], fill=GOLD)

    # ── 6. ЛЕВАЯ ПАНЕЛЬ (380 px) — имя + цена ────────────────────────────────
    LP = 380
    LX = 36
    LY = 38

    f_tag   = _font(11, bold=True)
    f_name  = _font(25, bold=True)
    f_price = _font(46, bold=True)
    f_small = _font(14)
    f_feat  = _font(17)
    f_featb = _font(17, bold=True)
    f_stat  = _font(20, bold=True)
    f_statl = _font(10)

    # Бейдж
    tag_text = "КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ"
    d.text((LX, LY), tag_text, font=f_tag, fill=GOLD)
    d.rectangle([LX, LY + 16, LX + 200, LY + 17], fill=GOLD_D)

    # Название пакета
    raw = _clean(title)
    if raw and not (raw[0].isalpha() or raw[0] in 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'):
        raw = raw[2:].strip()
    pkg_name, pkg_price = (raw.split(' - ', 1) if ' - ' in raw
                           else (raw.split('--', 1) if '--' in raw else (raw, '')))
    pkg_name  = pkg_name.strip()
    pkg_price = pkg_price.strip()

    d.text((LX, LY + 24), pkg_name, font=f_name, fill=WHITE)

    # Цена крупно + золотом
    d.text((LX, LY + 68), pkg_price or "По запросу", font=f_price, fill=GOLD)

    # Тонкая разделительная линия
    line_y = LY + 128
    d.rectangle([LX, line_y, LX + 290, line_y + 1], fill=DARK3)

    # Срок
    if timeline:
        d.text((LX, line_y + 10), _clean(f"Срок: {timeline}"),
               font=f_small, fill=LGRAY)

    # Декоративный ромб внизу левой панели
    _diamond_deco(d, 60, H - 110, 36, GOLD_D, width=1)
    _diamond_deco(d, 60, H - 110, 60, (35, 30, 18), width=1)

    # ── 7. Вертикальный разделитель панелей ──────────────────────────────────
    SEP_X = LP + 10
    for xi in range(2):
        d.rectangle([SEP_X + xi, 20, SEP_X + xi, H - 70],
                    fill=GOLD_D if xi == 0 else DARK3)

    # ── 8. ПРАВАЯ ПАНЕЛЬ — фичи ──────────────────────────────────────────────
    RX = SEP_X + 28
    RW = W - RX - 20

    items = [l.strip() for l in details.split("\n")
             if l.strip() and not l.startswith("⏱")]

    # Заголовок раздела
    d.text((RX, 32), "Что входит в пакет:", font=f_small, fill=LGRAY)

    cols  = 2 if len(items) >= 4 else 1
    col_w = (RW - 16) // cols
    row_h = 56
    ry0   = 60

    for i, line in enumerate(items[:8]):
        clean = _clean(line.replace("✅", "").replace("✓", "").strip())
        if not clean:
            continue
        col = i % cols
        row = i // cols
        ix  = RX + col * (col_w + 16)
        iy  = ry0 + row * row_h

        if iy + row_h > H - 90:
            break

        # Фон блока — чуть светлее
        d.rounded_rectangle(
            [ix - 6, iy - 8, ix + col_w - 10, iy + 38],
            radius=8, fill=DARK2
        )
        # Золотая левая полоска блока
        d.rectangle([ix - 6, iy - 8, ix - 3, iy + 38], fill=GOLD_D)

        # Чекмарк
        _gold_check(d, ix + 14, iy + 15, radius=10, lw=2)

        # Текст
        d.text((ix + 30, iy + 6), clean, font=f_feat, fill=OFFWH)

    # ── 9. Нижняя тёмная плашка (stats bar) ──────────────────────────────────
    BAR_H = 65
    BAR_Y = H - BAR_H
    _vgrad(img, 0, BAR_Y, W, H, (30, 25, 15), (20, 16, 8))
    d = ImageDraw.Draw(img)
    d.rectangle([0, BAR_Y, W, BAR_Y + 2], fill=GOLD)

    stats = [
        ("50% СТАРТ",   "Предоплата"),
        ("50% СДАЧА",   "При приёмке"),
        ("ГАРАНТИЯ",    "Результата"),
    ]
    sw = W // len(stats)
    for i, (val, lbl) in enumerate(stats):
        sx = i * sw + sw // 2
        sy = BAR_Y + 10
        # Значение
        tw = d.textlength(val, font=f_stat) if hasattr(d, 'textlength') else len(val) * 12
        d.text((sx - tw // 2, sy), val, font=f_stat, fill=GOLD)
        # Подпись
        tw2 = d.textlength(lbl, font=f_statl) if hasattr(d, 'textlength') else len(lbl) * 7
        d.text((sx - tw2 // 2, sy + 26), lbl, font=f_statl, fill=LGRAY)
        # Разделитель
        if i > 0:
            d.rectangle([i * sw - 1, BAR_Y + 14, i * sw, H - 12], fill=DARK3)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf
