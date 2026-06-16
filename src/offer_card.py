"""
Карточка КП — премиальный тёмный дизайн.
Стиль: GK Pokraska — тёмный фон, золото, точечный узор.
"""
import io, os, logging

log = logging.getLogger(__name__)

GOLD   = (196, 148,  58)
GOLD_L = (230, 185,  90)
GOLD_D = (120,  88,  24)
DARK   = ( 16,  13,   8)
DARK2  = ( 28,  23,  13)
DARK3  = ( 42,  36,  20)
WHITE  = (255, 255, 255)
OFFWH  = (232, 226, 208)
LGRAY  = (155, 145, 118)
DLINE  = ( 55,  48,  28)


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


def _dot_pattern(img, x0, y0, x1, y1, step=32, r=1, color=(44, 38, 20)):
    from PIL import ImageDraw
    d = ImageDraw.Draw(img)
    for gx in range(x0, x1 + step, step):
        for gy in range(y0, y1 + step, step):
            d.ellipse([gx - r, gy - r, gx + r, gy + r], fill=color)


def _wrap_text(d, text, font, max_w):
    """Разбивает текст на строки по max_w пикселей."""
    words = text.split()
    lines, line = [], []
    for w in words:
        test = " ".join(line + [w])
        try:
            tw = d.textlength(test, font=font)
        except Exception:
            tw = len(test) * 9
        if tw <= max_w:
            line.append(w)
        else:
            if line:
                lines.append(" ".join(line))
            line = [w]
    if line:
        lines.append(" ".join(line))
    return lines


def _gold_check(d, cx, cy, r=9, lw=2):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GOLD, width=lw)
    d.line([(cx - 4, cy + 1), (cx - 1, cy + 4)], fill=GOLD, width=lw)
    d.line([(cx - 1, cy + 4), (cx + 5, cy - 3)], fill=GOLD, width=lw)


