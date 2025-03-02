from typing import Optional, List, Any, Mapping

from motor.motor_asyncio import AsyncIOMotorClient

from model.User import User
from model.order import Orders


class DB:
    def __init__(self, client: str, db_name: str):
        """Инициализация подключения к базе данных."""
        self.client = AsyncIOMotorClient(client)
        self.db = self.client[db_name]

    async def get_user(self, user_id: int) -> Optional[User]:
        """Получение пользователя по его ID."""
        user_data = await self.db["login"].find_one({"id": user_id})
        if user_data:
            return User(**user_data)
        else:
            return None

    async def get_admins(self) -> List[User]:
        """Retrieve all users with admin level."""
        cursor = self.db["login"].find({"user_level": "admin"})
        admins = await cursor.to_list(length=None)
        return [User(**admin) for admin in admins]

    async def get_user_fio(self, fio: str) -> Optional[User]:
        """Получение пользователя по полному имени (FIO)."""
        user_data = await self.db["login"].find_one({"full_name": fio})
        if user_data:
            return User(**user_data)
        else:
            return None

    async def insert_user(self, user: User) -> User:
        """Вставка нового пользователя в базу данных."""
        # Преобразуем UUID в BSON Binary, если это необходимо
        await self.db["login"].insert_one(user.model_dump())
        return user

    async def delete_user(self, user: User):
        """Delete a user by their ID."""
        await self.db["login"].delete_one({"id": user.id})
        return user

    async def update_user(self, user: User) -> User:
        await self.db["login"].update_one(
            {"id": user.id},
            {"$set": user.model_dump()}
        )

        return await self.get_user(user.id)

    async def get_order(self, order_id: str) -> Optional[Orders]:
        orders_data = await self.db["Orders"].find_one({"id": order_id})
        if orders_data:
            return Orders(**orders_data)
        else:
            return None

    async def insert_order(self, order: Orders) -> Orders:
        await self.db["Orders"].insert_one(order.model_dump())
        return order

    async def delete_order(self, order: Orders):
        await self.db["Orders"].delete_one({"id": order.id})
        return order

    async def update_order(self, order: Orders) -> Orders:
        await self.db["Orders"].update_one(
            {"id": order.id},
            {"$set": order.model_dump()}
        )

        return await self.get_order(order.id)

    async def get_all_orders(self) -> list[Mapping[str, Any] | Any]:
        return await self.db["Orders"].find().to_list(None)
