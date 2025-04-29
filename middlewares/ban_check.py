from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from config import mongo_db
from model.user import User


class BanMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        acc: User = await mongo_db.get_user(event.from_user.id)
        if acc:
            if not acc.is_ban:
                result = await handler(event, data)  # Передаём управление дальше
                return result
            else:
                await event.answer("🚫 Вы заблокированы!", show_alert=True)
        else:
            result = await handler(event, data)  # Передаём управление дальше
            return result
