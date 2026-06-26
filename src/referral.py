"""Реферальная система."""
import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import config
from src.db import add_referral, get_referral_stats, complete_referral

log = logging.getLogger(__name__)
router = Router()

BOT_USERNAME = "Test1lidbot_bot"  # обновится автоматически при старте


def ref_link(user_id: int) -> str:
    return f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"


async def parse_ref(start_payload: str, new_user_id: int) -> int | None:
    """Парсит реф из payload /start ref_12345. Возвращает referrer_id или None."""
    if not start_payload.startswith("ref_"):
        return None
    try:
        referrer_id = int(start_payload[4:])
        if referrer_id == new_user_id:
            return None  # нельзя рефовать себя
        await add_referral(referrer_id, new_user_id)
        return referrer_id
    except (ValueError, Exception) as e:
        log.warning("parse_ref error: %s", e)
        return None


async def notify_referrer(bot, referrer_id: int, referred_name: str) -> None:
    """Уведомляем реферера что по его ссылке пришёл новый пользователь."""
    try:
        stats = await get_referral_stats(referrer_id)
        await bot.send_message(
            referrer_id,
            f"🎉 По твоей реферальной ссылке пришёл новый человек!\n\n"
            f"👤 {referred_name}\n\n"
            f"📊 Всего рефералов: {stats['total']}\n"
            f"✅ Завершили воронку: {stats['completed']}\n\n"
            f"Когда он дойдёт до конца — ты получишь скидку 10% на следующий заказ 🎁",
        )
    except Exception as e:
        log.warning("notify_referrer %s: %s", referrer_id, e)


async def notify_referral_complete(bot, referrer_id: int, referred_name: str) -> None:
    """Уведомляем реферера что его реферал завершил воронку."""
    try:
        stats = await get_referral_stats(referrer_id)
        await bot.send_message(
            referrer_id,
            f"🔥 Отличная новость!\n\n"
            f"Человек которого ты привёл ({referred_name}) "
            f"только что оставил заявку на созвон.\n\n"
            f"✅ Завершённых рефералов: {stats['completed']}\n\n"
            f"🎁 Напомни об этом при следующем заказе — дам скидку 10%!",
        )
    except Exception as e:
        log.warning("notify_referral_complete %s: %s", referrer_id, e)


@router.message(Command("ref"))
async def cmd_ref(message: Message) -> None:
    user = message.from_user
    stats = await get_referral_stats(user.id)
    link = ref_link(user.id)

    text = (
        f"🔗 <b>Твоя реферальная ссылка:</b>\n"
        f"<code>{link}</code>\n\n"
        f"Поделись с коллегами и знакомыми кому нужны сайты или боты.\n\n"
        f"📊 <b>Твоя статистика:</b>\n"
        f"👥 Пришло по ссылке: <b>{stats['total']}</b>\n"
        f"✅ Оставили заявку: <b>{stats['completed']}</b>\n\n"
        f"🎁 <b>За каждого завершившего воронку — скидка 10% на твой следующий заказ.</b>"
    )
    await message.answer(text, parse_mode="HTML")