def make_offer_card(title: str, _unused: str, details: str, timeline: str) -> io.BytesIO:
    from PIL import Image, ImageDraw

    W, H = 1060, 600

    # ── 1. Градиентный фон ───────────────────────────────────────────────────
    img = Image.new("RGB", (W, H), DARK)
    _vgrad(img, 0, 0, W, H, (22, 18, 10), (10, 8, 4))

    # ── 2. Точечная сетка (паттерн) ──────────────────────────────────────────
    _dot_pattern(img, 0, 0, W, H, step=30, r=1, color=(42, 36, 18))

    d = ImageDraw.Draw(img)

    # ── 3. Декор: кольца в левом нижнем углу (не мешают тексту) ─────────────
    for ri in (160, 120, 85, 55, 30):
        opacity = max(18, 60 - ri // 3)
        shade = tuple(min(255, DARK[j] + opacity) for j in range(3))
        d.ellipse([-ri, H - ri, ri, H + ri], outline=shade, width=1)

    # ── 4. Декор: ромб в правом верхнем углу ─────────────────────────────────
    def diamond(cx, cy, s, col):
        d.polygon([(cx, cy - s), (cx + s, cy), (cx, cy + s), (cx - s, cy)],
                  outline=col, fill=None)
    diamond(W - 55, 55, 40, DARK3)
    diamond(W - 55, 55, 28, DLINE)
    diamond(W - 55, 55, 16, GOLD_D)

    # ── 5. Рамка всей карточки (тонкая золотая) ──────────────────────────────
    d.rounded_rectangle([0, 0, W - 1, H - 1], radius=0,
                        outline=GOLD_D, width=1)

    # ── 6. Золотая полоса сверху ──────────────────────────────────────────────
    for yi in range(4):
        t = yi / 3
        shade = tuple(int(GOLD[j] * (1 - t * 0.35)) for j in range(3))
        d.rectangle([0, yi, W, yi], fill=shade)

    # ── 7. Левая золотая полоса ───────────────────────────────────────────────
    for xi in range(5):
        t = xi / 4
        shade = tuple(int(GOLD[j] * (1 - t * 0.5)) for j in range(3))
        d.rectangle([xi, 0, xi, H], fill=shade)

    # ── 8. ЛЕВАЯ ПАНЕЛЬ — название + цена (360 px) ───────────────────────────
    LP   = 360   # ширина левой панели
    LX   = 32
    LY   = 36

    f_tag   = _font(10, bold=True)
    f_name  = _font(23, bold=True)
    f_price = _font(44, bold=True)
    f_small = _font(13)
    f_feat  = _font(16)
    f_stat  = _font(19, bold=True)
    f_statl = _font(10)

    # Бейдж-текст
    d.text((LX, LY), "КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ", font=f_tag, fill=GOLD)
    d.rectangle([LX, LY + 15, LX + 195, LY + 16], fill=GOLD_D)

    # Парсим название и цену
    raw = _clean(title)
    # Убираем нечитаемые символы в начале (эмодзи)
    while raw and not (raw[0].isalpha() or ord(raw[0]) >= 0x400):
        raw = raw[1:].strip()
    if ' - ' in raw:
        pkg_name, pkg_price = raw.split(' - ', 1)
    elif '--' in raw:
        pkg_name, pkg_price = raw.split('--', 1)
    else:
        pkg_name, pkg_price = raw, ''

    d.text((LX, LY + 24), pkg_name.strip(), font=f_name, fill=WHITE)
    d.text((LX, LY + 68), pkg_price.strip() or "По запросу",
           font=f_price, fill=GOLD)

    # Горизонтальный разделитель
    sep_y = LY + 130
    d.rectangle([LX, sep_y, LP - 20, sep_y + 1], fill=DLINE)

    # Срок
    if timeline:
        d.text((LX, sep_y + 10), _clean(f"Срок: {timeline}"),
               font=f_small, fill=LGRAY)

    # ── 9. Вертикальный разделитель ───────────────────────────────────────────
    SEP_X = LP + 14
    d.rectangle([SEP_X, 18, SEP_X + 1, H - 68], fill=DLINE)
    d.rectangle([SEP_X + 2, 18, SEP_X + 3, H - 68], fill=GOLD_D)

    # ── 10. ПРАВАЯ ПАНЕЛЬ — фичи ─────────────────────────────────────────────
    RX   = SEP_X + 22
    RW   = W - RX - 18   # доступная ширина

    items = [l.strip() for l in details.split("\n")
             if l.strip() and not l.startswith("⏱")]

    # Заголовок
    d.text((RX, 28), "Что входит в пакет:", font=f_small, fill=LGRAY)

    # Раскладка: 2 колонки, блок на каждую фичу с переносом текста
    cols   = 2
    col_w  = (RW - 14) // cols    # ширина одной колонки
    row_h  = 62                    # высота строки (с запасом на 2 строки)
    feat_x = [RX, RX + col_w + 14]
    feat_y = 56

    for i, line in enumerate(items[:8]):
        clean = _clean(line.replace("✅", "").replace("✓", "").strip())
        if not clean:
            continue

        col = i % cols
        row = i // cols
        ix  = feat_x[col]
        iy  = feat_y + row * row_h

        if iy + row_h > H - 78:
            break

        block_w = col_w - 4

        # Фон блока
        d.rounded_rectangle(
            [ix - 4, iy - 6, ix + block_w, iy + row_h - 10],
            radius=6, fill=DARK2
        )
        # Левая золотая линия блока
        d.rectangle([ix - 4, iy - 6, ix - 1, iy + row_h - 10], fill=GOLD_D)

        # Чекмарк
        _gold_check(d, ix + 12, iy + 15)

        # Текст с переносом
        text_x = ix + 28
        text_max_w = block_w - 30
        lines_wrap = _wrap_text(d, clean, f_feat, text_max_w)
        for li, wline in enumerate(lines_wrap[:2]):
            d.text((text_x, iy + 6 + li * 20), wline, font=f_feat, fill=OFFWH)

    # ── 11. Нижняя плашка ────────────────────────────────────────────────────
    BAR_Y = H - 62
    _vgrad(img, 0, BAR_Y, W, H, (32, 27, 14), (16, 13, 6))
    d = ImageDraw.Draw(img)
    d.rectangle([0, BAR_Y, W, BAR_Y + 2], fill=GOLD)

    stats = [("50% СТАРТ", "Предоплата"), ("50% СДАЧА", "При приёмке"), ("ГАРАНТИЯ", "Результата")]
    sw = W // len(stats)
    for i, (val, lbl) in enumerate(stats):
        sx = i * sw + sw // 2
        try:
            tw = d.textlength(val, font=f_stat)
            tw2 = d.textlength(lbl, font=f_statl)
        except Exception:
            tw = len(val) * 11
            tw2 = len(lbl) * 7
        d.text((sx - tw // 2,  BAR_Y + 9),  val, font=f_stat,  fill=GOLD)
        d.text((sx - tw2 // 2, BAR_Y + 36), lbl, font=f_statl, fill=LGRAY)
        if i > 0:
            d.rectangle([i * sw, BAR_Y + 14, i * sw + 1, H - 12], fill=DLINE)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf
