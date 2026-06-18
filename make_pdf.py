"""
Лид-магнит PDF — светлый дизайн по референсу:
бежевый фон, белые карточки, оранжевые акценты, иконки.
"""
import os, math
from pathlib import Path
from fpdf import FPDF

BASE = Path(__file__).parent
OUT  = str(BASE / "assets" / "guide.pdf")
os.makedirs(str(BASE / "assets"), exist_ok=True)

# ── Цвета ────────────────────────────────────────────────────────────────────
BG      = (248, 241, 229)
BG2     = (236, 218, 195)
WHITE   = (255, 255, 255)
ORANGE  = (205, 112,  42)
ORANGE_L= (249, 237, 222)
ORANGE_D= (165,  84,  22)
DARK    = ( 35,  26,  16)
DGRAY   = ( 90,  80,  68)
LGRAY   = (160, 148, 134)
BAR_BG  = (228, 215, 198)
CARD_SH = (215, 200, 180)
GREEN   = ( 72, 160,  80)
RED     = (190,  75,  65)
BLUE    = ( 80, 140, 200)


class PDF(FPDF):

    def f(self, sz=11, b=False, c=DARK):
        self.set_font("R", "B" if b else "", sz)
        self.set_text_color(*c)

    def box(self, x, y, w, h, c, r=0):
        self.set_fill_color(*c)
        if r:
            self.set_draw_color(*c)
            self.rounded_rect(x, y, w, h, r, "F")
        else:
            self.rect(x, y, w, h, "F")

    def rounded_rect(self, x, y, w, h, r, style=""):
        self.set_draw_color(*self._fill)
        k = self.k
        hp = self.h
        self.set_line_width(0)
        # Используем встроенный rounded_rect если доступен, иначе rect
        try:
            super().rounded_rect(x, y, w, h, r, corner_style="ABCD", style=style)
        except Exception:
            self.rect(x, y, w, h, style)

    @property
    def _fill(self):
        return (self._fill_color.r, self._fill_color.g, self._fill_color.b) if hasattr(self, '_fill_color') else WHITE

    def hl(self, y, c=CARD_SH, lw=0.3):
        self.set_draw_color(*c)
        self.set_line_width(lw)
        self.line(0, y, 210, y)

    def vl(self, x, y1, y2, c=CARD_SH, lw=0.3):
        self.set_draw_color(*c)
        self.set_line_width(lw)
        self.line(x, y1, x, y2)

    def dot(self, x, y, r, c):
        self.set_fill_color(*c)
        self.ellipse(x - r, y - r, r * 2, r * 2, "F")

    def circle_out(self, cx, cy, r, c, lw=0.5):
        self.set_draw_color(*c)
        self.set_line_width(lw)
        self.ellipse(cx - r, cy - r, r * 2, r * 2, "D")

    # ── Фон страницы ─────────────────────────────────────────────────────────
    def page_bg(self):
        """Светлый бежевый фон."""
        # Верхняя треть чуть светлее
        self.set_fill_color(*BG)
        self.rect(0, 0, 210, 297, "F")
        # Нижняя треть чуть темнее (имитация градиента)
        for i in range(10):
            t = i / 9
            c = tuple(int(BG[j] + (BG2[j] - BG[j]) * t) for j in range(3))
            self.set_fill_color(*c)
            y_start = 180 + i * 12
            self.rect(0, y_start, 210, 13, "F")

    # ── Белая карточка ───────────────────────────────────────────────────────
    def white_card(self, x, y, w, h, r=5):
        # Тень
        self.set_fill_color(*CARD_SH)
        try:
            self.rounded_rect(x + 1.5, y + 1.5, w, h, r, "F")
        except Exception:
            self.rect(x + 1.5, y + 1.5, w, h, "F")
        # Белая карточка
        self.set_fill_color(*WHITE)
        try:
            self.rounded_rect(x, y, w, h, r, "F")
        except Exception:
            self.rect(x, y, w, h, "F")

    # ── Иконка-квадрат ───────────────────────────────────────────────────────
    def icon_box(self, x, y, s=8):
        """Светло-оранжевый квадрат для иконки."""
        self.set_fill_color(*ORANGE_L)
        try:
            self.rounded_rect(x, y, s, s, 2, "F")
        except Exception:
            self.rect(x, y, s, s, "F")

    def icon_check(self, x, y, s=8):
        """Галочка в оранжевом квадрате."""
        self.icon_box(x, y, s)
        cx, cy = x + s / 2, y + s / 2
        self.set_draw_color(*ORANGE)
        self.set_line_width(0.6)
        self.line(cx - 2, cy, cx - 0.5, cy + 2)
        self.line(cx - 0.5, cy + 2, cx + 2.5, cy - 1.5)

    def icon_circle(self, cx, cy, r, c, filled=True):
        """Круг иконки."""
        self.set_fill_color(*c)
        self.set_draw_color(*c)
        self.ellipse(cx - r, cy - r, r * 2, r * 2, "F" if filled else "D")

    # ── Бейдж ────────────────────────────────────────────────────────────────
    def badge(self, x, y, text, bg=ORANGE, tc=WHITE, sz=8):
        self.f(sz, True, tc)
        w = self.get_string_width(text) + 6
        self.set_fill_color(*bg)
        try:
            self.rounded_rect(x, y, w, 7, 2, "F")
        except Exception:
            self.rect(x, y, w, 7, "F")
        self.set_xy(x + 1, y + 0.8)
        self.cell(w - 2, 5.5, text, align="C")

    def section_label(self, num, title):
        self.f(7, True, ORANGE)
        self.set_xy(14, 14)
        self.cell(0, 5, f"{num:02d}  /  {title.upper()}")
        # Оранжевая линия
        self.set_fill_color(*ORANGE)
        self.rect(14, 21, 30, 0.8, "F")
        self.set_fill_color(*CARD_SH)
        self.rect(44, 21.3, 166, 0.4, "F")

    # ── Блок фичи ────────────────────────────────────────────────────────────
    def feat_card(self, x, y, w, h, icon_idx, text):
        """Белая карточка с иконкой и текстом."""
        self.white_card(x, y, w, h, r=4)
        # Иконка
        isize = 9
        ix = x + 4
        iy = y + (h - isize) / 2
        self.icon_box(ix, iy, isize)
        # Символ иконки
        icons_chars = ["+", ">", "*", "#", "@", "!"]
        self.set_draw_color(*ORANGE)
        self.set_line_width(0.5)
        cx, cy = ix + isize / 2, iy + isize / 2
        if icon_idx % 6 == 0:    # страница
            self.line(cx - 2, cy - 1, cx + 2, cy - 1)
            self.line(cx - 2, cy + 0.5, cx + 2, cy + 0.5)
            self.line(cx - 2, cy + 2, cx + 1, cy + 2)
        elif icon_idx % 6 == 1:  # график
            self.line(cx - 2, cy + 2, cx, cy - 1)
            self.line(cx, cy - 1, cx + 2, cy - 2.5)
            self.line(cx + 1.5, cy - 3, cx + 2, cy - 2.5)
            self.line(cx + 2, cy - 2.5, cx + 1.5, cy - 2)
        elif icon_idx % 6 == 2:  # шестерня
            self.ellipse(cx - 1.8, cy - 1.8, 3.6, 3.6, "D")
        elif icon_idx % 6 == 3:  # календарь
            self.rect(cx - 2.5, cy - 2, 5, 4, "D")
            self.line(cx - 2.5, cy - 0.5, cx + 2.5, cy - 0.5)
        elif icon_idx % 6 == 4:  # цель
            self.ellipse(cx - 2.5, cy - 2.5, 5, 5, "D")
            self.ellipse(cx - 1, cy - 1, 2, 2, "F")
        else:                     # щит
            self.line(cx - 2, cy - 2, cx, cy - 3)
            self.line(cx, cy - 3, cx + 2, cy - 2)
            self.line(cx + 2, cy - 2, cx + 2, cy + 0.5)
            self.line(cx + 2, cy + 0.5, cx, cy + 3)
            self.line(cx, cy + 3, cx - 2, cy + 0.5)
            self.line(cx - 2, cy + 0.5, cx - 2, cy - 2)

        # Текст
        self.f(8.5, False, DARK)
        self.set_xy(x + isize + 7, y + 2)
        self.multi_cell(w - isize - 10, 5, text)

    # ─────────────────────────────────────────────────────────────────────────
    # ОБЛОЖКА
    # ─────────────────────────────────────────────────────────────────────────
    def cover(self):
        self.page_bg()
        self.section_label(0, "Бесплатный гайд")

        # ── Левая белая карточка ─────────────────────────────────────────────
        self.white_card(12, 28, 88, 200, r=5)

        self.f(6.5, True, ORANGE)
        self.set_xy(18, 34)
        self.cell(0, 4, "КОММЕРЧЕСКИЙ ГИД")

        # Оранжевая линия
        self.set_fill_color(*ORANGE)
        self.rect(18, 39, 28, 0.8, "F")

        self.f(22, True, DARK)
        self.set_xy(18, 43)
        self.multi_cell(76, 10, "Сайт\nили бот?", "L")

        self.f(9, False, DGRAY)
        self.set_xy(18, 71)
        self.multi_cell(76, 5.5,
            "Как выбрать правильный\n"
            "инструмент и не потратить\n"
            "деньги впустую", "L")

        # Буллеты
        bullets = [
            "Сравнение 3 инструментов",
            "3 реальных кейса с цифрами",
            "Алгоритм выбора за 5 шагов",
            "Частые ошибки",
        ]
        by = 100
        for t in bullets:
            self.icon_check(18, by + 0.5, 6)
            self.f(8, False, DARK)
            self.set_xy(26, by)
            self.cell(72, 6, t)
            by += 9

        # Кнопка
        self.set_fill_color(*ORANGE)
        try:
            self.rounded_rect(18, 218, 76, 10, 2.5, "F")
        except Exception:
            self.rect(18, 218, 76, 10, "F")
        self.f(9, True, WHITE)
        self.set_xy(18, 220)
        self.cell(76, 6, "Начать читать  ->", align="C")

        # ── Правая панель: три факта ──────────────────────────────────────────
        # Большой процент
        self.f(52, True, ORANGE)
        self.set_xy(104, 32)
        self.cell(94, 38, "73%", align="C")

        self.f(9, False, DGRAY)
        self.set_xy(104, 70)
        self.multi_cell(94, 5.5, "бизнесов выбирают\nне тот инструмент", align="C")

        # Три карточки-факта
        facts = [
            (ORANGE,  "60-80%", "открываемость\nTelegram"),
            (GREEN,   "3x",     "дешевле лид\nс лендинга"),
            (BLUE,    "7 дней", "средний запуск\nбота"),
        ]
        for i, (c, n, l) in enumerate(facts):
            fy = 95 + i * 44
            self.white_card(108, fy, 88, 38, r=4)
            self.set_fill_color(*c)
            try:
                self.rounded_rect(108, fy, 88, 2.5, 4, "F")
            except Exception:
                self.rect(108, fy, 88, 2.5, "F")
            self.f(18, True, c)
            self.set_xy(108, fy + 4)
            self.cell(88, 12, n, align="C")
            self.f(7.5, False, LGRAY)
            self.set_xy(108, fy + 17)
            self.multi_cell(88, 4.5, l, align="C")

        # ── Нижняя плашка ────────────────────────────────────────────────────
        self.set_fill_color(*BAR_BG)
        try:
            self.rounded_rect(12, 240, 186, 46, 5, "F")
        except Exception:
            self.rect(12, 240, 186, 46, "F")

        stats = [("50% СТАРТ", "Предоплата"), ("50% СДАЧА", "При приёмке"), ("ГАРАНТИЯ", "Результата")]
        sw = 62
        for i, (v, l) in enumerate(stats):
            sx = 12 + i * sw
            # Круг
            self.set_fill_color(*DARK)
            self.ellipse(sx + 10, 248, 12, 12, "F")
            # Текст
            self.f(9, True, ORANGE)
            self.set_xy(sx + 24, 249)
            self.cell(sw - 26, 5, v)
            self.f(7.5, False, DGRAY)
            self.set_xy(sx + 24, 256)
            self.cell(sw - 26, 5, l)
            if i < 2:
                self.set_fill_color(*CARD_SH)
                self.rect(sx + sw - 0.5, 244, 1, 36, "F")

    # ─────────────────────────────────────────────────────────────────────────
    # СТРАНИЦА 2: ПРОБЛЕМА
    # ─────────────────────────────────────────────────────────────────────────
    def p_problem(self):
        self.page_bg()
        self.section_label(1, "Почему это важно")

        # Заголовок
        self.f(22, True, DARK)
        self.set_xy(14, 28)
        self.multi_cell(182, 10, "Почему большинство\nтратит деньги зря", "L")

        self.f(10, False, DGRAY)
        self.set_xy(14, 58)
        self.multi_cell(182, 6,
            "Каждый день ко мне приходят предприниматели с похожей историей. "
            "Потратили 80 000 рублей на сайт — заявок нет. "
            "Сделали лендинг — а клиенты сидят в Telegram. "
            "Заказали бот — а нужен был нормальный сайт с SEO.", "L")

        # Три карточки-статистики
        stats = [
            (ORANGE, "73%",   "выбирают\nне тот инструмент"),
            (RED,    "2.4x",  "дороже обходится\nпеределка"),
            (GREEN,  "87 дн", "теряют в среднем\nна ошибочный путь"),
        ]
        for i, (c, n, l) in enumerate(stats):
            x = 14 + i * 63
            self.white_card(x, 102, 59, 54, r=4)
            self.set_fill_color(*c)
            try:
                self.rounded_rect(x, 102, 59, 2.5, 4, "F")
            except Exception:
                self.rect(x, 102, 59, 2.5, "F")
            self.f(24, True, c)
            self.set_xy(x, 106)
            self.cell(59, 16, n, align="C")
            self.f(8, False, LGRAY)
            self.set_xy(x, 124)
            self.multi_cell(59, 5, l, align="C")

        # Цитата-карточка
        self.white_card(14, 166, 182, 28, r=4)
        self.set_fill_color(*ORANGE)
        try:
            self.rounded_rect(14, 166, 3.5, 28, 4, "F")
        except Exception:
            self.rect(14, 166, 3.5, 28, "F")
        self.f(10, True, DARK)
        self.set_xy(22, 172)
        self.multi_cell(170, 6,
            "«Правильный инструмент — это половина успеха.\n"
            "Этот гайд поможет выбрать его за 12 минут.»")

        # Ошибки
        self.f(11, True, DARK)
        self.set_xy(14, 204); self.cell(0, 7, "Типичные ошибки:")

        errs = [
            "Сделали многостраничный сайт — а нужен был простой лендинг",
            "Заказали лендинг — а 80% клиентов приходят через Telegram",
            "Потратили 100 000 руб. на сайт — а бот за 20 000 дал бы больше",
        ]
        for i, e in enumerate(errs):
            ey = 214 + i * 16
            self.white_card(14, ey, 182, 13, r=3)
            self.set_fill_color(*ORANGE)
            self.rect(14, ey, 2.5, 13, "F")
            self.icon_check(18, ey + 2.5, 8)
            self.f(9, False, DARK)
            self.set_xy(28, ey + 2.5)
            self.cell(164, 8, e)

    # ─────────────────────────────────────────────────────────────────────────
    # СТРАНИЦА 3: СРАВНЕНИЕ
    # ─────────────────────────────────────────────────────────────────────────
    def p_compare(self):
        self.page_bg()
        self.section_label(2, "Сравнение инструментов")

        self.f(22, True, DARK)
        self.set_xy(14, 28)
        self.multi_cell(182, 10, "Три инструмента — три разные задачи", "L")

        tools = [
            (ORANGE, "Telegram-бот",  "от 20 000 руб.", "3-7 дней",
             "Автоматизация\nи повторный контакт",
             ["Работает 24/7 без менеджера",
              "Push открывают 60-80%",
              "Воронка, запись, рассылки",
              "Повторный контакт бесплатно"]),
            (GREEN,  "Лендинг",       "от 25 000 руб.", "5-10 дней",
             "Один оффер —\nмаксимум заявок",
             ["Продающая структура",
              "Один оффер — фокус",
              "Быстрый запуск",
              "Форма заявки + Telegram"]),
            (BLUE,   "Сайт",          "от 40 000 руб.", "10-14 дней",
             "Многостраничный\nсайт под ключ",
             ["Уникальный дизайн",
              "Каталог и портфолио",
              "Доверие и репутация",
              "Работает годами"]),
        ]

        for i, (c, name, price, term, desc, pts) in enumerate(tools):
            x = 14 + i * 63
            self.white_card(x, 54, 61, 192, r=5)
            # Цветная шапка карточки
            self.set_fill_color(*c)
            try:
                self.rounded_rect(x, 54, 61, 3, 5, "F")
            except Exception:
                self.rect(x, 54, 61, 3, "F")

            self.f(10, True, c)
            self.set_xy(x + 3, 60)
            self.cell(55, 7, name)

            self.f(8, False, LGRAY)
            self.set_xy(x + 3, 68)
            self.multi_cell(55, 4.5, desc)

            # Цена и срок
            self.set_fill_color(*CARD_SH)
            self.rect(x + 3, 80, 55, 0.3, "F")
            self.f(7, False, LGRAY)
            self.set_xy(x + 3, 82); self.cell(28, 4, "СТОИМОСТЬ")
            self.set_xy(x + 31, 82); self.cell(27, 4, "СРОК", align="R")
            self.f(9, True, DARK)
            self.set_xy(x + 3, 87); self.cell(28, 6, price)
            self.f(9, True, c)
            self.set_xy(x + 31, 87); self.cell(27, 6, term, align="R")

            self.set_fill_color(*CARD_SH)
            self.rect(x + 3, 96, 55, 0.3, "F")

            for j, pt in enumerate(pts):
                py = 100 + j * 33
                self.feat_card(x + 3, py, 55, 30, j, pt)

        # Лайфхак
        self.white_card(14, 256, 182, 18, r=4)
        self.set_fill_color(*GREEN)
        try:
            self.rounded_rect(14, 256, 3.5, 18, 4, "F")
        except Exception:
            self.rect(14, 256, 3.5, 18, "F")
        self.f(8.5, True, GREEN)
        self.set_xy(22, 260); self.cell(24, 5, "Лайфхак:")
        self.f(8.5, False, DARK)
        self.set_xy(47, 260)
        self.cell(144, 5, "Лендинг + Telegram-бот при меньшем бюджете дают больше конверсий")

    # ─────────────────────────────────────────────────────────────────────────
    # СТРАНИЦА 4: КЕЙСЫ
    # ─────────────────────────────────────────────────────────────────────────
    def p_cases(self):
        self.page_bg()
        self.section_label(3, "Реальные кейсы")

        self.f(22, True, DARK)
        self.set_xy(14, 28)
        self.multi_cell(182, 10, "Результаты клиентов в цифрах", "L")

        cases = [
            (ORANGE, "Telegram-бот", "Производство мебельных фасадов",
             "Менеджер вручную обрабатывал заявки — полдня на переписку.",
             [("Заявок/мес",   "18 > 67",    GREEN, "+272%"),
              ("Время ответа", "4ч > 2мин",  GREEN, "-97%"),
              ("Конверсия",    "2.1 > 8.4%", GREEN, "+300%")]),
            (GREEN, "Лендинг", "Юридические услуги онлайн",
             "Старый сайт: конверсия 1.2%, лид — 3200 руб.",
             [("Стоимость лида", "3200>890р.", GREEN, "-72%"),
              ("Конверсия",      "1.2>4.8%",  GREEN, "+300%"),
              ("Окупился за",    "18 дней",   GREEN, "ROI 840%")]),
            (BLUE, "Сайт + Бот", "Строительная компания",
             "Работали только по сарафану, нет онлайн-присутствия.",
             [("Новых клиентов", "+14/мес", GREEN, "с нуля"),
              ("Средний чек",    "+42%",    GREEN, "доверие"),
              ("ROI за год",     "1840%",   GREEN, "окупился")]),
        ]

        for i, (c, tool, niche, problem, results) in enumerate(cases):
            y = 52 + i * 72
            self.white_card(14, y, 182, 66, r=5)
            self.set_fill_color(*c)
            try:
                self.rounded_rect(14, y, 3.5, 66, 5, "F")
            except Exception:
                self.rect(14, y, 3.5, 66, "F")

            # Бейдж
            self.badge(20, y + 5, f"  {tool}  ", c, WHITE, 7.5)

            self.f(10, True, DARK)
            self.set_xy(20, y + 16); self.cell(85, 6, niche)
            self.f(8, False, DGRAY)
            self.set_xy(20, y + 24)
            self.multi_cell(74, 4.5, problem)

            # Вертикальный разделитель
            self.vl(100, y + 6, y + 60, CARD_SH)

            # Результаты
            for j, (label, val, vc, extra) in enumerate(results):
                rx = 104 + j * 30
                self.f(7, False, LGRAY)
                self.set_xy(rx, y + 8); self.cell(28, 4, label, align="C")
                self.f(10, True, vc)
                self.set_xy(rx, y + 14); self.cell(28, 7, val, align="C")
                self.f(8, True, c)
                self.set_xy(rx, y + 23); self.cell(28, 5, extra, align="C")

    # ─────────────────────────────────────────────────────────────────────────
    # СТРАНИЦА 5: АЛГОРИТМ
    # ─────────────────────────────────────────────────────────────────────────
    def p_algo(self):
        self.page_bg()
        self.section_label(4, "Алгоритм выбора")

        self.f(22, True, DARK)
        self.set_xy(14, 28)
        self.multi_cell(182, 10, "5 вопросов — и ответ станет очевидным", "L")

        qs = [
            (ORANGE, "Откуда приходят клиенты?",
             "Таргет / контекст ->", GREEN, "Лендинг",
             "Telegram / органика ->", ORANGE, "Бот"),
            (GREEN, "Нужна автоматизация?",
             "Да, без менеджера ->", ORANGE, "Бот",
             "Нет, просто заявка ->", GREEN, "Лендинг"),
            (BLUE, "Один оффер или каталог?",
             "Один продукт / услуга ->", GREEN, "Лендинг",
             "Много услуг / товаров ->", BLUE, "Сайт"),
            (ORANGE, "Нужен повторный контакт?",
             "Да, нужны рассылки ->", ORANGE, "Бот",
             "Нет, ретаргет ->", GREEN, "Лендинг"),
            (GREEN, "Какой бюджет и срок?",
             "До 30 000 руб / срочно ->", ORANGE, "Бот или лендинг",
             "Есть ресурс ->", BLUE, "Сайт"),
        ]

        for i, (c, q, a1, c1, r1, a2, c2, r2) in enumerate(qs):
            y = 52 + i * 44
            self.white_card(14, y, 182, 38, r=4)
            self.set_fill_color(*c)
            try:
                self.rounded_rect(14, y, 3.5, 38, 4, "F")
            except Exception:
                self.rect(14, y, 3.5, 38, "F")

            # Номер
            self.f(16, True, ORANGE_L)
            self.set_xy(16, y + 5); self.cell(12, 12, str(i + 1), align="C")

            self.f(10, True, DARK)
            self.set_xy(32, y + 8); self.cell(158, 7, q)

            # Варианты
            self.icon_check(32, y + 21, 7)
            self.f(8.5, False, DGRAY); self.set_xy(41, y + 20); self.cell(55, 6, a1)
            self.f(8.5, True, c1);     self.set_xy(98, y + 20); self.cell(40, 6, r1)

            self.set_fill_color(*RED)
            self.ellipse(34, y + 30, 3.5, 3.5, "F")
            self.f(8.5, False, DGRAY); self.set_xy(41, y + 28); self.cell(55, 6, a2)
            self.f(8.5, True, c2);     self.set_xy(98, y + 28); self.cell(40, 6, r2)

    # ─────────────────────────────────────────────────────────────────────────
    # СТРАНИЦА 6: CTA
    # ─────────────────────────────────────────────────────────────────────────
    def p_cta(self):
        self.page_bg()

        # Большая белая карточка по центру
        self.white_card(14, 20, 182, 140, r=6)
        self.set_fill_color(*ORANGE)
        try:
            self.rounded_rect(14, 20, 182, 3, 6, "F")
        except Exception:
            self.rect(14, 20, 182, 3, "F")

        self.f(7, True, ORANGE)
        self.set_xy(14, 30); self.cell(182, 5, "СЛЕДУЮЩИЙ ШАГ", align="C")

        self.f(26, True, DARK)
        self.set_xy(14, 38)
        self.multi_cell(182, 12, "Обсудим ваш проект?", "C")

        self.f(10, False, DGRAY)
        self.set_xy(14, 68)
        self.multi_cell(182, 6,
            "Бесплатный 20-минутный разбор.\n"
            "Покажу примеры — назову цену и срок.", "C")

        # Кнопка
        self.set_fill_color(*ORANGE)
        try:
            self.rounded_rect(67, 90, 76, 13, 3, "F")
        except Exception:
            self.rect(67, 90, 76, 13, "F")
        self.f(10, True, WHITE)
        self.set_xy(67, 92); self.cell(76, 9, "Записаться ->", align="C")

        # Три обещания
        promises = [(GREEN, "Бесплатно"), (ORANGE, "Без давления"), (BLUE, "Конкретный план")]
        for i, (c, t) in enumerate(promises):
            x = 20 + i * 60
            self.dot(x + 24, 118, 3, c)
            self.f(8.5, True, c)
            self.set_xy(x, 123); self.cell(48, 5, t, align="C")

        # Четыре карточки доверия
        proof = [(ORANGE, "50+", "проектов"), (GREEN, "7+", "лет опыта"),
                 (BLUE, "24ч", "время ответа"), (ORANGE, "100%", "гарантия")]
        for i, (c, n, l) in enumerate(proof):
            x = 14 + i * 47
            self.white_card(x, 148, 43, 38, r=4)
            self.set_fill_color(*c)
            try:
                self.rounded_rect(x, 148, 43, 2.5, 4, "F")
            except Exception:
                self.rect(x, 148, 43, 2.5, "F")
            self.f(18, True, c)
            self.set_xy(x, 152); self.cell(43, 12, n, align="C")
            self.f(7.5, False, LGRAY)
            self.set_xy(x, 166); self.cell(43, 5, l, align="C")

        # Услуги
        self.f(11, True, DARK)
        self.set_xy(14, 198); self.cell(0, 7, "Что делаю:")
        skills = [
            (ORANGE, "Telegram-боты под ключ — воронки, рассылки, запись на услугу"),
            (GREEN,  "Лендинги с высокой конверсией — от 5 дней"),
            (BLUE,   "Многостраничные сайты — SEO, каталог, портфолио"),
        ]
        for i, (c, t) in enumerate(skills):
            y = 208 + i * 16
            self.white_card(14, y, 182, 13, r=3)
            self.set_fill_color(*c)
            self.rect(14, y, 2.5, 13, "F")
            self.icon_check(18, y + 2.5, 8)
            self.f(9, False, DARK)
            self.set_xy(28, y + 2.5); self.cell(164, 8, t)

        # Нижняя плашка
        self.set_fill_color(*BAR_BG)
        try:
            self.rounded_rect(14, 258, 182, 30, 5, "F")
        except Exception:
            self.rect(14, 258, 182, 30, "F")
        self.f(8, False, LGRAY)
        self.set_xy(14, 268)
        self.cell(182, 6,
            "Telegram-боты  |  Лендинги  |  Сайты  |  Разработка под ключ",
            align="C")


# ─────────────────────────────────────────────────────────────────────────────

def make():
    font_r = str(BASE / "assets" / "Inter-Regular.ttf")
    font_b = str(BASE / "assets" / "Inter-Bold.ttf")
    if not Path(font_r).exists():
        font_r = str(BASE / "assets" / "Montserrat-Regular.ttf")
        font_b = str(BASE / "assets" / "Montserrat-Bold.ttf")
    if not Path(font_r).exists():
        print("Шрифты не найдены")
        return

    pdf = PDF("P", "mm", "A4")
    pdf.add_font("R", "",  fname=font_r)
    pdf.add_font("R", "B", fname=font_b)
    pdf.set_margins(0, 0, 0)
    pdf.set_auto_page_break(False)

    pdf.add_page(); pdf.cover()
    pdf.add_page(); pdf.p_problem()
    pdf.add_page(); pdf.p_compare()
    pdf.add_page(); pdf.p_cases()
    pdf.add_page(); pdf.p_algo()
    pdf.add_page(); pdf.p_cta()

    pdf.output(OUT)
    size = Path(OUT).stat().st_size
    print(f"PDF: {OUT}  ({size // 1024} KB)  6 страниц")


if __name__ == "__main__":
    make()
