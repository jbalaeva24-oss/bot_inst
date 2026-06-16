"""Запись на созвон через Telegram — без внешних сервисов."""
import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import config
from src.states import F as Funnel
from src.keyboards import kb, remove_keyboard
from src.db import cancel_followup

log = logging.getLogger(__name__)
router = Router()


async def start_booking(target: CallbackQuery | Message, state: FSMContext) -> None:
    """Точка входа — вызывается из любого места воронки."""
    msg = target.message if isinstance(target, CallbackQuery) else target

    await msg.answer(
        "📅 Отлично! Запишу тебя на созвон.\n\n"
        "Когда тебе удобно поговорить?\n"
        "Выбери или напиши своё время 👇",
        reply_markup=kb(
            ("Сегодня после 18:00",       "btime:today_evening"),
            ("Завтра утром (10:00–12:00)", "btime:tomorrow_morning"),
            ("Завтра днём (13:00–17:00)",  "btime:tomorrow_day"),
            ("На этой неделе, гибко",      "btime:this_week"),
            ("✏️ Напишу своё время",        "btime:custom"),
        )
    )
    await state.set_state(Funnel.booking_time)


@router.callback_query(Funnel.booking_time, F.data.startswith("btime:"))
async def booking_time_chosen(cb: CallbackQuery, state: FSMContext) -> None:
    await cb.answer()
    tag = cb.data.split(":")[1]

    labels = {
        "today_evening":    "сегодня после 18:00",
        "tomorrow_morning": "завтра утром (10:00–12:00)",
        "tomorrow_day":     "завтра днём (13:00–17:00)",
        "this_week":        "на этой неделе, гибко",
    }

    if tag == "custom":
        await cb.message.answer(
            "✏️ Напиши удобное время — например:\n"
            "«Завтра в 15:00» или «В пятницу утром»",
            reply_markup=remove_keyboard,
        )
        await state.update_data(booking_time="custom")
        # остаёмся в booking_time — ждём текстовый ответ
    else:
        time_label = labels[tag]
        await state.update_data(booking_time=time_label)
        await cb.message.answer(
            f"Записал: <b>{time_label}</b> ✅\n\n"
            "Как к тебе обращаться и куда написать?\n"
            "Оставь имя и @username или номер телефона:",
            reply_markup=remove_keyboard,
            parse_mode="HTML",
        )
        await state.set_state(Funnel.booking_contact)


@router.message(Funnel.booking_time, F.text)
async def booking_time_text(message: Message, state: FSMContext) -> None:
    """Пользователь написал своё время."""
    await state.update_data(booking_time=message.text.strip())
    await message.answer(
        f"Записал: <b>{message.text.strip()}</b> ✅\n\n"
        "Как к тебе обращаться и куда написать?\n"
        "Оставь имя и @username или номер телефона:",
        reply_markup=remove_keyboard,
        parse_mode="HTML",
    )
    await state.set_state(Funnel.booking_contact)


@router.message(Funnel.booking_contact, F.text)
async def booking_contact_received(message: Message, state: FSMContext) -> None:
    """Получили контакт — сохраняем и шлём заявку админу."""
    data = await state.get_data()
    user = message.from_user
    contact = message.text.strip()
    time_label = data.get("booking_time", "не указано")

    await cancel_followup(user.id)

    # Подтверждение пользователю
    await message.answer(
        "🎉 Заявка принята!\n\n"
        f"🕐 Время: <b>{time_label}</b>\n"
        f"📱 Контакт: <b>{contact}</b>\n\n"
        "Напишу тебе лично в указанное время.\n"
        "Если нужно раньше — просто напиши здесь 👇",
        parse_mode="HTML",
        reply_markup=remove_keyboard,
    )

    # Уведомление всем админам
    if config.ADMIN_IDS:
        tg_link = f"@{user.username}" if user.username else f"tg://user?id={user.id}"
        admin_text = (
            "🔔 <b>Новая заявка на созвон!</b>\n\n"
            f"👤 Имя: {user.full_name}\n"
            f"🔗 Telegram: {tg_link}\n"
            f"📱 Контакт: {contact}\n"
            f"🕐 Удобное время: <b>{time_label}</b>\n\n"
            f"📋 Что интересует: {data.get('product', '—')}\n"
            f"💰 Бюджет: {data.get('budget', '—')}\n\n"
            "👆 Напиши ему первым!"
        )
        for aid in config.ADMIN_IDS:
            try:
                await message.bot.send_message(aid, admin_text, parse_mode="HTML")
            except Exception as e:
                log.warning("notify admin %s: %s", aid, e)

    await state.clear()
