import asyncio
import logging

import config
from handlers import order_handlers, account_handlers, helps_handlers, object_handlers, states_handlers, other_handlers

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


async def main():
    logging.info(f"Бот запущен")
    config.db.include_router(object_handlers.router)
    config.db.include_router(helps_handlers.router)
    config.db.include_router(account_handlers.router)
    config.db.include_router(states_handlers.router)
    config.db.include_router(order_handlers.router)
    config.db.include_router(other_handlers.router)
    await config.bot.delete_webhook(drop_pending_updates=True)
    await config.db.start_polling(config.bot)


if __name__ == "__main__":
    logging.info(f"Программа запущена")
    asyncio.run(main())
