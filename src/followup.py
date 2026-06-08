"""Follow-up цепочка: 1ч → 24ч → 3 дня."""
import asyncio
import logging
from aiogram import Bot
from src.db import get_pending_followups, mark_followup_sent

logger = logging.getLogger(__name__)

MESSAGES = [
    # 1 час
    """\
👋 Привет, это я снова.

Ты начал заполнять форму, но куда‑то пропал.

Понимаю — дела, встречи, всё навалилось.
Но вопросов там всего 4, занимает буквально минуту.

В конце пришлю гайд и скажу, что нужно именно тебе 👇
/start\
""",
    # 24 часа
    """\
⏰ Напоминаю о себе.

Ты не забрал гайд «Бот, лендинг или сайт — как не ошибиться».

Он бесплатный. Помогает не слить деньги на не тот инструмент.
Это случается чаще, чем кажется.

Забрать гайд: /start\
""",
    # 3 дня
    """\
📌 Финальное напоминание.

Если думаешь над запуском бота, лендинга или сайта —
напиши мне прямо сейчас. Разберём твою задачу и я скажу честно:
что нужно, сколько стоит, когда будет готово.

Без воды и без впаривания.

Просто напиши «привет» — и начнём 👇\
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
