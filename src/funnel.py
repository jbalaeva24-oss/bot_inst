"""
Полная воронка продаж:
  Блок 1 — намерение
  Блок 2 — демо (сайты / бот)
  Блок 3 — квалификация (заявки / бюджет / срок)
  Блок 4 — КП под бюджет
  Блок 5 — возражения
"""
import logging
from pathlib import Path
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
import tempfile, os

import config
from src.states import F as Funnel
from src.keyboards import kb, url_kb, remove_keyboard
from src.booking import start_booking
from src.db import save_lead, upsert_user, schedule_followups, cancel_followup, \
    get_stats, get_all_user_ids, export_leads_xlsx
from src.crm import push_to_crm

log = logging.getLogger(__name__)
router = Router()


# ── хелперы ───────────────────────────────────────────────────────────────────

async def edit_or_answer(cb: CallbackQuery, text: str, reply_markup=None, parse_mode="HTML"):
    try:
        await cb.message.edit_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
    except Exception:
        await cb.message.answer(text, reply_markup=reply_markup, parse_mode=parse_mode)


_cached_file_id: str = ""

async def send_lead_magnet(message: Message):
    global _cached_file_id
    caption = config.LEAD_MAGNET_CAPTION
    try:
        # Если есть сохранённый file_id — используем его (быстро)
        if _cached_file_id:
            await message.answer_document(_cached_file_id, caption=caption)
            return
        if config.LEAD_MAGNET_FILE_ID:
            await message.answer_document(config.LEAD_MAGNET_FILE_ID, caption=caption)
            return
        path = Path(config.LEAD_MAGNET_PATH)
        if path.exists():
            msg = await message.answer_document(FSInputFile(str(path)), caption=caption)
            # Кешируем file_id для следующих отправок
            if msg.document:
                _cached_file_id = msg.document.file_id
                log.info("PDF file_id закеширован: %s", _cached_file_id)
        else:
            log.warning("PDF не найден: %s", path)
    except Exception as e:
        log.error("send_lead_magnet: %s", e)


async def notify_admins(bot, lead: dict):
    if not config.ADMIN_IDS:
        return
    lines = ["🔔 <b>Новый лид</b>"]
    for k, v in lead.items():
        if v:
            lines.append(f"• {k}: <i>{v}</i>")
    text = "\n".join(lines)
    for aid in config.ADMIN_IDS:
        try:
            await bot.send_message(aid, text, parse_mode="HTML")
        except Exception:
            pass


# ── БЛОК 1: ВХОД ──────────────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = message.from_user
    await upsert_user(user.id, user.username, user.full_name)
    await cancel_followup(user.id)
    await schedule_followups(user.id)

    await message.answer(
        "Привет! 👋\n\n"
        "Я делаю Telegram-боты, лендинги и сайты под ключ.\n"
        "Помогаю бизнесу получать больше клиентов.\n\n"
        "Что вас интересует?",
        reply_markup=kb(
            ("💰 Сколько стоит?", "intent:price"),
            ("📞 Давайте созвонимся", "intent:call"),
            ("⏰ Пока изучаю варианты", "intent:explore"),
        )
    )
    await state.set_state(Funnel.intent)


# ── БЛОК 2: ДЕМО ──────────────────────────────────────────────────────────────

@router.callback_query(Funnel.intent, F.data == "intent:price")
async def intent_price(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.update_data(intent="price")
    await edit_or_answer(cb,
        "Отлично! Что вам нужно сделать?\n\n"
        "Покажу живые примеры и назову точную цену 👇",
        reply_markup=kb(
            ("🌐 Сайт или лендинг", "demo:sites"),
            ("🤖 Telegram-бот", "demo:bot"),
            ("📦 Сайт + бот вместе", "demo:both"),
        )
    )


@router.callback_query(Funnel.intent, F.data == "intent:call")
async def intent_call(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.update_data(intent="call")
    await edit_or_answer(cb,
        "Отлично! Прежде чем созвониться — "
        "покажу пару примеров работ, чтобы разговор был предметным.\n\n"
        "Что делаем?",
        reply_markup=kb(
            ("🌐 Интересует сайт", "demo:sites"),
            ("🤖 Интересует бот", "demo:bot"),
            ("📦 Сайт + бот", "demo:both"),
        )
    )


@router.callback_query(Funnel.intent, F.data == "intent:explore")
async def intent_explore(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.update_data(intent="explore")
    await edit_or_answer(cb,
        "Понимаю, изучаете варианты 🤝\n\n"
        "Чтобы не тратить ваше время — покажу конкретные примеры "
        "с результатами. Займёт 2 минуты.\n\n"
        "Что ближе к вашей задаче?",
        reply_markup=kb(
            ("🌐 Сайт или лендинг", "demo:sites"),
            ("🤖 Telegram-бот", "demo:bot"),
            ("📦 Сайт + бот", "demo:both"),
        )
    )


@router.callback_query(F.data == "demo:sites")
async def demo_sites(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.update_data(product="site")
    s = config.DEMO_SITES
    await edit_or_answer(cb,
        "🎉 Отлично! Вот 3 сайта из моего портфолио:\n\n"
        f"1️⃣ <a href='{s[0][1]}'>{s[0][0]}</a>\n"
        f"   → {s[0][2]}\n\n"
        f"2️⃣ <a href='{s[1][1]}'>{s[1][0]}</a>\n"
        f"   → {s[1][2]}\n\n"
        f"3️⃣ <a href='{s[2][1]}'>{s[2][0]}</a>\n"
        f"   → {s[2][2]}\n\n"
        "Какой больше всего понравился по структуре?",
        reply_markup=kb(
            ("🎯 Первый понравился", "site_pick:1"),
            ("💼 Второй понравился", "site_pick:2"),
            ("⭐ Третий понравился", "site_pick:3"),
            ("📋 Перейти к вопросам", "site_pick:skip"),
        )
    )
    await state.set_state(Funnel.demo_site_reaction)


@router.callback_query(Funnel.demo_site_reaction, F.data.startswith("site_pick:"))
async def site_pick(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    pick = cb.data.split(":")[1]
    labels = {"1": "первый", "2": "второй", "3": "третий", "skip": ""}
    reaction = f"Отличный вкус — {labels[pick]} тоже мой фаворит! " if pick != "skip" else ""
    await state.update_data(demo_pick=pick)
    await edit_or_answer(cb,
        f"{reaction}Теперь пару вопросов — чтобы подготовить точное предложение:\n\n"
        "Сколько заявок получаете в месяц сейчас?",
        reply_markup=kb(
            ("📉 Меньше 10", "leads:low"),
            ("📊 10–30", "leads:mid"),
            ("📈 30–100", "leads:high"),
            ("🚀 Больше 100", "leads:top"),
            ("🆕 Только начинаю", "leads:zero"),
        )
    )
    await state.set_state(Funnel.q_leads)


@router.callback_query(F.data == "demo:bot")
async def demo_bot(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.update_data(product="bot")
    await edit_or_answer(cb,
        "🤖 Демо-бот уже готов — попробуйте прямо сейчас!\n\n"
        f"👉 {config.DEMO_BOT_LINK}\n\n"
        "Этот бот умеет:\n"
        "✅ Собирать заявки и квалифицировать клиентов\n"
        "✅ Отправлять прайс и портфолио\n"
        "✅ Записывать на созвон\n"
        "✅ Напоминать о себе\n\n"
        "Потестируйте 2–3 минуты и возвращайтесь 👇",
        reply_markup=kb(
            ("✅ Да, впечатляет!", "bot_demo:wow"),
            ("🤔 Неплохо, но есть вопросы", "bot_demo:questions"),
            ("💰 Сколько стоит такой?", "bot_demo:price"),
            ("🔧 Хочу другой функционал", "bot_demo:custom"),
        )
    )
    await state.set_state(Funnel.demo_bot_reaction)


@router.callback_query(F.data == "demo:both")
async def demo_both(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.update_data(product="both")
    await edit_or_answer(cb,
        "💡 Связка сайт + бот — это мощно!\n\n"
        "Сайт привлекает трафик → бот автоматически обрабатывает заявки.\n"
        "Такая связка обычно увеличивает конверсию в 2–3 раза.\n\n"
        "Чтобы подобрать оптимальный вариант — пара вопросов.\n\n"
        "Сколько заявок получаете сейчас?",
        reply_markup=kb(
            ("📉 Меньше 10", "leads:low"),
            ("📊 10–30", "leads:mid"),
            ("📈 30–100", "leads:high"),
            ("🚀 Больше 100", "leads:top"),
            ("🆕 Только начинаю", "leads:zero"),
        )
    )
    await state.set_state(Funnel.q_leads)


@router.callback_query(Funnel.demo_bot_reaction, F.data.startswith("bot_demo:"))
async def bot_demo_reaction(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    tag = cb.data.split(":")[1]
    reactions = {
        "wow":       "🔥 Отлично! Такой бот можно сделать именно под ваш бизнес.",
        "questions": "Конечно, разберём все вопросы — для этого пара уточнений:",
        "price":     "Сейчас посчитаем — зависит от функционала. Пара вопросов:",
        "custom":    "Сделаю под ваши задачи! Чтобы предложить точное решение:",
    }
    await state.update_data(bot_reaction=tag)
    await edit_or_answer(cb,
        f"{reactions.get(tag, '')}\n\nСколько заявок получаете в месяц сейчас?",
        reply_markup=kb(
            ("📉 Меньше 10", "leads:low"),
            ("📊 10–30", "leads:mid"),
            ("📈 30–100", "leads:high"),
            ("🚀 Больше 100", "leads:top"),
            ("🆕 Только начинаю", "leads:zero"),
        )
    )
    await state.set_state(Funnel.q_leads)


# ── БЛОК 3: КВАЛИФИКАЦИЯ ──────────────────────────────────────────────────────

@router.callback_query(Funnel.q_leads, F.data.startswith("leads:"))
async def q_leads(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.update_data(leads=cb.data.split(":")[1])
    await edit_or_answer(cb,
        "2️⃣ Какой бюджет рассматриваете на разработку?",
        reply_markup=kb(
            ("💰 До 30 000 ₽", "budget:low"),
            ("💰💰 30–60 000 ₽", "budget:mid"),
            ("💰💰💰 60–100 000 ₽", "budget:high"),
            ("💎 100 000+ ₽", "budget:premium"),
            ("🤔 Зависит от результата", "budget:discuss"),
        )
    )
    await state.set_state(Funnel.q_budget)


@router.callback_query(Funnel.q_budget, F.data.startswith("budget:"))
async def q_budget(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.update_data(budget=cb.data.split(":")[1])
    await edit_or_answer(cb,
        "3️⃣ Когда планируете запуститься?",
        reply_markup=kb(
            ("🔥 Ещё вчера нужно было", "timeline:asap"),
            ("⚡ На этой неделе", "timeline:week"),
            ("📅 В течение месяца", "timeline:month"),
            ("🤷 Пока изучаю варианты", "timeline:later"),
        )
    )
    await state.set_state(Funnel.q_timeline)


# ── БЛОК 4: КП ────────────────────────────────────────────────────────────────

BUDGET_MAP = {
    "low":     "low",
    "mid":     "mid",
    "high":    "high",
    "premium": "high",
    "discuss": "mid",
}

TIMELINE_COMMENTS = {
    "asap":  "🔥 Отлично — возьму в работу хоть завтра.",
    "week":  "⚡ Успеем — стартуем на этой неделе.",
    "month": "📅 Хорошо, время есть — сделаем без спешки.",
    "later": "👍 Понял, никакого давления.",
}


@router.callback_query(Funnel.q_timeline, F.data.startswith("timeline:"))
async def q_timeline(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    timeline = cb.data.split(":")[1]
    await state.update_data(timeline=timeline)

    data = await state.get_data()
    budget_key = BUDGET_MAP.get(data.get("budget", "mid"), "mid")
    product = data.get("product", "site")
    offer = config.OFFERS[budget_key]
    timeline_comment = TIMELINE_COMMENTS.get(timeline, "")

    if product == "bot":
        title, details = offer["bot"]
        text = (
            f"{timeline_comment}\n\n"
            f"Вот что предлагаю под ваш запрос:\n\n"
            f"🤖 <b>{title}</b>\n\n{details}"
        )
    elif product == "both":
        st, sd = offer["site"]
        bt, bd = offer["bot"]
        text = (
            f"{timeline_comment}\n\n"
            f"Связка под ваш бюджет:\n\n"
            f"🌐 <b>{st}</b>\n{sd}\n\n"
            f"🤖 <b>{bt}</b>\n{bd}\n\n"
            f"💡 При заказе вместе — скидка 10%"
        )
    else:
        title, details = offer["site"]
        text = (
            f"{timeline_comment}\n\n"
            f"Вот что предлагаю под ваш запрос:\n\n"
            f"🌐 <b>{title}</b>\n\n{details}"
        )

    await edit_or_answer(cb, text,
        reply_markup=kb(
            ("✅ Отлично, давайте работать!", "offer:yes"),
            ("💳 Можно разбить оплату?",     "offer:installment"),
            ("💰 Дорого...",                  "offer:expensive"),
            ("🤔 Нужно подумать",             "offer:think"),
        )
    )
    await state.set_state(Funnel.offer_reaction)

    # Сохраняем лид
    user = cb.from_user
    lead_id = await save_lead(
        user_id=user.id, username=user.username, full_name=user.full_name,
        answers={k: str(v) for k, v in data.items()},
        utm={}, completed=False,
    )
    await notify_admins(cb.bot, {
        "Пользователь": f"{user.full_name} @{user.username}",
        "Продукт": product, "Бюджет": data.get("budget"),
        "Заявки/мес": data.get("leads"), "Срок": timeline,
    })
    await push_to_crm(lead_id, user.id, user.username, user.full_name,
                      data, {})


# ── БЛОК 5: РАБОТА С ВОЗРАЖЕНИЯМИ ────────────────────────────────────────────

@router.callback_query(Funnel.offer_reaction, F.data == "offer:yes")
async def offer_yes(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await cancel_followup(cb.from_user.id)
    await edit_or_answer(cb,
        "🎉 Отлично! Рад работать с вами.\n\n"
        "Запишемся на короткий созвон — обсудим детали и стартуем 🚀"
    )
    await send_lead_magnet(cb.message)
    await start_booking(cb, state)


@router.callback_query(Funnel.offer_reaction, F.data == "offer:installment")
async def offer_installment(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await edit_or_answer(cb,
        "💳 Конечно, работаю с удобной оплатой:\n\n"
        "• 50% предоплата → 50% при сдаче\n"
        "• Или по этапам: 30% → 40% → 30%\n\n"
        "Выберите удобный вариант — и стартуем 🚀",
        reply_markup=kb(
            ("✅ 50/50 — подходит",          "final:50_50"),
            ("📋 По этапам 30/40/30",         "final:stages"),
            ("📞 Обсудить на созвоне",         "final:call"),
        )
    )
    await state.set_state(Funnel.objection)


@router.callback_query(Funnel.offer_reaction, F.data == "offer:expensive")
async def offer_expensive(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    data = await state.get_data()
    product = data.get("product", "сайт")
    prod_label = {"site": "сайт/лендинг", "bot": "бот", "both": "сайт + бот"}.get(product, "проект")
    await edit_or_answer(cb,
        f"Понимаю — давайте посчитаем окупаемость.\n\n"
        f"📊 Если {prod_label} принесёт всего <b>2 новых клиента в месяц</b>\n"
        f"💰 При среднем чеке <b>15 000 ₽</b> = +30 000 ₽/мес\n"
        f"📈 За год это <b>+360 000 ₽</b> дохода\n\n"
        f"Инвестиция окупается уже в первый месяц.\n\n"
        f"Плюс разобьём оплату — не нужно платить всё сразу:",
        reply_markup=kb(
            ("✅ Логично, давайте работать",  "final:yes"),
            ("💳 Интересует рассрочка",       "final:stages"),
            ("📞 Обсудить детали на созвоне", "final:call"),
            ("🤔 Всё равно нужно подумать",   "final:think"),
        )
    )
    await state.set_state(Funnel.objection)


@router.callback_query(Funnel.offer_reaction, F.data == "offer:think")
async def offer_think(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await edit_or_answer(cb,
        "Конечно, спешить не нужно 🤝\n\n"
        "Пока думаете — держите гайд: там сравнение всех инструментов "
        "и примеры окупаемости по нишам. Поможет принять решение.\n\n"
        "Когда будете готовы — просто напишите. "
        "Или сразу запишитесь на короткий созвон без обязательств 👇",
        reply_markup=kb(
            ("📅 Записаться на созвон", "final:call"),
            ("📨 Напишу сам позже",     "final:later"),
        )
    )
    await send_lead_magnet(cb.message)
    await state.set_state(Funnel.objection)


# ── ФИНАЛ ─────────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("final:"))
async def final(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    tag = cb.data.split(":")[1]
    await cancel_followup(cb.from_user.id)

    if tag in ("yes", "50_50", "stages"):
        await edit_or_answer(cb,
            "🎉 Отлично! Осталось согласовать детали.\n\n"
            "Запишемся на 20-минутный созвон — обсудим проект и стартуем 🚀"
        )
        await send_lead_magnet(cb.message)
        await start_booking(cb, state)
        return
    elif tag == "call":
        await edit_or_answer(cb, "📞 Отлично! Запишемся на созвон 👇")
        await send_lead_magnet(cb.message)
        await start_booking(cb, state)
        return
    elif tag in ("later", "think"):
        await edit_or_answer(cb,
            "👍 Хорошо! Когда будете готовы — просто напишите /start\n\n"
            "Буду рад помочь с вашим проектом 🙌"
        )
        await send_lead_magnet(cb.message)
    await state.clear()


# ── ADMIN ─────────────────────────────────────────────────────────────────────

def admin_only(fn):
    async def wrapper(msg: Message, *a, **kw):
        if msg.from_user.id not in config.ADMIN_IDS:
            return
        return await fn(msg, *a, **kw)
    wrapper.__name__ = fn.__name__
    return wrapper


@router.message(Command("stats"))
@admin_only
async def cmd_stats(message: Message):
    s = await get_stats()
    lines = [
        "📊 <b>Статистика</b>", "",
        f"👥 Пользователей: <b>{s['users']}</b>",
        f"📋 Лидов: <b>{s['total']}</b>",
        f"✅ Завершили: <b>{s['completed']}</b> ({s['conversion']}%)",
        f"📅 Сегодня: <b>{s['today']}</b>",
    ]
    if s.get("needs"):
        lines += ["", "🛠 Запросы:"]
        for n, c in s["needs"]:
            lines.append(f"  • {n}: {c}")
    await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(Command("export"))
@admin_only
async def cmd_export(message: Message):
    await message.answer("⏳ Формирую файл...")
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
        path = f.name
    try:
        count = await export_leads_xlsx(path)
        if not count:
            await message.answer("Лидов пока нет.")
            return
        await message.answer_document(
            FSInputFile(path, filename="leads.xlsx"),
            caption=f"📊 {count} лидов"
        )
    finally:
        os.unlink(path)


@router.message(Command("broadcast"))
@admin_only
async def cmd_broadcast(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Использование: /broadcast Текст")
        return
    text = parts[1]
    ids = await get_all_user_ids()
    ok = fail = 0
    for uid in ids:
        try:
            await message.bot.send_message(uid, text)
            ok += 1
        except Exception:
            fail += 1
    await message.answer(f"✅ {ok} доставлено, ❌ {fail} ошибок")
