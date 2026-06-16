"""
Лид-магнит PDF — Premium Gold Edition
Запускается автоматически при старте бота (main.py)
"""
import os
from pathlib import Path
from fpdf import FPDF
from fpdf.enums import XPos, YPos

BASE = Path(__file__).parent
A   = str(BASE / "assets")
OUT = str(BASE / "assets" / "guide.pdf")

os.makedirs(A, exist_ok=True)

# ── Палитра ──────────────────────────────────────────────────────────────────
BG   = (10,  10,  20)    # почти чёрный
BG2  = (18,  18,  35)    # тёмно-синий
BG3  = (30,  28,  58)    # карточка
GOLD = (212, 175,  55)   # золото
GLD2 = (240, 210,  90)   # золото светлое
W    = (255, 255, 255)   # белый
G1   = (205, 205, 225)   # основной текст
G2   = (145, 140, 170)   # второстепенный
G3   = ( 40,  38,  72)   # разделители
GR   = ( 52, 211, 120)   # зелёный
RS   = (230,  90, 100)   # красный
BL   = ( 90, 160, 240)   # синий
AM   = (251, 191,  36)   # янтарный


class PDF(FPDF):

    def f(self, sz=11, b=False, c=W):
        self.set_font("R", "B" if b else "", sz)
        self.set_text_color(*c)

    def box(self, x, y, w, h, c):
        self.set_fill_color(*c)
        self.rect(x, y, w, h, "F")

    def hl(self, y, c=G3, lw=0.3):
        self.set_draw_color(*c)
        self.set_line_width(lw)
        self.line(0, y, 210, y)

    def vl(self, x, y1, y2, c=G3, lw=0.3):
        self.set_draw_color(*c)
        self.set_line_width(lw)
        self.line(x, y1, x, y2)

    def dot(self, x, y, r, c):
        self.set_fill_color(*c)
        self.ellipse(x-r, y-r, r*2, r*2, "F")

    def badge(self, x, y, text, bg=GOLD, tc=BG, sz=7.5):
        self.f(sz, True, tc)
        w = self.get_string_width(text) + 10
        self.box(x, y, w, 8, bg)
        self.set_xy(x, y + 1)
        self.cell(w, 6, text, align="C")
        return w

    def gold_bar(self):
        """Вертикальная золотая полоса слева."""
        for i in range(5):
            shade = tuple(max(0, c - i * 8) for c in GOLD)
            self.box(i, 0, 1, 297, shade)

    def section_mark(self, num, title):
        self.f(7, True, GOLD)
        self.set_xy(20, 16)
        self.cell(0, 5, f"0{num}  /  {title.upper()}")
        self.hl(24, G3)

    def page_base(self, dark=True):
        self.box(0, 0, 210, 297, BG if dark else BG2)
        self.gold_bar()
        # Верхняя тонкая линия
        self.box(5, 0, 205, 2, GOLD)

    # ─── ОБЛОЖКА ────────────────────────────────────────────────────────────
    def cover(self):
        self.box(0, 0, 210, 297, BG)
        self.gold_bar()
        self.box(5, 0, 205, 3, GOLD)

        # Правый декоративный блок
        self.box(145, 0, 65, 297, BG2)
        self.box(145, 0, 1, 297, G3)

        # Тег
        self.badge(20, 26, "  БЕСПЛАТНЫЙ ГИД  ", GOLD, BG, 8)

        # Заголовок
        self.f(46, True, W)
        self.set_xy(20, 46)
        self.multi_cell(120, 18, "Сайт\nили бот?", "L")

        # Золотая акцентная линия
        self.box(20, 124, 70, 3, GOLD)

        self.f(12, False, G2)
        self.set_xy(20, 134)
        self.multi_cell(120, 7,
            "Как выбрать правильный инструмент\n"
            "и не потратить деньги впустую", "L")

        # Буллеты
        items = [
            (GR,   "Сравнение 3 инструментов"),
            (GOLD, "3 реальных кейса с цифрами"),
            (BL,   "Алгоритм выбора за 5 шагов"),
        ]
        for i, (c, t) in enumerate(items):
            y = 170 + i * 15
            self.dot(24, y + 4, 3.5, c)
            self.f(11, True, W)
            self.set_xy(32, y + 0.5)
            self.cell(100, 7, t)

        # ── Правая панель ──
        # Большая цифра
        self.f(70, True, G3)
        self.set_xy(142, 52)
        self.cell(62, 52, "73", align="C")

        self.f(26, True, GOLD)
        self.set_xy(142, 102)
        self.cell(62, 18, "%", align="C")

        self.f(8.5, False, G2)
        self.set_xy(142, 122)
        self.multi_cell(62, 5.5, "бизнесов выбирают\nне тот инструмент", align="C")

        # Три мини-блока
        facts = [
            (GR,   "60–80%", "открываемость\nTelegram push"),
            (GOLD, "3x",     "дешевле лид\nс лендинга vs сайт"),
            (AM,   "7 дней", "средний срок\nзапуска бота"),
        ]
        for i, (c, n, l) in enumerate(facts):
            y = 165 + i * 35
            self.box(147, y, 56, 31, BG3)
            self.box(147, y, 56, 2.5, c)
            self.f(18, True, c)
            self.set_xy(147, y + 5)
            self.cell(56, 12, n, align="C")
            self.f(7.5, False, G2)
            self.set_xy(147, y + 18)
            self.multi_cell(56, 4.5, l, align="C")

        # Футер
        self.box(0, 276, 210, 21, BG2)
        self.hl(276, GOLD, 0.4)
        self.f(8, False, G2)
        self.set_xy(20, 284)
        self.cell(85, 5, "6 страниц  •  12 минут  •  Бесплатно")
        self.set_xy(105, 284)
        self.cell(85, 5, "Сайты  •  Боты  •  Под ключ", align="R")

    # ─── СТРАНИЦА 2: ПРОБЛЕМА ─────────────────────────────────────────────────
    def p_problem(self):
        self.page_base()
        self.section_mark(1, "Почему это важно")

        self.f(30, True, W)
        self.set_xy(20, 32)
        self.multi_cell(170, 13, "Почему большинство\nтратит деньги зря", "L")

        self.f(11, False, G1)
        self.set_xy(20, 74)
        self.multi_cell(170, 6.5,
            "Каждый день ко мне приходят предприниматели с похожей историей. "
            "Потратили 80 000 рублей на сайт — заявок нет. "
            "Сделали лендинг — а клиенты сидят в Telegram. "
            "Заказали бот — а нужен был нормальный сайт с SEO.\n\n"
            "Причина одна: инструмент выбирается по совету знакомых "
            "или по красивому портфолио подрядчика — а не по задаче.", "L")

        # Три статистики
        stats = [
            (GOLD, "73%",  "выбирают\nне тот инструмент"),
            (RS,   "2.4x", "дороже обходится\nпеределка"),
            (GR,   "87 дн","теряют в среднем\nна ошибочный путь"),
        ]
        for i, (c, n, l) in enumerate(stats):
            x = 20 + i * 63
            self.box(x, 134, 58, 54, BG3)
            self.box(x, 134, 58, 3, c)
            self.f(28, True, c)
            self.set_xy(x, 140)
            self.cell(58, 18, n, align="C")
            self.f(8.5, False, G2)
            self.set_xy(x, 161)
            self.multi_cell(58, 5.5, l, align="C")

        # Цитата
        self.box(20, 200, 170, 34, BG3)
        self.box(20, 200, 4, 34, GOLD)
        self.f(12, True, W)
        self.set_xy(30, 207)
        self.multi_cell(155, 7,
            "«Правильный инструмент — это половина успеха.\n"
            "Этот гайд поможет выбрать его за 12 минут.»")

        # Ошибки
        self.f(10, True, W)
        self.set_xy(20, 244); self.cell(0, 7, "Типичные ошибки:")
        errs = [
            "Сделали многостраничный сайт — а нужен был лендинг под рекламу",
            "Заказали лендинг — а 80% клиентов приходят через Telegram",
            "Потратили 100 000 руб. на сайт — а бот за 20 000 руб. дал бы больше",
        ]
        for i, e in enumerate(errs):
            y = 256 + i * 13
            self.dot(24, y + 3.5, 2.5, RS)
            self.f(9.5, False, G1)
            self.set_xy(31, y)
            self.multi_cell(158, 6, e)

    # ─── СТРАНИЦА 3: СРАВНЕНИЕ ────────────────────────────────────────────────
    def p_compare(self):
        self.page_base()
        self.section_mark(2, "Сравнение инструментов")

        self.f(30, True, W)
        self.set_xy(20, 32)
        self.multi_cell(170, 13, "Три инструмента —\nтри разные задачи", "L")

        tools = [
            (GOLD, "Telegram-бот",  "от 20 000 руб.", "3–7 дней",
             "Автоматизация\nи повторный контакт",
             ["Работает 24/7 без менеджера",
              "Push открывают 60–80%",
              "Воронка, запись, рассылки",
              "Повторный контакт бесплатно",
              "Запуск от 3 дней"]),
            (GR,   "Лендинг",       "от 25 000 руб.", "5–10 дней",
             "Конверсия\nрекламного трафика",
             ["Максимум конверсии с рекламы",
              "Один оффер — фокус",
              "A/B-тест за неделю",
              "Быстрый запуск и окупаемость",
              "Легко масштабировать"]),
            (BL,   "Сайт",          "от 40 000 руб.", "10–14 дней",
             "SEO и долгосрочный\nактив бизнеса",
             ["SEO-трафик без рекламы",
              "Каталог и портфолио",
              "Доверие и репутация",
              "Работает годами",
              "Разные страницы под сегменты"]),
        ]

        for i, (c, name, price, term, desc, pts) in enumerate(tools):
            x = 14 + i * 65
            y = 82
            self.box(x, y, 62, 175, BG3)
            self.box(x, y, 62, 4, c)
            self.box(x, y, 62, 30, BG2)
            self.box(x, y + 26, 62, 2, G3)

            self.f(12, True, c)
            self.set_xy(x + 4, y + 8)
            self.cell(54, 8, name)

            self.f(8, False, G2)
            self.set_xy(x + 4, y + 18)
            self.multi_cell(54, 5, desc)

            self.hl(y + 36, G3, 0.2)
            self.f(7, False, G2)
            self.set_xy(x + 4, y + 38); self.cell(28, 5, "СТОИМОСТЬ")
            self.set_xy(x + 32, y + 38); self.cell(26, 5, "СРОК", align="R")
            self.f(10, True, W)
            self.set_xy(x + 4, y + 44); self.cell(28, 8, price)
            self.f(10, True, c)
            self.set_xy(x + 32, y + 44); self.cell(26, 8, term, align="R")

            self.hl(y + 56, G3, 0.2)
            self.f(8.5, False, G1)
            for j, pt in enumerate(pts):
                yp = y + 62 + j * 20
                self.dot(x + 8, yp + 4.5, 2.5, c)
                self.set_xy(x + 14, yp)
                self.multi_cell(46, 5.5, pt)

        # Лайфхак
        self.box(14, 266, 182, 20, BG3)
        self.box(14, 266, 4, 20, GR)
        self.f(9, True, GR)
        self.set_xy(24, 270); self.cell(30, 6, "Лайфхак:")
        self.f(9, False, G1)
        self.set_xy(24, 278)
        self.cell(164, 6, "Лендинг + Telegram-бот при меньшем бюджете бьют дорогой сайт по конверсии")

    # ─── СТРАНИЦА 4: КЕЙСЫ ───────────────────────────────────────────────────
    def p_cases(self):
        self.page_base()
        self.section_mark(3, "Реальные кейсы")

        self.f(30, True, W)
        self.set_xy(20, 32)
        self.multi_cell(170, 13, "Результаты клиентов\nв цифрах", "L")

        cases = [
            (GOLD, "Telegram-бот", "Производство мебельных фасадов",
             "Менеджер вручную обрабатывал заявки — полдня уходило на переписку.",
             [("Заявок/мес",  "18 → 67",   GR, "+272%"),
              ("Время ответа","4ч → 2мин", GR, "-97%"),
              ("Конверсия",   "2.1 → 8.4%",GR, "+300%")]),
            (GR,   "Лендинг",    "Юридические услуги онлайн",
             "Старый сайт давал дорогой трафик с конверсией 1.2%. Лид — 3200 руб.",
             [("Стоимость лида","3200→890р.", GR, "-72%"),
              ("Конверсия",    "1.2→4.8%",   GR, "+300%"),
              ("Окупился за",  "18 дней",    GR, "ROI 840%")]),
            (BL,   "Сайт + Бот", "Строительная компания",
             "Работали только по сарафану. Не было онлайн-присутствия совсем.",
             [("Новых клиентов","+14/мес",  GR, "с нуля"),
              ("Средний чек",   "+42%",     GR, "доверие"),
              ("ROI за год",    "1840%",    GR, "окупился")]),
        ]

        for i, (c, tool, niche, problem, results) in enumerate(cases):
            y = 84 + i * 66
            self.box(14, y, 182, 60, BG3)
            self.box(14, y, 4, 60, c)

            self.badge(22, y + 7, f"  {tool}  ", c, BG, 8)
            self.f(11, True, W)
            self.set_xy(22, y + 20); self.cell(90, 7, niche)

            self.f(8.5, False, G2)
            self.set_xy(22, y + 30)
            self.multi_cell(85, 5, problem)

            self.vl(115, y + 4, y + 56, G3)

            for j, (label, val, vc, extra) in enumerate(results):
                x = 120 + j * 26
                self.f(7, False, G2)
                self.set_xy(x, y + 8); self.cell(24, 5, label, align="C")
                self.f(10, True, vc)
                self.set_xy(x, y + 14); self.cell(24, 8, val, align="C")
                self.f(7.5, True, c)
                self.set_xy(x, y + 24); self.cell(24, 5, extra, align="C")

    # ─── СТРАНИЦА 5: АЛГОРИТМ ────────────────────────────────────────────────
    def p_algo(self):
        self.page_base()
        self.section_mark(4, "Алгоритм выбора")

        self.f(30, True, W)
        self.set_xy(20, 32)
        self.multi_cell(170, 13, "5 вопросов — и ответ\nстанет очевидным", "L")

        qs = [
            (GOLD, "Откуда клиенты?",
             "Таргет / контекст → ",  GR,   "Лендинг",
             "Telegram / органика → ", GOLD, "Бот"),
            (GR,   "Нужна автоматизация?",
             "Да, без менеджера → ",  GOLD, "Бот",
             "Нет, просто заявка → ", GR,   "Лендинг"),
            (BL,   "Один оффер или каталог?",
             "Один продукт / услуга →", GR, "Лендинг",
             "Много услуг / товаров →", BL,  "Сайт"),
            (AM,   "Повторный контакт без рекламы?",
             "Да, нужны рассылки → ",  GOLD, "Бот",
             "Нет, ретаргет → ",       GR,   "Лендинг"),
            (G1,   "Бюджет и срок?",
             "До 30 000 руб / быстро →", GOLD, "Бот или лендинг",
             "Есть ресурс → ",           BL,   "Сайт"),
        ]

        for i, (c, q, a1, c1, r1, a2, c2, r2) in enumerate(qs):
            y = 86 + i * 40
            self.box(14, y, 182, 35, BG3)
            self.box(14, y, 4, 35, c)

            # Номер
            self.f(22, True, G3)
            self.set_xy(16, y + 4); self.cell(14, 14, str(i + 1), align="C")

            # Вопрос
            self.f(11, True, W)
            self.set_xy(34, y + 8); self.cell(150, 8, q)

            # Ответы
            self.dot(34, y + 24, 2.5, GR)
            self.f(9, False, G1)
            self.set_xy(40, y + 20); self.cell(55, 7, a1)
            self.f(9, True, c1)
            self.set_xy(97, y + 20); self.cell(40, 7, r1)

            self.dot(34, y + 31, 2.5, RS)
            self.f(9, False, G1)
            self.set_xy(40, y + 27); self.cell(55, 7, a2)
            self.f(9, True, c2)
            self.set_xy(97, y + 27); self.cell(40, 7, r2)

    # ─── СТРАНИЦА 6: CTA ─────────────────────────────────────────────────────
    def p_cta(self):
        self.page_base(dark=True)

        # Акцентный блок сверху
        self.box(5, 4, 205, 115, BG2)
        self.box(5, 4, 205, 3, GOLD)

        self.f(7, True, GOLD)
        self.set_xy(20, 18); self.cell(0, 5, "СЛЕДУЮЩИЙ ШАГ")

        self.f(34, True, W)
        self.set_xy(20, 30)
        self.multi_cell(170, 14, "Обсудим ваш\nпроект?", "C")

        self.f(12, False, G2)
        self.set_xy(20, 82)
        self.multi_cell(170, 7,
            "Бесплатный 20-минутный разбор.\n"
            "Покажу примеры — назову цену и срок.", "C")

        # Кнопка
        self.box(60, 110, 90, 15, GOLD)
        self.f(11.5, True, BG)
        self.set_xy(60, 111); self.cell(90, 13, "Записаться →", align="C")

        # Три обещания
        promises = [(GR, "Бесплатно"), (GOLD, "Без давления"), (BL, "Конкретный план")]
        for i, (c, t) in enumerate(promises):
            x = 20 + i * 60
            self.dot(x + 24, 143, 3.5, c)
            self.f(9, True, c)
            self.set_xy(x, 150); self.cell(48, 6, t, align="C")

        # Четыре цифры доверия
        proof = [
            (GOLD, "50+",  "проектов"),
            (GR,   "7+",   "лет опыта"),
            (BL,   "24ч",  "время ответа"),
            (AM,   "100%", "гарантия"),
        ]
        for i, (c, n, l) in enumerate(proof):
            x = 14 + i * 49
            self.box(x, 164, 45, 40, BG3)
            self.box(x, 164, 45, 3, c)
            self.f(22, True, c)
            self.set_xy(x, 169); self.cell(45, 14, n, align="C")
            self.f(8, False, G2)
            self.set_xy(x, 185); self.cell(45, 6, l, align="C")

        # Что делаю
        self.f(10, True, W)
        self.set_xy(20, 218); self.cell(0, 7, "Что делаю:")
        skills = [
            (GOLD, "Telegram-боты под ключ — воронки, рассылки, запись"),
            (GR,   "Лендинги с высокой конверсией — от 5 дней"),
            (BL,   "Многостраничные сайты — SEO, каталог, портфолио"),
        ]
        for i, (c, t) in enumerate(skills):
            y = 230 + i * 13
            self.dot(24, y + 3.5, 3, c)
            self.f(10, False, G1)
            self.set_xy(31, y); self.cell(158, 7, t)

        # Футер
        self.box(0, 272, 210, 25, BG2)
        self.hl(272, GOLD, 0.4)
        self.f(8, False, G2)
        self.set_xy(0, 281)
        self.cell(210, 6,
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
        print("Шрифты не найдены, пропускаем генерацию PDF")
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
