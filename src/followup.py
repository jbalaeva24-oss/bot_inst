"""Follow-up цепочка: 1ч → 24ч → 3 дня."""
import asyncio
import logging
from aiogram import Bot
from src.db import get_pending_followups, mark_followup_sent

logger = logging.getLogger(__name__)

MESSAGES = [
    # 1 час
    """\
👋 Здравствуйте, это снова я.

Вы начали заполнять форму, но куда-то пропали — бывает, понимаю.

Вопросов там всего 4, занимает буквально минуту.
В конце пришлю гайд и скажу, что подойдёт именно вам 👇

/start\
""",
    # 24 часа
    """\
⏰ Напоминаю о себе.

Вы так и не забрали гайд «Сайт или бот — как не ошибиться с выбором».

Он бесплатный. Помогает не потратить деньги не на тот инструмент — \
это случается чаще, чем кажется.

Забрать гайд: /start\
""",
    # 3 дня
    """\
📌 Последнее сообщение.

Если думаете над запуском сайта или бота — напишите прямо сейчас.
Разберём вашу задачу и скажу честно: что нужно, сколько стоит и когда будет готово.

Без воды и навязывания.

Просто напишите «привет» — и начнём 👇\
""",
]


async def followup_loop(bot: Bot) -> None:
    while True:
        try:
            rows = await get_pending_followups()
            for fid, uid, step in rows:
                text = MESSAGES[step] if step < len(MESSAGES) else MESSAGES[-1]
                try:
                    await bot.send_message(uid, text)
                except Exception as e:
                    logger.warning("followup uid=%s step=%s: %s", uid, step, e)
                await mark_followup_sent(fid)
        except Exception as e:
            logger.error("followup_loop: %s", e)
        await asyncio.sleep(600)
