"""
Продающий PDF-гайд — бежевый дизайн, белые карточки, оранжевые акценты.
"""
import os
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
GREEN   = ( 60, 150,  70)
RED     = (190,  75,  65)
BLUE    = ( 70, 130, 190)


class PDF(FPDF):

    def f(self, sz=11, b=False, c=DARK):
        self.set_font("R", "B" if b else "", sz)
        self.set_text_color(*c)

    def box(self, x, y, w, h, c, r=0):
        self.set_fill_color(*c)
        if r:
            self.set_draw_color(*c)
            try:
                self.rounded_rect(x, y, w, h, r, corner_style="ABCD", style="F")
            except Exception:
                self.rect(x, y, w, h, "F")
        else:
            self.rect(x, y, w, h, "F")

    def rr(self, x, y, w, h, r, c):
        self.set_fill_color(*c)
        self.set_draw_color(*c)
        try:
            self.rounded_rect(x, y, w, h, r, corner_style="ABCD", style="F")
        except Exception:
            self.rect(x, y, w, h, "F")

    def dot(self, x, y, r, c):
        self.set_fill_color(*c)
        self.ellipse(x - r, y - r, r * 2, r * 2, "F")

    def hl(self, y, c=CARD_SH, lw=0.3):
        self.set_draw_color(*c)
        self.set_line_width(lw)
        self.line(0, y, 210, y)

    def page_bg(self):
        self.set_fill_color(*BG)
        self.rect(0, 0, 210, 297, "F")
        for i in range(12):
            t = i / 11
            c = tuple(int(BG[j] + (BG2[j] - BG[j]) * t) for j in range(3))
            self.set_fill_color(*c)
            self.rect(0, 180 + i * 10, 210, 11, "F")

    def white_card(self, x, y, w, h, r=5):
        self.set_fill_color(*CARD_SH)
        try:
            self.rounded_rect(x + 1.5, y + 1.5, w, h, r, corner_style="ABCD", style="F")
        except Exception:
            self.rect(x + 1.5, y + 1.5, w, h, "F")
        self.set_fill_color(*WHITE)
        try:
            self.rounded_rect(x, y, w, h, r, corner_style="ABCD", style="F")
        except Exception:
            self.rect(x, y, w, h, "F")

    def icon_check(self, x, y, s=8):
        self.rr(x, y, s, s, 2, ORANGE_L)
        cx, cy = x + s / 2, y + s / 2
        self.set_draw_color(*ORANGE)
        self.set_line_width(0.65)
        self.line(cx - 2, cy, cx - 0.5, cy + 2)
        self.line(cx - 0.5, cy + 2, cx + 2.5, cy - 1.5)

    def icon_x(self, x, y, s=8):
        self.rr(x, y, s, s, 2, (255, 230, 225))
        cx, cy = x + s / 2, y + s / 2
        self.set_draw_color(*RED)
        self.set_line_width(0.65)
        self.line(cx - 2, cy - 2, cx + 2, cy + 2)
        self.line(cx + 2, cy - 2, cx - 2, cy + 2)

    def badge(self, x, y, text, bg=ORANGE, tc=WHITE, sz=8):
        self.f(sz, True, tc)
        w = self.get_string_width(text) + 6
        self.rr(x, y, w, 7, 2, bg)
        self.set_xy(x + 1, y + 0.8)
        self.cell(w - 2, 5.5, text, align="C")

    def section_label(self, num, title):
        self.f(7, True, ORANGE)
        self.set_xy(14, 14)
        self.cell(0, 5, f"{num:02d}  /  {title.upper()}")
        self.set_fill_color(*ORANGE)
        self.rect(14, 21, 30, 0.8, "F")
        self.set_fill_color(*CARD_SH)
        self.rect(44, 21.3, 152, 0.4, "F")

    def num_circle(self, cx, cy, n, c):
        self.set_fill_color(*c)
        self.ellipse(cx - 6, cy - 6, 12, 12, "F")
        self.f(9, True, WHITE)
        self.set_xy(cx - 6, cy - 5.5)
        self.cell(12, 10, str(n), align="C")

    # ─────────────────────────────────────────────────────────────────────────
    # ОБЛОЖКА
    # ─────────────────────────────────────────────────────────────────────────
    def cover(self):
        self.page_bg()

        # Верхняя оранжевая полоска
        self.rr(0, 0, 210, 6, 0, ORANGE)

        # Метка
        self.f(7, True, ORANGE)
        self.set_xy(14, 14)
        self.cell(0, 5, "ВЕБ-РАЗРАБОТКА ПОД КЛЮЧ  /  КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ")
        self.set_fill_color(*ORANGE)
        self.rect(14, 21, 50, 0.8, "F")
        self.set_fill_color(*CARD_SH)
        self.rect(64, 21.3, 132, 0.4, "F")

        # Левая белая карточка
        self.white_card(12, 28, 115, 200, r=6)

        # Заголовок
        self.f(8, True, ORANGE)
        self.set_xy(20, 36)
        self.cell(0, 5, "САЙТЫ И TELEGRAM-БОТЫ")

        self.f(24, True, DARK)
        self.set_xy(20, 44)
        self.multi_cell(100, 11, "Продающий\nсайт или бот\nпод ключ", "L")

        self.f(10, False, DGRAY)
        self.set_xy(20, 84)
        self.multi_cell(100, 5.5,
            "Создаём инструменты, которые\n"
            "приносят заявки — а не просто\n"
            "красиво выглядят.", "L")

        # Буллеты
        bullets = [
            "Запуск за 3–14 дней",
            "Адаптация под мобильные",
            "Форма заявки + Telegram",
            "Гарантия результата",
        ]
        by = 114
        for t in bullets:
            self.icon_check(20, by + 0.5, 6)
            self.f(9, False, DARK)
            self.set_xy(28, by)
            self.cell(98, 6.5, t)
            by += 10

        # Оранжевая кнопка
        self.rr(20, 200, 100, 12, 3, ORANGE)
        self.f(10, True, WHITE)
        self.set_xy(20, 202)
        self.cell(100, 8, "Записаться на разбор  →", align="C")

        # Правая панель
        facts = [
            (ORANGE,  "50+",    "проектов\nсдано"),
            (GREEN,   "7+",     "лет\nопыта"),
            (BLUE,    "14 дн",  "макс срок\nзапуска"),
        ]
        for i, (c, n, l) in enumerate(facts):
            fy = 34 + i * 58
            self.white_card(133, fy, 63, 50, r=4)
            self.rr(133, fy, 63, 2.5, 4, c)
            self.f(22, True, c)
            self.set_xy(133, fy + 5)
            self.cell(63, 14, n, align="C")
            self.f(8, False, LGRAY)
            self.set_xy(133, fy + 21)
            self.multi_cell(63, 4.5, l, align="C")

        # Нижняя плашка
        self.rr(12, 240, 186, 46, 5, BAR_BG)
        stats = [
            ("50% СТАРТ",  "Предоплата"),
            ("50% СДАЧА",  "При приёмке"),
            ("ГАРАНТИЯ",   "Результата"),
        ]
        sw = 62
        for i, (v, l) in enumerate(stats):
            sx = 12 + i * sw
            self.set_fill_color(*DARK)
            self.ellipse(sx + 10, 250, 10, 10, "F")
            self.f(8, True, ORANGE)
            self.set_xy(sx + 23, 250)
            self.cell(sw - 26, 5, v)
            self.f(7, False, DGRAY)
            self.set_xy(sx + 23, 257)
            self.cell(sw - 26, 5, l)
            if i < 2:
                self.set_fill_color(*CARD_SH)
                self.rect(sx + sw - 0.5, 244, 0.5, 36, "F")

    # ─────────────────────────────────────────────────────────────────────────
    # СТРАНИЦА 2: БОЛИ
    # ─────────────────────────────────────────────────────────────────────────
    def p_pain(self):
        self.page_bg()
        self.section_label(1, "Что вы теряете прямо сейчас")

        self.f(21, True, DARK)
        self.set_xy(14, 28)
        self.multi_cell(182, 10, "Пока нет сайта или бота —\nконкуренты уже берут ваших клиентов", "L")

        self.f(9.5, False, DGRAY)
        self.set_xy(14, 58)
        self.multi_cell(182, 5.5,
            "Сегодня 78% клиентов ищут исполнителей онлайн. Без нормального сайта или бота "
            "вы просто невидимы — даже если делаете хорошую работу.", "L")

        # Карточки с болями (слева — проблема, справа — цена)
        pains = [
            ("Нет онлайн-присутствия",
             "Клиенты уходят к конкурентам, у которых красивый сайт — даже если они хуже вас",
             "до 30%", "потеря клиентов"),
            ("Обработка заявок вручную",
             "Менеджер тратит по 4–6 часов в день на переписку, которую бот сделает за секунды",
             "4–6 ч", "в день зря"),
            ("Нет автоматического прогрева",
             "Потенциальный клиент написал — вы ответили через час — он уже ушёл к другому",
             "60%", "уходят без ответа"),
        ]

        for i, (title, desc, stat, stat_l) in enumerate(pains):
            y = 80 + i * 58
            self.white_card(14, y, 182, 50, r=5)
            self.rr(14, y, 3.5, 50, 5, RED)

            # Номер
            self.f(18, True, (240, 230, 220))
            self.set_xy(18, y + 8)
            self.cell(16, 14, str(i + 1))

            self.f(10, True, DARK)
            self.set_xy(36, y + 8)
            self.cell(0, 7, title)
            self.f(8.5, False, DGRAY)
            self.set_xy(36, y + 17)
            self.multi_cell(105, 5, desc)

            # Статистика справа
            self.rr(148, y + 8, 42, 34, 4, ORANGE_L)
            self.f(16, True, ORANGE)
            self.set_xy(148, y + 11)
            self.cell(42, 11, stat, align="C")
            self.f(7, False, DGRAY)
            self.set_xy(148, y + 24)
            self.cell(42, 5, stat_l, align="C")

        # Вывод
        self.white_card(14, 258, 182, 22, r=4)
        self.rr(14, 258, 3.5, 22, 4, ORANGE)
        self.f(9.5, True, DARK)
        self.set_xy(22, 262)
        self.multi_cell(170, 5.5,
            "Решение простое: один раз создать правильный инструмент — "
            "и он будет работать на вас 24/7 без выходных.")

    # ─────────────────────────────────────────────────────────────────────────
    # СТРАНИЦА 3: КЕЙСЫ
    # ─────────────────────────────────────────────────────────────────────────
    def p_cases(self):
        self.page_bg()
        self.section_label(2, "Реальные результаты клиентов")

        self.f(21, True, DARK)
        self.set_xy(14, 28)
        self.multi_cell(182, 10, "Кейсы с цифрами — не просто слова", "L")

        cases = [
            (ORANGE, "Telegram-бот", "Производство фасадов",
             "Заявки обрабатывали вручную — 4+ часа в день.",
             [("Заявок/мес", "18 → 67", "+272%"),
              ("Время ответа", "4 ч → 2 мин", "−97%"),
              ("Конверсия", "2.1 → 8.4%", "+300%")]),
            (GREEN, "Лендинг", "Стилист г. Екатеринбург",
             "Клиенты узнавали через сарафан, сайта не было совсем.",
             [("Заявок в мес.", "0 → 24", "с нуля"),
              ("Стоимость лида", "— → 890 р.", "сразу"),
              ("Окупился за", "18 дней", "ROI 600%")]),
            (BLUE, "Сайт + Бот", "Покрасочный цех",
             "Работали только по рекомендациям, онлайна не было.",
             [("Новых клиентов", "+14/мес", "с нуля"),
              ("Средний чек", "+42%", "доверие"),
              ("Заявки за мес.", "+40%", "рост")]),
        ]

        for i, (c, tool, niche, problem, results) in enumerate(cases):
            y = 54 + i * 72
            self.white_card(14, y, 182, 64, r=5)
            self.rr(14, y, 3.5, 64, 5, c)

            self.badge(20, y + 5, f"  {tool}  ", c, WHITE, 7.5)

            self.f(10, True, DARK)
            self.set_xy(20, y + 16); self.cell(80, 6, niche)
            self.f(8, False, DGRAY)
            self.set_xy(20, y + 24)
            self.multi_cell(75, 4.5, problem)

            # Разделитель
            self.set_draw_color(*CARD_SH)
            self.set_line_width(0.3)
            self.line(101, y + 6, 101, y + 58)

            # Результаты
            for j, (label, val, extra) in enumerate(results):
                rx = 105 + j * 30
                self.f(7, False, LGRAY)
                self.set_xy(rx, y + 8); self.cell(28, 4, label, align="C")
                self.f(10, True, c)
                self.set_xy(rx, y + 14); self.cell(28, 7, val, align="C")
                self.f(8, True, GREEN)
                self.set_xy(rx, y + 23); self.cell(28, 5, extra, align="C")

        # Итог
        self.rr(14, 272, 182, 16, 4, ORANGE_L)
        self.f(9, True, ORANGE)
        self.set_xy(20, 276)
        self.cell(30, 5, "Итог:")
        self.f(9, False, DARK)
        self.set_xy(52, 276)
        self.cell(138, 5, "Средняя окупаемость наших проектов — 1–2 месяца")

    # ─────────────────────────────────────────────────────────────────────────
    # СТРАНИЦА 4: ПАКЕТЫ
    # ─────────────────────────────────────────────────────────────────────────
    def p_packages(self):
        self.page_bg()
        self.section_label(3, "Пакеты и цены")

        self.f(21, True, DARK)
        self.set_xy(14, 28)
        self.multi_cell(182, 10, "Выберите формат под вашу задачу", "L")

        packages = [
            (ORANGE, "БАЗОВЫЙ", "Лендинг / Простой бот",
             "от 20 000 ₽", "3–7 дней",
             [
                 "Продающая структура под вашу нишу",
                 "Форма заявки + уведомление в Telegram",
                 "Адаптация под мобильные",
                 "Инструкция по управлению",
             ]),
            (GREEN, "СТАНДАРТ", "Продающий сайт / Бот-воронка",
             "от 35 000 ₽", "7–10 дней",
             [
                 "6–8 страниц с продающими текстами",
                 "Полная воронка продаж под нишу",
                 "Интеграция с CRM или таблицами",
                 "Онлайн-запись или калькулятор",
             ]),
            (BLUE, "ПРЕМИУМ", "Сайт + Бот под ключ",
             "от 70 000 ₽", "10–14 дней",
             [
                 "Уникальный дизайн под ваш бренд",
                 "Бот-воронка + сайт как единая система",
                 "Интеграция с любыми сервисами",
                 "Продающие тексты под вашу нишу",
             ]),
        ]

        for i, (c, name, subtitle, price, term, feats) in enumerate(packages):
            x = 14 + i * 63
            self.white_card(x, 54, 60, 206, r=5)
            self.rr(x, 54, 60, 3, 5, c)

            self.f(9, True, c)
            self.set_xy(x + 3, 61); self.cell(54, 6, name, align="C")

            self.f(7.5, False, DGRAY)
            self.set_xy(x + 3, 69)
            self.multi_cell(54, 4, subtitle, align="C")

            # Цена
            self.rr(x + 4, 82, 52, 20, 3, ORANGE_L)
            self.f(14, True, ORANGE)
            self.set_xy(x + 4, 84); self.cell(52, 9, price, align="C")
            self.f(7, False, LGRAY)
            self.set_xy(x + 4, 94); self.cell(52, 5, f"Срок: {term}", align="C")

            # Фичи
            for j, feat in enumerate(feats):
                fy = 110 + j * 32
                self.white_card(x + 4, fy, 52, 28, r=3)
                self.icon_check(x + 7, fy + 9, 7)
                self.f(7.5, False, DARK)
                self.set_xy(x + 16, fy + 4)
                self.multi_cell(37, 4.5, feat)

            # Кнопка
            self.rr(x + 4, 244, 52, 11, 3, c)
            self.f(8, True, WHITE)
            self.set_xy(x + 4, 246)
            self.cell(52, 7, "Выбрать →", align="C")

        # Плашка с условиями
        self.rr(14, 268, 182, 22, 4, BAR_BG)
        conditions = ["Предоплата 50% / остаток после сдачи", "Гарантия на 3 месяца", "Правки до результата"]
        for i, cond in enumerate(conditions):
            x = 20 + i * 62
            self.dot(x, 276, 2, ORANGE)
            self.f(8, False, DARK)
            self.set_xy(x + 4, 272); self.cell(56, 10, cond)

    # ─────────────────────────────────────────────────────────────────────────
    # СТРАНИЦА 5: ПРОЦЕСС
    # ─────────────────────────────────────────────────────────────────────────
    def p_process(self):
        self.page_bg()
        self.section_label(4, "Как мы работаем")

        self.f(21, True, DARK)
        self.set_xy(14, 28)
        self.multi_cell(182, 10, "5 шагов от заявки до готового продукта", "L")

        steps = [
            (ORANGE, "Разбор задачи",
             "Бесплатный созвон 20–30 минут. Разбираем вашу нишу, задачи и ожидания. "
             "Вы получаете конкретный план и цену."),
            (GREEN, "Бриф и проектирование",
             "Заполняете короткую анкету. Мы делаем структуру сайта/бота и согласовываем "
             "с вами до начала разработки."),
            (BLUE, "Дизайн и разработка",
             "Создаём дизайн, разрабатываем сайт или бота. Показываем промежуточные результаты — "
             "вы всегда в курсе."),
            (ORANGE, "Тестирование и правки",
             "Проверяем всё на реальных устройствах. Вносим правки — "
             "работаем до тех пор, пока вас всё не устроит."),
            (GREEN, "Сдача и поддержка",
             "Передаём все доступы, обучаем управлению. "
             "3 месяца бесплатной поддержки после сдачи."),
        ]

        for i, (c, title, desc) in enumerate(steps):
            y = 54 + i * 44
            self.white_card(14, y, 182, 38, r=4)
            self.rr(14, y, 3.5, 38, 4, c)

            # Номер в круге
            self.num_circle(32, y + 19, i + 1, c)

            self.f(10, True, DARK)
            self.set_xy(46, y + 8); self.cell(0, 7, title)
            self.f(8.5, False, DGRAY)
            self.set_xy(46, y + 17)
            self.multi_cell(144, 5, desc)

            # Стрелка между шагами
            if i < 4:
                self.set_draw_color(*CARD_SH)
                self.set_line_width(0.5)
                ax = 30
                ay1 = y + 38
                ay2 = y + 44
                self.line(ax, ay1, ax, ay2)
                self.line(ax - 2, ay2 - 2, ax, ay2)
                self.line(ax + 2, ay2 - 2, ax, ay2)

        # Нижний блок
        self.rr(14, 278, 182, 12, 4, ORANGE_L)
        self.f(9, True, ORANGE)
        self.set_xy(20, 281)
        self.cell(35, 5, "Важно:")
        self.f(9, False, DARK)
        self.set_xy(57, 281)
        self.cell(133, 5, "Средний срок запуска — 7 дней. Принимаем 1–2 проекта в неделю.")

    # ─────────────────────────────────────────────────────────────────────────
    # СТРАНИЦА 6: ГАРАНТИИ + CTA
    # ─────────────────────────────────────────────────────────────────────────
    def p_cta(self):
        self.page_bg()
        self.section_label(5, "Гарантии и следующий шаг")

        # Заголовок
        self.f(21, True, DARK)
        self.set_xy(14, 28)
        self.multi_cell(182, 10, "Работаем на результат — не на отчёты", "L")

        # Гарантии — 3 карточки
        guarantees = [
            (ORANGE, "Гарантия\nсроков",
             "Называем срок — соблюдаем. Каждый день просрочки — скидка 1%."),
            (GREEN,  "Правки до\nрезультата",
             "Вносим правки бесплатно до тех пор, пока вас всё устраивает."),
            (BLUE,   "3 месяца\nподдержки",
             "После сдачи — 3 месяца бесплатной технической поддержки."),
        ]
        for i, (c, title, desc) in enumerate(guarantees):
            x = 14 + i * 63
            self.white_card(x, 56, 59, 72, r=5)
            self.rr(x, 56, 59, 3, 5, c)
            self.dot(x + 29, 72, 10, ORANGE_L)
            self.f(16, True, c)
            self.set_xy(x, 66); self.cell(59, 11, "✓", align="C")
            self.f(8.5, True, DARK)
            self.set_xy(x + 4, 80)
            self.multi_cell(51, 4.5, title, align="C")
            self.f(7.5, False, DGRAY)
            self.set_xy(x + 4, 94)
            self.multi_cell(51, 4, desc, align="C")

        # Отзыв / цитата
        self.white_card(14, 140, 182, 36, r=5)
        self.rr(14, 140, 3.5, 36, 5, ORANGE)
        self.f(10, True, DARK)
        self.set_xy(22, 146)
        self.multi_cell(170, 6,
            "«Сайт окупился за первый месяц — пришло 14 новых клиентов.\n"
            "Рекомендую всем, кто хочет результат, а не просто красивую картинку.»")
        self.f(8, False, LGRAY)
        self.set_xy(22, 164)
        self.cell(0, 5, "— Владелец покрасочного цеха GK Pokraska")

        # CTA блок
        self.white_card(14, 188, 182, 60, r=6)
        self.rr(14, 188, 182, 3, 6, ORANGE)

        self.f(8, True, ORANGE)
        self.set_xy(14, 197); self.cell(182, 5, "СЛЕДУЮЩИЙ ШАГ", align="C")

        self.f(19, True, DARK)
        self.set_xy(14, 204); self.cell(182, 12, "Обсудим ваш проект?", align="C")

        self.f(9, False, DGRAY)
        self.set_xy(14, 217)
        self.multi_cell(182, 5.5,
            "Бесплатный созвон 20 минут. Расскажете задачу — назову цену и срок.",
            align="C")

        # Кнопка
        self.rr(67, 228, 76, 13, 3, ORANGE)
        self.f(10, True, WHITE)
        self.set_xy(67, 230); self.cell(76, 9, "Записаться →", align="C")

        # Три обещания под кнопкой
        promises = [(GREEN, "Бесплатно"), (ORANGE, "Без давления"), (BLUE, "Конкретный план")]
        for i, (c, t) in enumerate(promises):
            x = 28 + i * 56
            self.dot(x + 20, 246, 2.5, c)
            self.f(8.5, True, c)
            self.set_xy(x, 250); self.cell(44, 5, t, align="C")

        # Нижняя плашка
        self.rr(14, 262, 182, 28, 5, BAR_BG)
        self.f(8, False, LGRAY)
        self.set_xy(14, 272)
        self.cell(182, 6,
            "Telegram-боты  |  Лендинги  |  Многостраничные сайты  |  Под ключ",
            align="C")
        self.f(7, False, LGRAY)
        self.set_xy(14, 279)
        self.cell(182, 5, "Гарантия  |  Оплата 50/50  |  Запуск от 3 дней", align="C")


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
    pdf.add_page(); pdf.p_pain()
    pdf.add_page(); pdf.p_cases()
    pdf.add_page(); pdf.p_packages()
    pdf.add_page(); pdf.p_process()
    pdf.add_page(); pdf.p_cta()

    pdf.output(OUT)
    size = Path(OUT).stat().st_size
    print(f"PDF: {OUT}  ({size // 1024} KB)  6 страниц")


if __name__ == "__main__":
    make()
