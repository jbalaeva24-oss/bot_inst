"""
Лид-магнит PDF — дизайн в стиле КП:
тёмный фон, золото, точечный паттерн, декоративные элементы.
"""
import os
from pathlib import Path
from fpdf import FPDF

BASE = Path(__file__).parent
OUT  = str(BASE / "assets" / "guide.pdf")
os.makedirs(str(BASE / "assets"), exist_ok=True)

# ── Палитра (как в offer_card.py) ────────────────────────────────────────────
DARK   = (16,  13,   8)
DARK2  = (28,  23,  13)
DARK3  = (42,  36,  20)
DLINE  = (55,  48,  28)
GOLD   = (196, 148,  58)
GOLD_L = (230, 185,  90)
GOLD_D = (120,  88,  24)
WHITE  = (255, 255, 255)
OFFWH  = (232, 226, 208)
LGRAY  = (155, 145, 118)
GREEN  = (82,  180,  90)
RED    = (190,  75,  65)


class PDF(FPDF):

    # ── Шрифт ────────────────────────────────────────────────────────────────
    def f(self, sz=11, b=False, c=WHITE):
        self.set_font("R", "B" if b else "", sz)
        self.set_text_color(*c)

    # ── Примитивы ────────────────────────────────────────────────────────────
    def box(self, x, y, w, h, c):
        self.set_fill_color(*c)
        self.rect(x, y, w, h, "F")

    def line_h(self, y, c=DLINE, lw=0.25):
        self.set_draw_color(*c)
        self.set_line_width(lw)
        self.line(0, y, 210, y)

    def line_v(self, x, y1, y2, c=DLINE, lw=0.25):
        self.set_draw_color(*c)
        self.set_line_width(lw)
        self.line(x, y1, x, y2)

    def dot(self, x, y, r, c):
        self.set_fill_color(*c)
        self.ellipse(x - r, y - r, r * 2, r * 2, "F")

    def circle_out(self, cx, cy, r, c, lw=0.2):
        self.set_draw_color(*c)
        self.set_line_width(lw)
        self.ellipse(cx - r, cy - r, r * 2, r * 2, "D")

    def diamond(self, cx, cy, s, c, lw=0.3):
        self.set_draw_color(*c)
        self.set_line_width(lw)
        # FPDF не имеет polygon — рисуем 4 линии
        self.line(cx,     cy - s, cx + s, cy    )
        self.line(cx + s, cy,     cx,     cy + s)
        self.line(cx,     cy + s, cx - s, cy    )
        self.line(cx - s, cy,     cx,     cy - s)

    def gold_check(self, x, y, r=2.8):
        """Золотой круг с галочкой."""
        self.set_draw_color(*GOLD)
        self.set_line_width(0.4)
        self.ellipse(x - r, y - r, r * 2, r * 2, "D")
        self.set_draw_color(*GOLD)
        self.set_line_width(0.5)
        self.line(x - 1.2, y + 0.2, x - 0.2, y + 1.4)
        self.line(x - 0.2, y + 1.4, x + 1.8,  y - 1.0)

    # ── Базовый фон страницы ─────────────────────────────────────────────────
    def page_bg(self):
        """Тёмный фон + точечный паттерн + золотые полосы."""
        # Фон
        self.box(0, 0, 210, 297, DARK)
        # Точки (сетка 8мм)
        self.set_fill_color(42, 36, 18)
        step = 8
        for gx in range(0, 220, step):
            for gy in range(0, 305, step):
                self.ellipse(gx - 0.4, gy - 0.4, 0.8, 0.8, "F")
        # Золотая полоса сверху
        self.box(0, 0, 210, 1.2, GOLD)
        # Золотая полоса слева
        for xi in range(4):
            alpha = 1 - xi * 0.25
            c = tuple(int(GOLD[j] * alpha) for j in range(3))
            self.set_fill_color(*c)
            self.rect(xi * 0.4, 0, 0.4, 297, "F")

    def deco_rings(self, cx, cy, rings=(30, 22, 15, 9)):
        """Концентрические кольца как в offer_card."""
        shades = [(38, 32, 16), (48, 42, 20), (58, 50, 24), GOLD_D]
        for r, sh in zip(rings, shades):
            self.circle_out(cx, cy, r, sh, lw=0.2)

    def deco_diamond(self, cx, cy):
        """Трёхслойный ромб."""
        self.diamond(cx, cy, 12, DARK3, lw=0.3)
        self.diamond(cx, cy,  8, DLINE, lw=0.3)
        self.diamond(cx, cy,  4, GOLD_D, lw=0.4)

    def section_label(self, num, title):
        self.f(7, True, GOLD)
        self.set_xy(18, 15)
        self.cell(0, 5, f"{num:02d}  /  {title.upper()}")
        self.line_h(22, DLINE)

    def feat_item(self, x, y, text, w=80):
        """Блок фичи с золотым чеком."""
        # фон блока
        self.set_fill_color(*DARK2)
        self.rect(x - 2, y - 1.5, w, 10, "F")
        self.set_fill_color(*GOLD_D)
        self.rect(x - 2, y - 1.5, 1.2, 10, "F")
        self.gold_check(x + 4, y + 3.3)
        self.f(9, False, OFFWH)
        self.set_xy(x + 9, y)
        self.multi_cell(w - 11, 5, text)

    # ─────────────────────────────────────────────────────────────────────────
    # ОБЛОЖКА
    # ─────────────────────────────────────────────────────────────────────────
    def cover(self):
        self.page_bg()

        # Декор: кольца левый низ
        self.deco_rings(0, 297, rings=(55, 40, 28, 16))
        # Декор: ромб правый верх
        self.deco_diamond(198, 12)
        # Ещё один ромб меньше
        self.diamond(185, 22, 6, DARK3, lw=0.2)

        # Бейдж
        self.f(8, True, GOLD)
        self.set_xy(18, 26)
        self.cell(0, 5, "БЕСПЛАТНЫЙ ГИД")
        self.set_fill_color(*GOLD_D)
        self.rect(18, 32, 55, 0.6, "F")

        # Заголовок
        self.f(42, True, WHITE)
        self.set_xy(18, 38)
        self.multi_cell(120, 17, "Сайт\nили бот?", "L")

        # Золотая подчёркивающая линия
        self.box(18, 88, 65, 1.5, GOLD)

        self.f(11, False, LGRAY)
        self.set_xy(18, 95)
        self.multi_cell(120, 6.5,
            "Как выбрать правильный инструмент\n"
            "и не потратить деньги впустую", "L")

        # Буллеты
        feats = [
            "Сравнение 3 инструментов",
            "3 реальных кейса с цифрами",
            "Алгоритм выбора за 5 шагов",
            "Частые ошибки и как их избежать",
        ]
        y = 120
        for t in feats:
            self.gold_check(22, y + 3)
            self.f(10, False, OFFWH)
            self.set_xy(28, y - 0.5)
            self.cell(100, 7, t)
            y += 13

        # Вертикальный разделитель
        self.line_v(145, 25, 265, DLINE)
        self.line_v(146, 25, 265, GOLD_D)

        # Правая панель: большая цифра
        self.f(68, True, DARK3)
        self.set_xy(148, 38)
        self.cell(58, 48, "73", align="C")

        self.f(26, True, GOLD)
        self.set_xy(148, 82)
        self.cell(58, 16, "%", align="C")

        self.f(8, False, LGRAY)
        self.set_xy(148, 100)
        self.multi_cell(58, 5, "бизнесов выбирают\nне тот инструмент", align="C")

        # Три мини-блока
        facts = [
            (GOLD,  "60-80%", "открываемость\nTelegram"),
            (GREEN, "3x",     "дешевле лид\nс лендинга"),
            ((90, 160, 220), "7 дней", "средний срок\nзапуска бота"),
        ]
        for i, (c, n, l) in enumerate(facts):
            fy = 128 + i * 36
            self.box(148, fy, 57, 32, DARK2)
            self.box(148, fy, 57, 1.5, c)
            self.f(18, True, c)
            self.set_xy(148, fy + 3)
            self.cell(57, 12, n, align="C")
            self.f(7.5, False, LGRAY)
            self.set_xy(148, fy + 16)
            self.multi_cell(57, 4.5, l, align="C")

        # Нижняя плашка
        self.box(0, 267, 210, 30, DARK2)
        self.box(0, 267, 210, 1.5, GOLD)
        self.f(8, False, LGRAY)
        self.set_xy(0, 276)
        self.cell(210, 6,
            "6 страниц  •  12 минут  •  Бесплатно  •  Сайты и Telegram-боты",
            align="C")

    # ─────────────────────────────────────────────────────────────────────────
    # СТРАНИЦА 2: ПРОБЛЕМА
    # ─────────────────────────────────────────────────────────────────────────
    def p_problem(self):
        self.page_bg()
        self.deco_rings(210, 0, rings=(40, 28, 18))
        self.deco_diamond(18, 285)
        self.section_label(1, "Почему это важно")

        self.f(28, True, WHITE)
        self.set_xy(18, 28)
        self.multi_cell(174, 12, "Почему большинство\nтратит деньги зря", "L")

        self.f(10, False, OFFWH)
        self.set_xy(18, 66)
        self.multi_cell(174, 6,
            "Каждый день ко мне приходят предприниматели с похожей историей. "
            "Потратили 80 000 рублей на сайт — заявок нет. "
            "Сделали лендинг — а клиенты сидят в Telegram. "
            "Заказали бот — а нужен был нормальный сайт с SEO.\n\n"
            "Причина одна: инструмент выбирается по совету знакомых, "
            "а не по реальной задаче.", "L")

        # Три статистики
        stats = [
            (GOLD,  "73%",   "выбирают\nне тот инструмент"),
            (RED,   "2.4x",  "дороже обходится\nпеределка"),
            (GREEN, "87 дн", "теряют в среднем\nна ошибочный путь"),
        ]
        for i, (c, n, l) in enumerate(stats):
            x = 18 + i * 62
            self.box(x, 122, 58, 52, DARK2)
            self.box(x, 122, 58, 2, c)
            self.f(26, True, c)
            self.set_xy(x, 126)
            self.cell(58, 16, n, align="C")
            self.f(8, False, LGRAY)
            self.set_xy(x, 145)
            self.multi_cell(58, 5, l, align="C")

        # Цитата
        self.box(18, 184, 174, 30, DARK2)
        self.box(18, 184, 3, 30, GOLD)
        self.f(11, True, WHITE)
        self.set_xy(26, 190)
        self.multi_cell(162, 7,
            "«Правильный инструмент — это половина успеха.\n"
            "Этот гайд поможет выбрать его за 12 минут.»")

        self.f(10, True, WHITE)
        self.set_xy(18, 225); self.cell(0, 7, "Типичные ошибки:")

        errs = [
            "Сделали многостраничный сайт — а нужен был лендинг под рекламу",
            "Заказали лендинг — а 80% клиентов приходят через Telegram",
            "Потратили 100 000 руб. на сайт — а бот за 20 000 дал бы больше",
        ]
        for i, e in enumerate(errs):
            self.feat_item(18, 236 + i * 13, e, w=174)

    # ─────────────────────────────────────────────────────────────────────────
    # СТРАНИЦА 3: СРАВНЕНИЕ
    # ─────────────────────────────────────────────────────────────────────────
    def p_compare(self):
        self.page_bg()
        self.deco_rings(0, 297, rings=(45, 32, 20))
        self.deco_diamond(198, 285)
        self.section_label(2, "Сравнение инструментов")

        self.f(28, True, WHITE)
        self.set_xy(18, 28)
        self.multi_cell(174, 12, "Три инструмента —\nтри разные задачи", "L")

        tools = [
            (GOLD,  "Telegram-бот", "от 20 000 руб.", "3-7 дней",
             "Автоматизация\nи повторный контакт",
             ["Работает 24/7 без менеджера",
              "Push открывают 60-80%",
              "Воронка, запись, рассылки",
              "Повторный контакт бесплатно"]),
            (GREEN, "Лендинг", "от 25 000 руб.", "5-10 дней",
             "Конверсия\nрекламного трафика",
             ["Максимум конверсии с рекламы",
              "Один оффер — фокус",
              "Быстрый запуск и окупаемость",
              "A/B-тест за неделю"]),
            ((90, 160, 220), "Сайт", "от 40 000 руб.", "10-14 дней",
             "SEO и долгосрочный\nактив бизнеса",
             ["SEO-трафик без рекламы",
              "Каталог и портфолио",
              "Доверие и репутация",
              "Работает годами"]),
        ]

        for i, (c, name, price, term, desc, pts) in enumerate(tools):
            x = 14 + i * 65
            y = 82
            self.box(x, y, 62, 178, DARK2)
            self.box(x, y, 62, 2.5, c)

            self.f(11, True, c)
            self.set_xy(x + 3, y + 6)
            self.cell(56, 8, name)

            self.f(7.5, False, LGRAY)
            self.set_xy(x + 3, y + 16)
            self.multi_cell(56, 4.5, desc)

            self.line_h(y + 30, DLINE)
            self.f(7, False, LGRAY)
            self.set_xy(x + 3, y + 33); self.cell(28, 4, "СТОИМОСТЬ")
            self.set_xy(x + 31, y + 33); self.cell(27, 4, "СРОК", align="R")
            self.f(10, True, WHITE)
            self.set_xy(x + 3, y + 38); self.cell(28, 7, price)
            self.f(10, True, c)
            self.set_xy(x + 31, y + 38); self.cell(27, 7, term, align="R")

            self.line_h(y + 50, DLINE)
            for j, pt in enumerate(pts):
                py = y + 54 + j * 28
                self.feat_item(x + 3, py, pt, w=57)

        # Лайфхак
        self.box(14, 268, 182, 16, DARK2)
        self.box(14, 268, 3, 16, GREEN)
        self.f(9, True, GREEN); self.set_xy(22, 271); self.cell(28, 6, "Лайфхак:")
        self.f(9, False, OFFWH); self.set_xy(52, 271)
        self.cell(140, 6, "Лендинг + Telegram-бот при меньшем бюджете дают больше конверсий")

    # ─────────────────────────────────────────────────────────────────────────
    # СТРАНИЦА 4: КЕЙСЫ
    # ─────────────────────────────────────────────────────────────────────────
    def p_cases(self):
        self.page_bg()
        self.deco_rings(210, 297, rings=(40, 28, 18))
        self.deco_diamond(18, 12)
        self.section_label(3, "Реальные кейсы")

        self.f(28, True, WHITE)
        self.set_xy(18, 28)
        self.multi_cell(174, 12, "Результаты клиентов\nв цифрах", "L")

        cases = [
            (GOLD,  "Telegram-бот", "Производство мебельных фасадов",
             "Менеджер вручную обрабатывал заявки — полдня уходило на переписку.",
             [("Заявок/мес",   "18 > 67",    GREEN, "+272%"),
              ("Время ответа", "4ч > 2мин",  GREEN, "-97%"),
              ("Конверсия",    "2.1 > 8.4%", GREEN, "+300%")]),
            (GREEN, "Лендинг", "Юридические услуги онлайн",
             "Старый сайт давал дорогой трафик с конверсией 1.2%. Лид — 3200 руб.",
             [("Стоимость лида", "3200>890р.", GREEN, "-72%"),
              ("Конверсия",      "1.2>4.8%",  GREEN, "+300%"),
              ("Окупился за",    "18 дней",   GREEN, "ROI 840%")]),
            ((90, 160, 220), "Сайт + Бот", "Строительная компания",
             "Работали только по сарафану. Не было онлайн-присутствия совсем.",
             [("Новых клиентов", "+14/мес", GREEN, "с нуля"),
              ("Средний чек",    "+42%",    GREEN, "доверие"),
              ("ROI за год",     "1840%",   GREEN, "окупился")]),
        ]

        for i, (c, tool, niche, problem, results) in enumerate(cases):
            y = 82 + i * 65
            self.box(14, y, 182, 58, DARK2)
            self.box(14, y, 3, 58, c)

            # Бейдж
            self.f(7.5, True, DARK)
            bw = self.get_string_width(tool) + 8
            self.set_fill_color(*c)
            self.rect(20, y + 5, bw, 7, "F")
            self.set_xy(20, y + 5.5)
            self.cell(bw, 6, tool, align="C")

            self.f(10, True, WHITE)
            self.set_xy(20, y + 16); self.cell(85, 7, niche)
            self.f(8, False, LGRAY)
            self.set_xy(20, y + 25)
            self.multi_cell(72, 5, problem)

            # Результаты
            self.line_v(100, y + 5, y + 53, DLINE)
            for j, (label, val, vc, extra) in enumerate(results):
                rx = 106 + j * 30
                self.f(7, False, LGRAY)
                self.set_xy(rx, y + 6); self.cell(28, 5, label, align="C")
                self.f(9, True, vc)
                self.set_xy(rx, y + 12); self.cell(28, 7, val, align="C")
                self.f(7.5, True, c)
                self.set_xy(rx, y + 20); self.cell(28, 5, extra, align="C")

    # ─────────────────────────────────────────────────────────────────────────
    # СТРАНИЦА 5: АЛГОРИТМ
    # ─────────────────────────────────────────────────────────────────────────
    def p_algo(self):
        self.page_bg()
        self.deco_rings(0, 0, rings=(45, 32, 20))
        self.deco_diamond(198, 12)
        self.section_label(4, "Алгоритм выбора")

        self.f(28, True, WHITE)
        self.set_xy(18, 28)
        self.multi_cell(174, 12, "5 вопросов — и ответ\nстанет очевидным", "L")

        qs = [
            (GOLD,  "Откуда приходят клиенты?",
             "Таргет / контекст ->", GREEN, "Лендинг",
             "Telegram / органика ->", GOLD, "Бот"),
            (GREEN, "Нужна автоматизация?",
             "Да, без менеджера ->", GOLD, "Бот",
             "Нет, просто заявка ->", GREEN, "Лендинг"),
            ((90,160,220), "Один оффер или каталог?",
             "Один продукт / услуга ->", GREEN, "Лендинг",
             "Много услуг / товаров ->", (90,160,220), "Сайт"),
            (GOLD,  "Нужен повторный контакт бесплатно?",
             "Да, нужны рассылки ->", GOLD, "Бот",
             "Нет, ретаргет ->", GREEN, "Лендинг"),
            (GREEN, "Какой бюджет и срок?",
             "До 30 000 руб / срочно ->", GOLD, "Бот или лендинг",
             "Есть ресурс ->", (90,160,220), "Сайт"),
        ]

        for i, (c, q, a1, c1, r1, a2, c2, r2) in enumerate(qs):
            y = 82 + i * 40
            self.box(14, y, 182, 34, DARK2)
            self.box(14, y, 3, 34, c)

            # Номер
            self.f(20, True, DARK3)
            self.set_xy(16, y + 3); self.cell(14, 14, str(i + 1), align="C")

            self.f(10, True, WHITE)
            self.set_xy(34, y + 7); self.cell(150, 7, q)

            self.dot(34, y + 21, 1.8, GREEN)
            self.f(8.5, False, OFFWH); self.set_xy(38, y + 18); self.cell(55, 6, a1)
            self.f(8.5, True, c1);     self.set_xy(95, y + 18); self.cell(40, 6, r1)

            self.dot(34, y + 29, 1.8, RED)
            self.f(8.5, False, OFFWH); self.set_xy(38, y + 26); self.cell(55, 6, a2)
            self.f(8.5, True, c2);     self.set_xy(95, y + 26); self.cell(40, 6, r2)

    # ─────────────────────────────────────────────────────────────────────────
    # СТРАНИЦА 6: CTA
    # ─────────────────────────────────────────────────────────────────────────
    def p_cta(self):
        self.page_bg()
        self.deco_rings(210, 297, rings=(55, 40, 28, 16))
        self.deco_diamond(198, 12)
        self.diamond(185, 22, 6, DARK3)

        # Акцентный блок сверху
        self.box(5, 4, 205, 112, DARK2)
        self.box(5, 4, 205, 1.5, GOLD)

        self.f(7, True, GOLD); self.set_xy(18, 15); self.cell(0, 5, "СЛЕДУЮЩИЙ ШАГ")

        self.f(32, True, WHITE)
        self.set_xy(18, 26)
        self.multi_cell(174, 13, "Обсудим ваш\nпроект?", "C")

        self.f(11, False, LGRAY)
        self.set_xy(18, 78)
        self.multi_cell(174, 6.5,
            "Бесплатный 20-минутный разбор.\n"
            "Покажу примеры — назову цену и срок.", "C")

        # Кнопка
        self.set_fill_color(*GOLD)
        self.rect(65, 106, 80, 13, "F")
        self.f(11, True, DARK); self.set_xy(65, 107); self.cell(80, 11, "Записаться ->", align="C")

        # Три обещания
        promises = [(GREEN, "Бесплатно"), (GOLD, "Без давления"), ((90,160,220), "Конкретный план")]
        for i, (c, t) in enumerate(promises):
            x = 22 + i * 58
            self.dot(x + 22, 133, 2.8, c)
            self.f(8.5, True, c); self.set_xy(x, 138); self.cell(44, 5, t, align="C")

        # Четыре блока
        proof = [(GOLD, "50+", "проектов"), (GREEN, "7+", "лет опыта"),
                 ((90,160,220), "24ч", "ответ"),  (GOLD, "100%", "гарантия")]
        for i, (c, n, l) in enumerate(proof):
            x = 14 + i * 49
            self.box(x, 155, 45, 38, DARK2)
            self.box(x, 155, 45, 2, c)
            self.f(20, True, c); self.set_xy(x, 159); self.cell(45, 13, n, align="C")
            self.f(7.5, False, LGRAY); self.set_xy(x, 174); self.cell(45, 5, l, align="C")

        # Список услуг
        self.f(10, True, WHITE); self.set_xy(18, 205); self.cell(0, 7, "Что делаю:")
        skills = [
            (GOLD,          "Telegram-боты под ключ — воронки, рассылки, запись"),
            (GREEN,         "Лендинги с высокой конверсией — от 5 дней"),
            ((90,160,220),  "Многостраничные сайты — SEO, каталог, портфолио"),
        ]
        for i, (c, t) in enumerate(skills):
            y = 216 + i * 13
            self.gold_check(22, y + 3)
            self.f(9.5, False, OFFWH); self.set_xy(28, y); self.cell(170, 7, t)

        # Нижняя плашка
        self.box(0, 268, 210, 29, DARK2)
        self.box(0, 268, 210, 1.5, GOLD)
        self.f(8, False, LGRAY)
        self.set_xy(0, 278)
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
