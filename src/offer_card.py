"""
Карточка КП в стиле сайта GK Pokraska:
светлый фон, золото, круглые чекмарки, чёткая типографика.
"""
import io, os, logging

log = logging.getLogger(__name__)

# ── Цвета сайта ──────────────────────────────────────────────────────────────
CREAM   = (252, 251, 248)   # фон — тёплый белый
WHITE   = (255, 255, 255)
GOLD    = (196, 148,  58)   # золото как на сайте
GOLD_L  = (220, 176,  80)   # золото светлее (hover)
GOLD_D  = (150, 110,  35)   # золото тёмное
DARK    = ( 18,  16,  12)   # почти чёрный для заголовков
CHAR    = ( 45,  42,  35)   # тёмно-коричневый для текста
GRAY1   = ( 90,  88,  80)   # серый текст
GRAY2   = (180, 178, 170)   # светлый серый
BGBAR   = ( 38,  34,  28)   # тёмная плашка статистики (как на сайте)
BGSUB   = (245, 243, 237)   # светлый блок фич


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
        str(config.BASE_DIR / "assets" / "Inter-SemiBold.ttf"),
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


def _gold_circle_check(img, cx, cy, r, line_w=2):
    """Рисует золотой круг с галочкой внутри — как на сайте."""
    from PIL import ImageDraw
    d = ImageDraw.Draw(img)
    # Круг
    d.ellipse([cx - r, cy - r, cx + r, cy + r],
              outline=GOLD, width=line_w, fill=None)
    # Галочка (два отрезка)
    gx, gy = cx, cy
    d.line([(gx - r//2, gy), (gx - r//6, gy + r//2)], fill=GOLD, width=line_w)
    d.line([(gx - r//6, gy + r//2), (gx + r//2, gy - r//2)], fill=GOLD, width=line_w)


def _shadow(d, x0, y0, x1, y1, r, layers=5):
    """Мягкая тень под карточкой."""
    for i in range(layers, 0, -1):
        alpha = 255 - i * 28
        shade = (alpha, alpha, alpha - 5)
        d.rounded_rectangle(
            [x0 + i, y0 + i, x1 + i, y1 + i],
            radius=r, fill=shade
        )


def make_offer_card(title: str, _unused: str, details: str, timeline: str) -> io.BytesIO:
    from PIL import Image, ImageDraw

    W, H = 1020, 580

    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # ── Тень карточки ────────────────────────────────────────────────────────
    CARD_M = 22          # отступ карточки от края
    R = 16               # радиус скругления
    _shadow(d, CARD_M, CARD_M, W - CARD_M, H - CARD_M, R, layers=6)

    # ── Белая карточка ───────────────────────────────────────────────────────
    d.rounded_rectangle([CARD_M, CARD_M, W - CARD_M, H - CARD_M],
                        radius=R, fill=WHITE)

    # ── Левая золотая полоса (3 px) — фирменный элемент ─────────────────────
    d.rectangle([CARD_M, CARD_M, CARD_M + 5, H - CARD_M], fill=GOLD)

    # ── ЛЕВАЯ КОЛОНКА: заголовок + цена ──────────────────────────────────────
    LEFT_W = 360
    LX = CARD_M + 36
    TOP = CARD_M + 30

    # Надпись-категория маленькими буквами
    f_cat   = _font(12, bold=True)
    f_name  = _font(26, bold=True)
    f_price = _font(40, bold=True)
    f_item  = _font(18)
    f_ibd   = _font(18, bold=True)
    f_small = _font(14)
    f_stat_n = _font(22, bold=True)
    f_stat_l = _font(11)

    d.text((LX, TOP), "КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ", font=f_cat, fill=GOLD)

    # Разбиваем title: "🌐 БАЗОВЫЙ САЙТ — 25 000 ₽"
    raw = _clean(title)
    # Убираем эмодзи-заглушку в начале (неCyrillic/non-ASCII слова)
    if raw and not raw[0].isalpha():
        raw = raw[1:].strip()
    # Делим на имя и цену по " - " или " -- "
    if ' - ' in raw:
        pkg_name, pkg_price = raw.split(' - ', 1)
    elif '--' in raw:
        pkg_name, pkg_price = raw.split('--', 1)
    else:
        pkg_name, pkg_price = raw, ''

    pkg_name  = pkg_name.strip()
    pkg_price = pkg_price.strip()

    # Золотая линия под категорией
    d.rectangle([LX, TOP + 20, LX + 180, TOP + 22], fill=GOLD)

    d.text((LX, TOP + 30), pkg_name, font=f_name, fill=DARK)

    # Цена — крупно, золотом
    if pkg_price:
        d.text((LX, TOP + 76), pkg_price, font=f_price, fill=GOLD)
    else:
        d.text((LX, TOP + 76), "Обсудим на созвоне", font=f_name, fill=GOLD)

    # Срок
    if timeline:
        tl = _clean(f"Срок: {timeline}")
        d.text((LX, TOP + 130), tl, font=f_small, fill=GRAY1)

    # Разделитель
    sep_x = CARD_M + LEFT_W + 20
    d.rectangle([sep_x, CARD_M + 20, sep_x + 1, H - CARD_M - 80],
                fill=(230, 228, 220))

    # ── ПРАВАЯ КОЛОНКА: фичи ─────────────────────────────────────────────────
    RX = sep_x + 28
    RY = CARD_M + 24
    COL_W = W - RX - CARD_M - 20

    items = [l.strip() for l in details.split("\n")
             if l.strip() and not l.startswith("⏱")]

    # 2 колонки если 5+
    cols = 2 if len(items) >= 5 else 1
    col_w = (COL_W - 20) // cols
    row_h = 48

    for i, line in enumerate(items[:8]):
        clean = _clean(line.replace("✅", "").replace("✓", "").strip())
        if not clean:
            continue
        col = i % cols
        row = i // cols
        ix = RX + col * (col_w + 20)
        iy = RY + row * row_h

        if iy + row_h > H - CARD_M - 85:
            break

        # Фоновый блок
        d.rounded_rectangle(
            [ix - 8, iy - 6, ix + col_w - 8, iy + 36],
            radius=10, fill=BGSUB
        )

        # Золотой круглый чекмарк
        _gold_circle_check(img, ix + 11, iy + 15, 10, line_w=2)

        # Текст
        d.text((ix + 28, iy + 6), clean, font=f_item, fill=CHAR)

    # ── Нижняя тёмная плашка (как stats bar на сайте) ────────────────────────
    BAR_Y = H - CARD_M - 62
    # Тёмный прямоугольник на всю ширину карточки
    d.rounded_rectangle(
        [CARD_M, BAR_Y, W - CARD_M, H - CARD_M],
        radius=R, fill=BGBAR
    )
    # Верхняя золотая линия у плашки
    d.rectangle([CARD_M, BAR_Y, W - CARD_M, BAR_Y + 2], fill=GOLD)

    # Три блока статистики как на сайте
    stats = [
        ("50% старт", "ПРЕДОПЛАТА"),
        ("50% сдача", "ОПЛАТА"),
        ("Гарантия", "РЕЗУЛЬТАТА"),
    ]
    sw = (W - CARD_M * 2) // len(stats)
    for i, (val, lbl) in enumerate(stats):
        sx = CARD_M + i * sw + sw // 2
        sy = BAR_Y + 12
        d.text((sx, sy), _clean(val), font=f_stat_n, fill=GOLD,
               anchor="mt" if hasattr(d, 'textlength') else None)
        d.text((sx, sy + 28), lbl, font=f_stat_l, fill=GRAY2,
               anchor="mt" if hasattr(d, 'textlength') else None)

    # Вертикальные разделители в плашке
    for i in range(1, len(stats)):
        dvx = CARD_M + i * sw
        d.rectangle([dvx, BAR_Y + 12, dvx + 1, H - CARD_M - 10],
                    fill=(70, 65, 55))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf
