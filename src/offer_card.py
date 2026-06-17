"""
Карточка КП — светлый дизайн по референсу:
бежевый фон, белая карточка, оранжевые акценты, иконки, нижняя плашка.
"""
import io, os, logging

log = logging.getLogger(__name__)

# ── Цвета ────────────────────────────────────────────────────────────────────
BG1      = (248, 241, 229)   # фон сверху
BG2      = (236, 218, 195)   # фон снизу
WHITE    = (255, 255, 255)
ORANGE   = (205, 112,  42)   # основной акцент
ORANGE_L = (249, 237, 222)   # светло-оранжевый (фон иконок)
ORANGE_D = (165,  84,  22)   # тёмно-оранжевый
DARK     = ( 35,  26,  16)   # заголовки
DGRAY    = ( 90,  80,  68)   # вторичный текст
LGRAY    = (160, 148, 134)   # третичный
BAR_BG   = (228, 215, 198)   # нижняя плашка
ICON_DARK= ( 48,  36,  22)   # тёмный круг иконки в плашке
SHADOW   = (215, 200, 180)   # цвет тени карточки


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


def _vgrad(img, x0, y0, x1, y1, c_top, c_bot):
    from PIL import ImageDraw
    d = ImageDraw.Draw(img)
    h = y1 - y0
    for i in range(h):
        t = i / max(h - 1, 1)
        c = tuple(int(c_top[j] + (c_bot[j] - c_top[j]) * t) for j in range(3))
        d.line([(x0, y0 + i), (x1, y0 + i)], fill=c)


def _wrap(d, text, font, max_w):
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


def _tlen(d, text, font):
    try:
        return d.textlength(text, font=font)
    except Exception:
        return len(text) * 9


# ── Иконки ───────────────────────────────────────────────────────────────────

def _icon_page(d, cx, cy, s, c):
    """Иконка страницы/документа."""
    x, y, w, h = cx - s, cy - s, s * 2, s * 2
    d.rounded_rectangle([x, y, x + w, y + h], radius=3, outline=c, width=2)
    for li in range(3):
        lx1, ly = x + 4, y + 6 + li * 7
        lx2 = x + w - 4 - (6 if li == 2 else 0)
        d.line([(lx1, ly), (lx2, ly)], fill=c, width=2)


def _icon_chart(d, cx, cy, s, c):
    """Иконка графика/SEO."""
    x, y = cx - s, cy + s
    for i, bh in enumerate([s // 2, s, int(s * 0.75), int(s * 1.4)]):
        bx = x + i * (s // 2 + 2)
        d.rectangle([bx, y - bh, bx + s // 2 - 1, y], fill=c)
    # стрелка вверх-вправо
    d.line([(cx - s + 2, cy + s // 2), (cx + s - 2, cy - s + 2)], fill=c, width=2)
    d.line([(cx + s - 6, cy - s + 2), (cx + s - 2, cy - s + 2)], fill=c, width=2)
    d.line([(cx + s - 2, cy - s + 2), (cx + s - 2, cy - s + 6)], fill=c, width=2)


def _icon_gear(d, cx, cy, s, c):
    """Иконка шестерёнки/интеграции."""
    d.ellipse([cx - s + 4, cy - s + 4, cx + s - 4, cy + s - 4], outline=c, width=2)
    for angle_deg in range(0, 360, 45):
        import math
        a = math.radians(angle_deg)
        x1 = cx + int((s - 5) * math.cos(a))
        y1 = cy + int((s - 5) * math.sin(a))
        x2 = cx + int((s + 1) * math.cos(a))
        y2 = cy + int((s + 1) * math.sin(a))
        d.line([(x1, y1), (x2, y2)], fill=c, width=3)


def _icon_calendar(d, cx, cy, s, c):
    """Иконка календаря."""
    x, y, w, h = cx - s + 1, cy - s + 2, (s - 1) * 2, (s - 2) * 2
    d.rounded_rectangle([x, y, x + w, y + h], radius=3, outline=c, width=2)
    d.line([(x, y + 6), (x + w, y + 6)], fill=c, width=2)
    d.line([(x + 5, y - 1), (x + 5, y + 3)], fill=c, width=2)
    d.line([(x + w - 5, y - 1), (x + w - 5, y + 3)], fill=c, width=2)
    for row in range(2):
        for col in range(3):
            px = x + 4 + col * (w // 3)
            py = y + 10 + row * 7
            d.ellipse([px, py, px + 3, py + 3], fill=c)


def _icon_target(d, cx, cy, s, c):
    """Иконка цели/аналитики."""
    for r in [s - 1, s - 5, s - 9]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=c, width=2)
    d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=c)


def _icon_shield(d, cx, cy, s, c):
    """Иконка щита/гарантии."""
    pts = [(cx, cy - s), (cx + s, cy - s // 2),
           (cx + s, cy + s // 3), (cx, cy + s),
           (cx - s, cy + s // 3), (cx - s, cy - s // 2)]
    d.polygon(pts, outline=c, fill=None)
    # галочка внутри
    d.line([(cx - 4, cy + 1), (cx - 1, cy + 5), (cx + 5, cy - 3)], fill=c, width=2)


def _icon_wallet(d, cx, cy, s, c):
    """Иконка кошелька."""
    d.rounded_rectangle([cx - s, cy - s // 2, cx + s, cy + s],
                        radius=3, outline=c, width=2)
    d.rounded_rectangle([cx, cy - 1, cx + s - 2, cy + s - 2],
                        radius=4, outline=c, width=2)
    d.line([(cx - s, cy - s // 2), (cx + s, cy - s // 2)], fill=c, width=2)
    d.line([(cx - s // 2, cy - s), (cx - s // 2, cy - s // 2)], fill=c, width=2)
    d.line([(cx + s // 2, cy - s), (cx + s // 2, cy - s // 2)], fill=c, width=2)
    d.line([(cx - s, cy - s), (cx + s, cy - s)], fill=c, width=2)


ICON_FUNCS = [_icon_page, _icon_chart, _icon_gear, _icon_calendar, _icon_target, _icon_shield]


def _draw_icon_box(img, d, cx, cy, size, idx):
    """Светло-оранжевый квадрат с иконкой."""
    s = size // 2
    d.rounded_rectangle([cx - s, cy - s, cx + s, cy + s], radius=10, fill=ORANGE_L)
    fn = ICON_FUNCS[idx % len(ICON_FUNCS)]
    fn(d, cx, cy, s - 8, ORANGE)


# ── Главная функция ───────────────────────────────────────────────────────────

def make_offer_card(title: str, _unused: str, details: str, timeline: str) -> io.BytesIO:
    from PIL import Image, ImageDraw

    W, H = 1120, 660

    # ── Фон ─────────────────────────────────────────────────────────────────
    img = Image.new("RGB", (W, H), BG1)
    _vgrad(img, 0, 0, W, H, BG1, BG2)
    d = ImageDraw.Draw(img)

    # ── Левая белая карточка ─────────────────────────────────────────────────
    CX1, CY1, CX2, CY2 = 26, 26, 430, 590
    for s in range(7, 0, -1):
        shade = tuple(max(0, SHADOW[j] - s * 3) for j in range(3))
        d.rounded_rectangle([CX1 + s, CY1 + s, CX2 + s, CY2 + s], radius=20, fill=shade)
    d.rounded_rectangle([CX1, CY1, CX2, CY2], radius=20, fill=WHITE)

    # Шрифты
    f_cat   = _font(12, bold=True)
    f_head  = _font(30, bold=True)
    f_price = _font(52, bold=True)
    f_info  = _font(16)
    f_infob = _font(16, bold=True)
    f_btn   = _font(20, bold=True)
    f_sec   = _font(20, bold=True)
    f_feat  = _font(17)
    f_featb = _font(17, bold=True)
    f_statv = _font(20, bold=True)
    f_statl = _font(13)

    LX = CX1 + 32

    # Категория
    d.text((LX, CY1 + 30), "КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ", font=f_cat, fill=ORANGE)

    # Название пакета
    raw = _clean(title)
    while raw and not (raw[0].isalpha() or ord(raw[0]) >= 0x400):
        raw = raw[1:].strip()
    if ' - ' in raw:
        pkg_name, pkg_price = raw.split(' - ', 1)
    elif '--' in raw:
        pkg_name, pkg_price = raw.split('--', 1)
    else:
        pkg_name, pkg_price = raw, ''

    # Переводим в Title Case
    name_title = pkg_name.strip().title()
    price_str  = pkg_price.strip()

    d.text((LX, CY1 + 56), name_title, font=f_head, fill=DARK)

    # Оранжевая разделительная линия
    d.rectangle([LX, CY1 + 102, LX + 120, CY1 + 105], fill=ORANGE)

    # Цена
    d.text((LX, CY1 + 118), price_str or "По запросу", font=f_price, fill=ORANGE)

    # Инфо: срок + гарантия
    info_y = CY1 + 234
    # Иконка календаря
    _icon_calendar(d, LX + 14, info_y + 14, 12, DGRAY)
    d.text((LX + 32, info_y), "Срок:", font=f_infob, fill=DARK)
    d.text((LX + 32, info_y + 20), _clean(timeline) if timeline else "Обсудим", font=f_info, fill=DGRAY)

    # Иконка щита
    _icon_shield(d, LX + 180, info_y + 14, 10, DGRAY)
    d.text((LX + 196, info_y), "Гарантия", font=f_infob, fill=DARK)
    d.text((LX + 196, info_y + 20), "до результата", font=f_info, fill=DGRAY)

    # Кнопка "Заказать проект →"
    btn_y = CY2 - 90
    d.rounded_rectangle([LX, btn_y, CX2 - 32, btn_y + 52], radius=12, fill=ORANGE)
    btn_text = "Заказать проект  ->"
    btw = _tlen(d, btn_text, f_btn)
    btn_cx = LX + (CX2 - 32 - LX) // 2
    d.text((btn_cx - btw // 2, btn_y + 14), btn_text, font=f_btn, fill=WHITE)

    # ── Правая сторона: фичи ─────────────────────────────────────────────────
    RX = CX2 + 28
    RW = W - RX - 20

    # Заголовок
    d.text((RX, CY1 + 10), "Что входит в пакет:", font=f_sec, fill=DARK)
    d.rectangle([RX, CY1 + 40, RX + 80, CY1 + 43], fill=ORANGE)

    items = [l.strip() for l in details.split("\n")
             if l.strip() and not l.startswith("⏱")]

    # 2 колонки
    cols   = 2
    col_w  = (RW - 16) // cols
    row_h  = 110
    feat_y = CY1 + 58

    for i, line in enumerate(items[:6]):
        clean = _clean(line.replace("✅", "").replace("✓", "").strip())
        if not clean:
            continue
        col = i % cols
        row = i // cols
        fx  = RX + col * (col_w + 16)
        fy  = feat_y + row * row_h

        if fy + row_h > CY2 - 10:
            break

        fcard_w = col_w - 4
        fcard_h = row_h - 12

        # Белая карточка фичи
        for s in range(4, 0, -1):
            shade = tuple(max(0, SHADOW[j] + s * 4) for j in range(3))
            d.rounded_rectangle([fx+s, fy+s, fx+fcard_w+s, fy+fcard_h+s], radius=14, fill=shade)
        d.rounded_rectangle([fx, fy, fx + fcard_w, fy + fcard_h], radius=14, fill=WHITE)

        # Иконка
        icon_size = 44
        icon_cx = fx + 30
        icon_cy = fy + fcard_h // 2
        _draw_icon_box(img, d, icon_cx, icon_cy, icon_size, i)
        d = ImageDraw.Draw(img)

        # Текст фичи
        text_x = fx + 62
        text_max = fcard_w - 70
        wrapped = _wrap(d, clean, f_feat, text_max)
        total_h = len(wrapped) * 22
        text_start_y = fy + (fcard_h - total_h) // 2
        for li, wl in enumerate(wrapped[:3]):
            d.text((text_x, text_start_y + li * 22), wl, font=f_feat, fill=DARK)

    # ── Нижняя плашка ────────────────────────────────────────────────────────
    BAR_Y = CY2 + 14
    BAR_H = H - BAR_Y - 14
    d.rounded_rectangle([26, BAR_Y, W - 20, H - 14], radius=16, fill=BAR_BG)

    stats = [
        ("50% СТАРТ",  "Предоплата",   _icon_wallet),
        ("50% СДАЧА",  "При приёмке",  _icon_page),
        ("ГАРАНТИЯ",   "Результата",   _icon_shield),
    ]
    sw = (W - 46) // len(stats)
    ir = 22          # radius of icon circle
    GAP = 14         # gap between circle and text block
    for i, (val, lbl, icon_fn) in enumerate(stats):
        sx = 26 + i * sw + sw // 2
        cy_bar = BAR_Y + BAR_H // 2

        # Measure text widths to centre the [icon + text] group in the column
        vw = _tlen(d, val, f_statv)
        lw = _tlen(d, lbl, f_statl)
        text_w = max(vw, lw)
        group_w = ir * 2 + GAP + text_w
        group_x = sx - group_w // 2   # left edge of group

        # Тёмный круг иконки
        cx_icon = group_x + ir
        d.ellipse([cx_icon - ir, cy_bar - ir, cx_icon + ir, cy_bar + ir],
                  fill=ICON_DARK)
        icon_fn(d, cx_icon, cy_bar, 11, ORANGE_L)

        # Текст (выровнен по левому краю текстового блока)
        tx = group_x + ir * 2 + GAP
        d.text((tx, cy_bar - 15), val, font=f_statv, fill=ORANGE)
        d.text((tx, cy_bar + 11), lbl, font=f_statl, fill=DGRAY)

        # Разделитель
        if i > 0:
            d.line([(26 + i * sw, BAR_Y + 12), (26 + i * sw, H - 26)],
                   fill=(210, 195, 175), width=1)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf
