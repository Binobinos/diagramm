import asyncio
import logging

import config
from handlers import order_handlers, account_handlers, helps_handlers, object_handlers, states_handlers, other_handlers

logging.basicConfig(level=config.LOGGING_LEVEL, format="%(asctime)s %(levelname)s %(message)s")


async def main():
    logging.info(f"Бот запущен")
    config.db.include_routers(object_handlers.router,
                              helps_handlers.router,
                              account_handlers.router,
                              states_handlers.router,
                              order_handlers.router,
                              other_handlers.router)
    await config.bot.delete_webhook(drop_pending_updates=True)
    await config.db.start_polling(config.bot)


if __name__ == "__main__":
    logging.info(f"Программа запущена")
    asyncio.run(main())
