"""
Лид-магнит PDF — Premium Edition
"""
import os
from pathlib import Path
from fpdf import FPDF
from fpdf.enums import XPos, YPos

BASE = Path(__file__).parent
A   = str(BASE / "assets")
OUT = str(BASE / "assets" / "guide.pdf")

os.makedirs(A, exist_ok=True)

# -- Палитра ------------------------------------------------------------------─
BG    = (7,    6,   16)
W     = (255, 255, 255)
P     = (110,  93, 255)   # фиолетовый
PD    = ( 22,  20,  55)   # тёмный фон
PD2   = ( 38,  34,  90)   # блок
PD3   = ( 55,  50, 130)   # акцент
G1    = (225, 220, 245)   # основной текст
G2    = (148, 140, 182)   # второстепенный
G3    = ( 50,  46,  90)   # разделители
GR    = ( 52, 211, 153)   # зелёный
AM    = (251, 191,  36)   # янтарный
BL    = ( 96, 165, 250)   # синий
RS    = (251, 113, 133)   # розовый
CY    = ( 34, 211, 238)   # циан


class PDF(FPDF):

    def f(self, sz=11, b=False, c=W):
        self.set_font("R", "B" if b else "", sz)
        self.set_text_color(*c)

    def box(self, x, y, w, h, c):
        self.set_fill_color(*c)
        self.rect(x, y, w, h, "F")

    def hl(self, y, c=G3, lw=0.2):
        self.set_draw_color(*c)
        self.set_line_width(lw)
        self.line(0, y, 210, y)

    def vl(self, x, y1, y2, c=G3, lw=0.2):
        self.set_draw_color(*c)
        self.set_line_width(lw)
        self.line(x, y1, x, y2)

    def dot(self, x, y, r, c):
        self.set_fill_color(*c)
        self.ellipse(x-r, y-r, r*2, r*2, "F")

    def badge(self, x, y, text, bg=P, tc=W, sz=7.5):
        self.f(sz, True, tc)
        w = self.get_string_width(text) + 10
        self.box(x, y, w, 7.5, bg)
        self.set_xy(x, y+0.8)
        self.cell(w, 6, text, align="C")
        return w

    def label(self, x, y, text, c=P):
        self.f(7.5, True, c)
        self.set_xy(x, y)
        self.cell(0, 5, text)

    def section_mark(self, num, title):
        self.f(7, True, P)
        self.set_xy(20, 16)
        self.cell(0, 5, f"{num:02d}  --  {title.upper()}")
        self.hl(24, G3)

    # ------------------------------------------------------------------------─
    # ОБЛОЖКА
    # ------------------------------------------------------------------------─
    def cover(self):
        self.box(0, 0, 210, 297, BG)

        # Левая акцентная полоса с градиентом
        for i in range(6):
            alpha = int(255 * (1 - i/6))
            self.box(i, 0, 1, 297, (
                int(P[0] * alpha/255),
                int(P[1] * alpha/255),
                int(P[2] * alpha/255),
            ))

        # Правый декоративный блок
        self.box(138, 0, 72, 297, PD)
        self.box(138, 0, 1, 297, PD3)

        # Верхняя горизонтальная полоса
        self.box(0, 0, 210, 3, P)

        # -- Левая часть --
        self.badge(20, 30, "  БЕСПЛАТНЫЙ ГИД  ", P, W, 8)

        self.f(52, True, W)
        self.set_xy(20, 48)
        self.multi_cell(115, 20, "Бот,\nлендинг\nили сайт?", align="L")

        # Акцентная линия под заголовком
        self.box(20, 138, 60, 2, P)

        self.f(12, False, G2)
        self.set_xy(20, 145)
        self.multi_cell(115, 7,
            "Как выбрать правильный инструмент\n"
            "и не потратить деньги впустую", align="L")

        # Три пункта
        items = [
            (GR, "Сравнение 3 инструментов"),
            (AM, "3 реальных кейса с цифрами"),
            (BL, "Алгоритм выбора за 5 шагов"),
        ]
        for i, (c, t) in enumerate(items):
            y = 172 + i*14
            self.dot(22, y+4, 3.5, c)
            self.f(10, True, W)
            self.set_xy(30, y+0.5)
            self.cell(100, 7, t)

        # -- Правая часть --
        # Большая цифра
        self.f(76, True, PD2)
        self.set_xy(136, 55)
        self.cell(72, 55, "73", align="C")

        self.f(28, True, P)
        self.set_xy(136, 108)
        self.cell(72, 20, "%", align="C")

        self.f(8.5, False, G2)
        self.set_xy(136, 128)
        self.multi_cell(72, 5.5, "бизнесов выбирают\nне тот инструмент", align="C")

        # Три мини-факта
        facts = [(GR, "60-80%", "открываемость\nTelegram push"),
                 (RS, "3x",    "дешевле лид\nс лендинга vs сайт"),
                 (AM, "7 дней","средний срок\nзапуска бота")]
        for i, (c, n, l) in enumerate(facts):
            y = 168 + i*34
            self.box(142, y, 60, 30, PD2)
            self.box(142, y, 60, 2, c)
            self.f(18, True, c)
            self.set_xy(142, y+4)
            self.cell(60, 12, n, align="C")
            self.f(7.5, False, G2)
            self.set_xy(142, y+17)
            self.multi_cell(60, 4.5, l, align="C")

        # Футер
        self.box(0, 278, 210, 19, PD)
        self.hl(278, PD3)
        self.f(8, False, G2)
        self.set_xy(20, 285)
        self.cell(85, 5, "6 страниц  •  12 минут  •  Бесплатно")
        self.set_xy(105, 285)
        self.cell(85, 5, "Telegram-боты  Лендинги  Сайты", align="R")

    # ------------------------------------------------------------------------─
    # СТРАНИЦА 2: ПРОБЛЕМА
    # ------------------------------------------------------------------------─
    def p_problem(self):
        self.box(0, 0, 210, 297, BG)
        self.box(0, 0, 3, 297, P)
        self.box(0, 0, 210, 3, P)
        self.section_mark(1, "Почему это важно")

        self.f(32, True, W)
        self.set_xy(20, 32)
        self.multi_cell(170, 14, "Почему большинство\nтратит деньги зря", "L")

        self.f(10.5, False, G1)
        self.set_xy(20, 72)
        self.multi_cell(170, 6.5,
            "Каждый день ко мне приходят предприниматели с похожей историей. "
            "Потратили 80 000 ₽ на сайт — заявок нет. "
            "Сделали лендинг — а клиенты сидят в Telegram. "
            "Заказали бот — а нужен был нормальный сайт с SEO.\n\n"
            "Причина одна: инструмент выбирается по совету знакомых "
            "или по красивому портфолио подрядчика, а не по реальной задаче.", "L")

        # Три большие статистики
        stats = [
            (P,  "73%", "выбирают\nне тот инструмент"),
            (RS, "2.4x","дороже обходится\nпеределка"),
            (AM, "87 дн","теряют в среднем\nна ошибочный путь"),
        ]
        for i, (c, n, l) in enumerate(stats):
            x = 20 + i*63
            self.box(x, 132, 58, 52, PD)
            self.box(x, 132, 58, 3, c)
            self.box(x, 179, 58, 5, PD2)
            self.f(28, True, c)
            self.set_xy(x, 137)
            self.cell(58, 20, n, align="C")
            self.f(8, False, G2)
            self.set_xy(x, 159)
            self.multi_cell(58, 5, l, align="C")

        # Цитата-блок
        self.box(20, 196, 170, 32, PD2)
        self.box(20, 196, 4, 32, P)
        self.f(12, True, W)
        self.set_xy(30, 202)
        self.multi_cell(155, 7,
            "«Правильный инструмент — это половина успеха.\n"
            "Этот гайд поможет выбрать его за 12 минут.»")

        # Ошибки
        self.f(10, True, W)
        self.set_xy(20, 238); self.cell(0, 7, "Типичные ошибки:")
        errs = [
            "Сделали многостраничный сайт — а нужен был лендинг под рекламу",
            "Заказали лендинг — а 80% клиентов приходят через Telegram",
            "Потратили 100 000 ₽ на сайт — а бот за 25 000 ₽ дал бы больше",
        ]
        for i, e in enumerate(errs):
            y = 249 + i*13
            self.dot(24, y+3.5, 2.5, RS)
            self.f(9.5, False, G1)
            self.set_xy(30, y)
            self.multi_cell(158, 6, e)

    # ------------------------------------------------------------------------─
    # СТРАНИЦА 3: СРАВНЕНИЕ
    # ------------------------------------------------------------------------─
    def p_compare(self):
        self.box(0, 0, 210, 297, BG)
        self.box(0, 0, 3, 297, P)
        self.box(0, 0, 210, 3, P)
        self.section_mark(2, "Сравнение инструментов")

        self.f(32, True, W)
        self.set_xy(20, 32)
        self.multi_cell(170, 14, "Три инструмента —\nтри разные задачи", "L")

        tools = [
            (P,  "Telegram-бот",   "от 15 000 ₽", "7-14 дней",
             "Автоматизация и\nповторный контакт",
             ["Работает 24/7 без менеджера",
              "Push открывают 60-80%",
              "Воронка, оплата, рассылки",
              "Повторный контакт — бесплатно",
              "Запуск от 7 дней"]),
            (AM, "Лендинг",        "от 15 000 ₽", "5-10 дней",
             "Конверсия\nрекламного трафика",
             ["Максимум конверсии с рекламы",
              "Один оффер = фокус",
              "A/B-тест за неделю",
              "Быстрый запуск и окупаемость",
              "Легко масштабировать"]),
            (BL, "Сайт",           "от 40 000 ₽", "2-4 нед.",
             "SEO и долгосрочный\nактив бизнеса",
             ["SEO-трафик без рекламы",
              "Каталог и портфолио",
              "Доверие и репутация",
              "Работает годами",
              "Разные страницы под сегменты"]),
        ]

        for i, (c, name, price, term, desc, pts) in enumerate(tools):
            x = 14 + i*65
            y = 82
            # Карточка
            self.box(x, y, 62, 172, PD)
            self.box(x, y, 62, 4, c)

            # Название
            self.f(12, True, c)
            self.set_xy(x+4, y+9)
            self.cell(54, 8, name)

            # Описание
            self.f(8, False, G2)
            self.set_xy(x+4, y+19)
            self.multi_cell(54, 5, desc)

            # Цена и срок
            self.hl(y+34, G3, 0.15)
            self.f(7, False, G2)
            self.set_xy(x+4, y+37); self.cell(26, 5, "СТОИМОСТЬ")
            self.set_xy(x+32, y+37); self.cell(26, 5, "СРОК", align="R")
            self.f(11, True, W)
            self.set_xy(x+4, y+43); self.cell(26, 8, price)
            self.f(11, True, c)
            self.set_xy(x+32, y+43); self.cell(26, 8, term, align="R")

            # Пункты
            self.hl(y+55, G3, 0.15)
            self.f(8.5, False, G1)
            for j, pt in enumerate(pts):
                yp = y+60+j*20
                self.dot(x+7, yp+4, 2.2, c)
                self.set_xy(x+12, yp)
                self.multi_cell(48, 5.5, pt)

        # Подсказка
        self.box(14, 262, 182, 18, PD2)
        self.box(14, 262, 4, 18, GR)
        self.f(9, True, W)
        self.set_xy(24, 266); self.cell(80, 6, "Лайфхак:")
        self.f(9, False, G1)
        self.set_xy(24, 272)
        self.cell(164, 6, "Лендинг + Telegram-бот бьют дорогой сайт по конверсии при меньшем бюджете")

    # ------------------------------------------------------------------------─
    # СТРАНИЦА 4: КЕЙСЫ
    # ------------------------------------------------------------------------─
    def p_cases(self):
        self.box(0, 0, 210, 297, BG)
        self.box(0, 0, 3, 297, P)
        self.box(0, 0, 210, 3, P)
        self.section_mark(3, "Реальные кейсы")

        self.f(32, True, W)
        self.set_xy(20, 32)
        self.multi_cell(170, 14, "Результаты клиентов\nв цифрах", "L")

        cases = [
            (P, "Telegram-бот", "Производство мебельных фасадов",
             "Менеджер вручную обрабатывал заявки. "
             "Полдня уходило на переписку и отправку прайса.",
             [("Заявок/мес", "18 → 67",   GR, "+272%"),
              ("Время ответа","4ч → 2мин", GR, "-97%"),
              ("Конверсия",  "2.1 → 8.4%",GR, "+300%")]),
            (AM, "Лендинг", "Юридические услуги онлайн",
             "Старый сайт давал дорогой трафик с конверсией 1.2%. "
             "Лид обходился в 3200 ₽.",
             [("Стоимость лида","3200→890₽", GR, "-72%"),
              ("Конверсия",    "1.2→4.8%",   GR, "+300%"),
              ("Окупился за",  "18 дней",    GR, "ROI 840%")]),
            (BL, "Сайт + Бот", "Строительная компания",
             "Работали только по сарафану. "
             "Не было онлайн-присутствия совсем.",
             [("Новых клиентов","+14/мес",   GR, "с нуля"),
              ("Средний чек",   "+42%",       GR, "доверие"),
              ("ROI за год",    "1840%",      GR, "окупился")]),
        ]

        for i, (c, tool, niche, problem, results) in enumerate(cases):
            y = 84 + i*66
            self.box(14, y, 182, 60, PD)
            self.box(14, y, 4, 60, c)

            # Тег и ниша
            self.badge(22, y+6, f"  {tool}  ", c, W, 8)
            self.f(11, True, W)
            self.set_xy(22, y+18); self.cell(90, 7, niche)

            # Проблема
            self.f(8.5, False, G2)
            self.set_xy(22, y+27)
            self.multi_cell(85, 5, problem)

            # Вертикальный разделитель
            self.vl(115, y+4, y+56, G3)

            # Результаты
            for j, (label, val, vc, extra) in enumerate(results):
                x = 120 + j*26
                self.f(7, False, G2)
                self.set_xy(x, y+7); self.cell(24, 5, label, align="C")
                self.f(10, True, vc)
                self.set_xy(x, y+13); self.cell(24, 8, val, align="C")
                self.f(7.5, True, c)
                self.set_xy(x, y+22); self.cell(24, 5, extra, align="C")

    # ------------------------------------------------------------------------─
    # СТРАНИЦА 5: АЛГОРИТМ
    # ------------------------------------------------------------------------─
    def p_algo(self):
        self.box(0, 0, 210, 297, BG)
        self.box(0, 0, 3, 297, P)
        self.box(0, 0, 210, 3, P)
        self.section_mark(4, "Алгоритм выбора")

        self.f(32, True, W)
        self.set_xy(20, 32)
        self.multi_cell(170, 14, "5 вопросов — и ответ\nстанет очевидным", "L")

        qs = [
            (P,  "Откуда клиенты?",
             "Таргет / контекст → ",   AM,  "Лендинг",
             "Telegram / органика → ", P,   "Бот"),
            (AM, "Нужна автоматизация?",
             "Да, без менеджера → ",   P,   "Бот",
             "Нет, просто заявка → ",  AM,  "Лендинг"),
            (BL, "Один оффер или каталог?",
             "Один продукт / услуга →",AM,  "Лендинг",
             "Много услуг / товаров →",BL,  "Сайт"),
            (GR, "Повторный контакт без рекламы?",
             "Да, нужны рассылки → ",  P,   "Бот",
             "Нет, ретаргет → ",       AM,  "Лендинг"),
            (CY, "Бюджет и срок?",
             "До 30к / быстро → ",     P,   "Бот или лендинг",
             "Есть ресурс → ",         BL,  "Сайт"),
        ]

        for i, (c, q, a1, c1, r1, a2, c2, r2) in enumerate(qs):
            y = 85 + i*40
            self.box(14, y, 182, 35, PD)
            self.box(14, y, 4, 35, c)

            # Номер
            self.f(22, True, PD2)
            self.set_xy(16, y+4); self.cell(14, 16, str(i+1), align="C")

            # Вопрос
            self.f(11, True, W)
            self.set_xy(34, y+8); self.cell(150, 8, q)

            # Ответы
            self.dot(34, y+24, 2.5, GR)
            self.f(9, False, G1)
            self.set_xy(40, y+20); self.cell(55, 7, a1)
            self.f(9, True, c1)
            self.set_xy(97, y+20); self.cell(40, 7, r1)

            self.dot(34, y+31, 2.5, RS)
            self.f(9, False, G1)
            self.set_xy(40, y+27); self.cell(55, 7, a2)
            self.f(9, True, c2)
            self.set_xy(97, y+27); self.cell(40, 7, r2)

    # ------------------------------------------------------------------------─
    # СТРАНИЦА 6: CTA
    # ------------------------------------------------------------------------─
    def p_cta(self):
        self.box(0, 0, 210, 297, BG)
        self.box(0, 0, 3, 297, P)
        self.box(0, 0, 210, 3, P)

        # Верхний акцентный блок
        self.box(3, 3, 207, 120, PD)
        self.box(3, 3, 207, 4, P)

        self.f(7, True, P)
        self.set_xy(20, 18); self.cell(0, 5, "СЛЕДУЮЩИЙ ШАГ")

        self.f(36, True, W)
        self.set_xy(20, 30)
        self.multi_cell(170, 15, "Обсудим твой\nпроект?", "C")

        self.f(12, False, G2)
        self.set_xy(20, 82)
        self.multi_cell(170, 7,
            "Бесплатный 20-минутный разбор.\n"
            "Покажу примеры — назову цену и срок.", "C")

        # Кнопка
        self.box(58, 110, 94, 15, P)
        self.f(11.5, True, W)
        self.set_xy(58, 111); self.cell(94, 13, "Записаться ->", align="C")

        # Три обещания
        promises = [(GR, "Бесплатно"), (AM, "Без давления"), (BL, "Конкретный план")]
        for i, (c, t) in enumerate(promises):
            x = 20 + i*60
            self.dot(x+24, 143, 3.5, c)
            self.f(9, True, c)
            self.set_xy(x, 150); self.cell(48, 6, t, align="C")

        # Четыре цифры доверия
        proof = [
            (P,  "150+",  "проектов"),
            (GR, "7+",    "лет опыта"),
            (AM, "24ч",   "ответ"),
            (BL, "100%",  "гарантия"),
        ]
        for i, (c, n, l) in enumerate(proof):
            x = 14 + i*49
            self.box(x, 164, 45, 40, PD)
            self.box(x, 164, 45, 3, c)
            self.f(22, True, c)
            self.set_xy(x, 169); self.cell(45, 14, n, align="C")
            self.f(8, False, G2)
            self.set_xy(x, 185); self.cell(45, 6, l, align="C")

        # Что умею
        self.f(10, True, W)
        self.set_xy(20, 216); self.cell(0, 7, "Что делаю:")
        skills = [
            (P,  "Telegram-боты под ключ — воронки, рассылки, оплата"),
            (AM, "Лендинги с высокой конверсией — от 5 дней"),
            (BL, "Многостраничные сайты — SEO, каталог, портфолио"),
        ]
        for i, (c, t) in enumerate(skills):
            y = 228 + i*13
            self.dot(24, y+3.5, 3, c)
            self.f(10, False, G1)
            self.set_xy(31, y); self.cell(158, 7, t)

        # Футер
        self.box(0, 272, 210, 25, PD)
        self.hl(272, P)
        self.f(8, False, G2)
        self.set_xy(0, 281)
        self.cell(210, 6,
            "Telegram-боты  |  Лендинги  |  Сайты  |  Разработка под ключ",
            align="C")


# ----------------------------------------------------------------------------─

def make():
    font_r = str(BASE / "assets" / "Inter-Regular.ttf")
    font_b = str(BASE / "assets" / "Inter-Bold.ttf")

    # Фоллбэк если Inter не найден
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
    print(f"PDF: {OUT}  ({size//1024}KB)  6 страниц")


if __name__ == "__main__":
    make()
