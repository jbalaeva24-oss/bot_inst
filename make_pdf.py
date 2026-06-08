from fpdf import FPDF
from fpdf.enums import XPos, YPos

A   = "assets"
OUT = "assets/guide.pdf"

# Палитра
BG      = (8,    7,   18)
WHITE   = (255, 255, 255)
P       = (108,  92, 255)   # фиолетовый акцент
P2      = ( 79,  63, 210)
P3      = ( 22,  20,  55)   # тёмный фон-блок
P4      = ( 35,  32,  90)   # блок чуть светлее
G1      = (220, 215, 240)   # основной текст
G2      = (150, 142, 185)   # второстепенный
G3      = ( 60,  55, 100)   # разделители
GREEN   = ( 52, 211, 153)
AMBER   = (251, 191,  36)
BLUE    = ( 96, 165, 250)
ROSE    = (251, 113, 133)
TEAL    = ( 45, 212, 191)


class PDF(FPDF):

    def _r(self, bold=False, size=11, color=WHITE):
        self.set_font("R", "B" if bold else "", size)
        self.set_text_color(*color)

    def box(self, x, y, w, h, c):
        self.set_fill_color(*c); self.rect(x, y, w, h, "F")

    def hline(self, y, c=G3, lw=0.25):
        self.set_draw_color(*c); self.set_line_width(lw)
        self.line(0, y, 210, y)

    def dot(self, x, y, r, c):
        self.set_fill_color(*c); self.ellipse(x-r, y-r, r*2, r*2, "F")

    def tag(self, x, y, text, bg=P, tc=WHITE, ts=7.5):
        self._r(True, ts, tc)
        w = self.get_string_width(text) + 8
        self.box(x, y, w, 7, bg)
        self.set_xy(x, y+0.5); self.cell(w, 6, text, align="C")

    # ── ОБЛОЖКА ───────────────────────────────────────────────────────────────
    def cover(self):
        self.box(0, 0, 210, 297, BG)

        # Левая вертикальная полоса
        self.box(0, 0, 4, 297, P)

        # Фоновая геометрия
        self.box(120, 0, 90, 297, P3)
        self.box(120, 0, 2, 297, P)

        # Маленький тег
        self.tag(20, 28, "  БЕСПЛАТНЫЙ ГИД  ", P, WHITE, 8)

        # Главный заголовок
        self._r(True, 48, WHITE)
        self.set_xy(20, 46)
        self.multi_cell(98, 19, "Бот,\nлендинг\nили сайт?", align="L")

        # Подзаголовок
        self._r(False, 13, G2)
        self.set_xy(20, 136)
        self.multi_cell(98, 7,
            "Как выбрать правильный\nинструмент и не потратить\nденьги впустую", "L")

        # Три фишки справа
        chips = [
            (P,     "Сравнение инструментов"),
            (GREEN, "3 реальных кейса"),
            (AMBER, "Алгоритм выбора"),
        ]
        for i, (c, t) in enumerate(chips):
            y = 55 + i * 28
            self.dot(135, y+4, 3, c)
            self._r(True, 10, WHITE)
            self.set_xy(142, y); self.cell(60, 7, t)
            self._r(False, 8.5, G2)

        # Большая цифра
        self._r(True, 64, P3)
        self.set_xy(122, 160); self.cell(86, 45, "73%", align="C")
        self._r(True, 9, P)
        self.set_xy(122, 200); self.cell(86, 6,
            "бизнесов выбирают", align="C")
        self._r(False, 9, G2)
        self.set_xy(122, 208); self.cell(86, 6,
            "не тот инструмент", align="C")

        # Футер
        self.box(0, 276, 210, 21, P3)
        self.hline(276, P)
        self._r(False, 8, G2)
        self.set_xy(20, 283); self.cell(85, 5, "12 мин. чтения  •  Бесплатно")
        self.set_xy(105, 283); self.cell(85, 5,
            "Telegram-боты  Лендинги  Сайты", align="R")

    # ── СТРАНИЦА 2: ПРОБЛЕМА ──────────────────────────────────────────────────
    def page_problem(self):
        self.box(0, 0, 210, 297, BG)
        self.box(0, 0, 4, 297, P)

        # Секция-метка
        self._r(True, 8, P)
        self.set_xy(20, 18); self.cell(0, 6, "01  /  ПРОБЛЕМА")
        self.hline(27, G3)

        # Заголовок
        self._r(True, 30, WHITE)
        self.set_xy(20, 34)
        self.multi_cell(170, 13, "Почему большинство\nтратит деньги зря", "L")

        # Текст
        self._r(False, 10.5, G1)
        self.set_xy(20, 74)
        self.multi_cell(170, 6.5,
            "Каждый день ко мне приходят с одним и тем же запросом. "
            "Начинаем разговор — и выясняется, что решение было выбрано неверно. "
            "Сайт вместо лендинга. Лендинг вместо бота. "
            "Итог: деньги потрачены, результата нет, всё переделывается с нуля.", "L")

        # Три статистики
        stats = [
            (P,     "73%", "выбирают\nне тот инструмент"),
            (ROSE,  "2x",  "дороже обходится\nпеределка"),
            (AMBER, "3 мес", "теряют в среднем\nна ошибочный выбор"),
        ]
        y0 = 118
        for i, (c, num, label) in enumerate(stats):
            x = 20 + i * 63
            self.box(x, y0, 58, 48, P3)
            self.box(x, y0, 58, 3, c)
            self._r(True, 26, c)
            self.set_xy(x, y0+8); self.cell(58, 18, num, align="C")
            self._r(False, 8.5, G2)
            self.set_xy(x, y0+27); self.multi_cell(58, 5.5, label, align="C")

        # Цитата
        self.box(20, 180, 170, 26, P4)
        self.box(20, 180, 3, 26, P)
        self._r(True, 11, WHITE)
        self.set_xy(28, 184)
        self.multi_cell(157, 6.5,
            "«Правильный инструмент — это 50% успеха.\n"
            "Гайд ниже поможет выбрать его за 12 минут.»")

        # Список ошибок
        self._r(True, 10, WHITE)
        self.set_xy(20, 216); self.cell(0, 7, "Типичные ошибки:")
        errors = [
            "Сделали сайт — а нужен был лендинг под рекламу",
            "Заказали лендинг — а клиенты идут через Telegram",
            "Потратили 80 000 ₽ на сайт — а бот за 20 000 ₽ дал бы больше",
        ]
        for i, e in enumerate(errors):
            y = 226 + i * 13
            self.dot(24, y+3.5, 2.5, ROSE)
            self._r(False, 10, G1)
            self.set_xy(30, y); self.multi_cell(160, 6, e)

    # ── СТРАНИЦА 3: СРАВНЕНИЕ ─────────────────────────────────────────────────
    def page_compare(self):
        self.box(0, 0, 210, 297, BG)
        self.box(0, 0, 4, 297, P)

        self._r(True, 8, P)
        self.set_xy(20, 18); self.cell(0, 6, "02  /  СРАВНЕНИЕ")
        self.hline(27, G3)

        self._r(True, 30, WHITE)
        self.set_xy(20, 34)
        self.multi_cell(170, 13, "Три инструмента —\nтри разные задачи", "L")

        tools = [
            (P,    "Telegram-бот",         "от 15 000 ₽", "7-14 дней",
             ["Работает 24/7 без менеджера",
              "Push-уведомления: открыв. 70%",
              "Воронка, оплата, рассылки",
              "Повторный контакт бесплатно"]),
            (AMBER,"Лендинг",              "от 15 000 ₽", "5-10 дней",
             ["Максимум конверсии с рекламы",
              "Один оффер = фокус клиента",
              "A/B-тест гипотез за неделю",
              "Быстрый запуск и окупаемость"]),
            (BLUE, "Многостр. сайт",       "от 40 000 ₽", "2-4 нед.",
             ["SEO-трафик без рекламы",
              "Каталог услуг и портфолио",
              "Доверие и репутация бренда",
              "Актив на годы вперёд"]),
        ]

        for i, (c, name, price, term, pts) in enumerate(tools):
            x = 14 + i * 65
            y = 82
            h = 140
            self.box(x, y, 62, h, P3)
            self.box(x, y, 62, 4, c)

            # Название
            self._r(True, 11.5, c)
            self.set_xy(x+3, y+8); self.cell(56, 8, name)

            # Цена и срок
            self._r(False, 7.5, G2)
            self.set_xy(x+3, y+19); self.cell(28, 5, "СТОИМОСТЬ")
            self.set_xy(x+33, y+19); self.cell(26, 5, "СРОК", align="R")

            self._r(True, 12, WHITE)
            self.set_xy(x+3, y+25); self.cell(28, 8, price)
            self._r(True, 12, c)
            self.set_xy(x+33, y+25); self.cell(26, 8, term, align="R")

            # Разделитель
            self.hline(y+37, G3, 0.2)

            # Пункты
            self._r(False, 8.5, G1)
            for j, pt in enumerate(pts):
                yp = y + 42 + j * 14
                self.dot(x+6, yp+3, 2, c)
                self.set_xy(x+11, yp)
                self.multi_cell(50, 5.5, pt)

        # Подсказка
        self.box(14, 232, 182, 16, P4)
        self.box(14, 232, 3, 16, GREEN)
        self._r(True, 9.5, WHITE)
        self.set_xy(22, 235); self.cell(0, 6, "Связка лендинг + бот")
        self._r(False, 9.5, G1)
        self.set_xy(22, 241)
        self.cell(0, 6, "бьёт дорогой сайт по конверсии при меньшем бюджете")

    # ── СТРАНИЦА 4: КЕЙСЫ ────────────────────────────────────────────────────
    def page_cases(self):
        self.box(0, 0, 210, 297, BG)
        self.box(0, 0, 4, 297, P)

        self._r(True, 8, P)
        self.set_xy(20, 18); self.cell(0, 6, "03  /  КЕЙСЫ")
        self.hline(27, G3)

        self._r(True, 30, WHITE)
        self.set_xy(20, 34)
        self.multi_cell(170, 13, "Реальные результаты\nклиентов", "L")

        cases = [
            (P, "Telegram-бот",
             "Производство мебельных фасадов",
             "Менеджер обрабатывал заявки вручную.\nПолдня уходило на ответы в переписке.",
             [("Заявок в месяц",   "18 → 67",  GREEN),
              ("Время ответа",     "4ч → 2мин", GREEN),
              ("Конверсия",        "+40%",       GREEN)]),
            (AMBER, "Лендинг",
             "Юридические услуги",
             "Многостраничный сайт давал дорогой\nтрафик с низкой конверсией.",
             [("Стоимость лида",   "3200 → 890₽", GREEN),
              ("Конверсия сайта",  "1.2 → 4.8%",  GREEN),
              ("Окупился за",      "3 недели",     GREEN)]),
            (BLUE, "Сайт + Бот",
             "Строительная компания",
             "Не было сайта. Заявки только\nпо сарафанному радио.",
             [("Новых клиентов",   "+12/мес",   GREEN),
              ("Средний чек",      "+35%",       GREEN),
              ("ROI за год",       "1240%",      GREEN)]),
        ]

        for i, (c, tool, niche, problem, results) in enumerate(cases):
            y = 84 + i * 66
            self.box(14, y, 182, 60, P3)
            self.box(14, y, 3, 60, c)

            # Тег инструмента
            self.tag(20, y+5, f"  {tool}  ", c, WHITE, 8)

            # Ниша
            self._r(True, 11, WHITE)
            self.set_xy(20, y+16); self.cell(95, 7, niche)

            # Проблема
            self._r(False, 8.5, G2)
            self.set_xy(20, y+25)
            self.multi_cell(85, 5.5, problem)

            # Результаты
            for j, (label, val, vc) in enumerate(results):
                x = 115 + j * 27
                self._r(False, 7, G2)
                self.set_xy(x, y+8); self.cell(25, 5, label, align="C")
                self._r(True, 11, vc)
                self.set_xy(x, y+14); self.cell(25, 8, val, align="C")

    # ── СТРАНИЦА 5: АЛГОРИТМ ─────────────────────────────────────────────────
    def page_algo(self):
        self.box(0, 0, 210, 297, BG)
        self.box(0, 0, 4, 297, P)

        self._r(True, 8, P)
        self.set_xy(20, 18); self.cell(0, 6, "04  /  АЛГОРИТМ ВЫБОРА")
        self.hline(27, G3)

        self._r(True, 30, WHITE)
        self.set_xy(20, 34)
        self.multi_cell(170, 13, "5 вопросов — и ответ\nстанет очевидным", "L")

        qa = [
            (P,    "1",
             "Откуда придут клиенты?",
             "Реклама (таргет/контекст)",  "→ Лендинг",     AMBER,
             "Telegram / соцсети",         "→ Бот",          P),
            (AMBER, "2",
             "Нужна автоматизация общения?",
             "Да, хочу без менеджера",     "→ Бот",          P,
             "Нет, просто принять заявку", "→ Лендинг",      AMBER),
            (BLUE,  "3",
             "Один оффер или несколько услуг?",
             "Один продукт / услуга",      "→ Лендинг",      AMBER,
             "Каталог / много направлений","→ Сайт",          BLUE),
            (GREEN, "4",
             "Важен повторный контакт без рекламы?",
             "Да, хочу писать базе",       "→ Бот (рассылки)",P,
             "Нет, ретаргетинг устроит",   "→ Лендинг",      AMBER),
            (TEAL,  "5",
             "Бюджет и срок запуска?",
             "До 30к, нужно быстро",       "→ Бот или лендинг",P,
             "Есть бюджет на долгосрок",   "→ Сайт",          BLUE),
        ]

        for i, (c, num, q, a1, r1, rc1, a2, r2, rc2) in enumerate(qa):
            y = 83 + i * 40
            self.box(14, y, 182, 35, P3)
            self.box(14, y, 3, 35, c)

            # Номер + вопрос
            self._r(True, 18, P4)
            self.set_xy(16, y+5); self.cell(14, 14, num, align="C")
            self._r(True, 10.5, WHITE)
            self.set_xy(32, y+8); self.cell(145, 7, q)

            # Два варианта
            self.dot(32, y+23, 2, GREEN)
            self._r(False, 9, G1)
            self.set_xy(37, y+19); self.cell(60, 6, a1)
            self._r(True, 9, rc1)
            self.set_xy(100, y+19); self.cell(45, 6, r1)

            self.dot(32, y+30, 2, ROSE)
            self._r(False, 9, G1)
            self.set_xy(37, y+26); self.cell(60, 6, a2)
            self._r(True, 9, rc2)
            self.set_xy(100, y+26); self.cell(45, 6, r2)

    # ── CTA ───────────────────────────────────────────────────────────────────
    def page_cta(self):
        self.box(0, 0, 210, 297, BG)
        self.box(0, 0, 4, 297, P)

        # Большой акцентный блок сверху
        self.box(4, 0, 206, 135, P3)
        self.box(4, 0, 206, 4, P)

        self._r(True, 8, P)
        self.set_xy(20, 18); self.cell(0, 6, "05  /  СЛЕДУЮЩИЙ ШАГ")

        self._r(True, 36, WHITE)
        self.set_xy(20, 34)
        self.multi_cell(170, 15, "Готов обсудить\nтвой проект?", "C")

        self._r(False, 12, G2)
        self.set_xy(20, 90)
        self.multi_cell(170, 7,
            "Бесплатный 20-минутный разбор.\n"
            "Покажу примеры, назову цену и срок.", "C")

        # Кнопка
        self.box(60, 124, 90, 16, P)
        self._r(True, 12, WHITE)
        self.set_xy(60, 125); self.cell(90, 14, "Записаться ->", align="C")

        # Три обещания
        promises = [(GREEN, "Бесплатно"), (AMBER, "Без давления"), (BLUE, "Конкретный план")]
        for i, (c, t) in enumerate(promises):
            x = 22 + i * 58
            self.dot(x+24, 156, 3, c)
            self._r(True, 9, c)
            self.set_xy(x, 162); self.cell(48, 6, t, align="C")

        # Три цифры
        proof = [("150+", "проектов", P), ("7+", "лет опыта", GREEN), ("24ч", "ответ", AMBER)]
        for i, (n, l, c) in enumerate(proof):
            x = 22 + i * 58
            self.box(x, 178, 48, 36, P4)
            self.box(x, 178, 48, 3, c)
            self._r(True, 22, c)
            self.set_xy(x, 183); self.cell(48, 14, n, align="C")
            self._r(False, 8.5, G2)
            self.set_xy(x, 198); self.cell(48, 6, l, align="C")

        # Финальный текст
        self._r(False, 10, G2)
        self.set_xy(20, 228)
        self.multi_cell(170, 6.5,
            "Работаю с малым и средним бизнесом.\n"
            "Telegram-боты, лендинги, сайты — под ключ.\n"
            "От идеи до запуска.", "C")

        # Футер
        self.box(0, 270, 210, 27, P3)
        self.hline(270, P)
        self._r(False, 8, G2)
        self.set_xy(0, 279)
        self.cell(210, 6,
            "Telegram-боты  |  Лендинги  |  Сайты  |  Разработка под ключ",
            align="C")


def make():
    pdf = PDF("P", "mm", "A4")
    pdf.add_font("R", "",  fname=f"{A}/Inter-Regular.ttf")
    pdf.add_font("R", "B", fname=f"{A}/Inter-Bold.ttf")
    pdf.set_margins(0, 0, 0)
    pdf.set_auto_page_break(False)

    pdf.add_page(); pdf.cover()
    pdf.add_page(); pdf.page_problem()
    pdf.add_page(); pdf.page_compare()
    pdf.add_page(); pdf.page_cases()
    pdf.add_page(); pdf.page_algo()
    pdf.add_page(); pdf.page_cta()

    pdf.output(OUT)
    size = __import__("os").path.getsize(OUT)
    print(f"PDF готов: {OUT}  ({size//1024} KB)  6 страниц")

if __name__ == "__main__":
    make()
