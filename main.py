import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import config
from DB.db import DB
from handlers import order_handlers, account_handlers, helps_handlers, object_handlers, states_handlers, other_handlers

storage = MemoryStorage()
db = Dispatcher(storage=storage)
bot = Bot(token=config.BOT_TOKEN)
mongo_db = DB(config.MONGO_DB_URL, "login")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


async def main():
    logging.info(f"Бот запущен")
    db.include_router(object_handlers.router)
    db.include_router(helps_handlers.router)
    db.include_router(account_handlers.router)
    db.include_router(states_handlers.router)
    db.include_router(order_handlers.router)
    db.include_router(other_handlers.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await db.start_polling(bot)


if __name__ == "__main__":
    logging.info(f"Программа запущена")
    asyncio.run(main())
