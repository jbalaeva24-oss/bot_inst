import asyncio
import logging
from dotenv import load_dotenv
load_dotenv()

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import config
from src.db import init_db
from src.funnel import router
from src.booking import router as booking_router
from src.followup import followup_loop


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    # Генерируем PDF при каждом старте
    try:
        from pathlib import Path
        import sys, os
        sys.path.insert(0, os.path.dirname(__file__))
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        from make_pdf import make
        make()
        logging.getLogger(__name__).info("PDF сгенерирован")
    except Exception as e:
        logging.getLogger(__name__).warning("PDF не сгенерирован: %s", e)

    await init_db()

    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    dp.include_router(booking_router)

    asyncio.create_task(followup_loop(bot))

    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    asyncio.run(main())
