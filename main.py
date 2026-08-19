import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage, SimpleEventIsolation
from aiogram.types import BotCommand

from config import settings
from db.database import async_session_maker, check_database_connection, engine
from handlers import router
from logger import logger
from middlewares.database import DatabaseSessionMiddleware


async def main() -> None:
    bot = Bot(settings.bot_token)
    dispatcher = Dispatcher(
        storage=MemoryStorage(), events_isolation=SimpleEventIsolation()
    )
    dispatcher.update.outer_middleware(DatabaseSessionMiddleware(async_session_maker))
    dispatcher.include_router(router)

    try:
        await check_database_connection()
        bot_info = await bot.get_me()
        await bot.set_my_commands(
            [BotCommand(command="start", description="Открыть главное меню")]
        )
        logger.info("База данных доступна")
        logger.info("Бот @%s запущен в демо-режиме", bot_info.username)
        await dispatcher.start_polling(
            bot,
            allowed_updates=dispatcher.resolve_used_update_types(),
        )
    except Exception:
        logger.exception("Бот остановлен из-за критической ошибки")
        raise
    finally:
        await bot.session.close()
        await engine.dispose()
        logger.info("Бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())
