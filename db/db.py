from typing import Optional, List, Any, Mapping

from motor.motor_asyncio import AsyncIOMotorClient

from model.user import User
from model.order import Orders
from model.reqwest import Reqwest


class DB:
    """ Класс для работы с базой данных mongo db motor"""
    __slots__ = ["client", "db"]  # Ускорение через статичные поля

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
        """ Получения списка всех админов """
        cursor = self.db["login"].find({"user_level": "admin"})
        admins = await cursor.to_list(length=None)
        return [User(**admin) for admin in admins]

    async def get_user_fio(self, fio: str) -> Optional[User]:
        """Получение пользователя по полному имени ФИО"""
        user_data = await self.db["login"].find_one({"full_name": fio})
        if user_data:
            return User(**user_data)
        else:
            return None

    async def insert_user(self, new_user: User) -> User:
        """Вставка нового пользователя в базу данных."""
        await self.db["login"].insert_one(new_user.model_dump())
        return new_user

    async def delete_user(self, user_id: User):
        """Удаления пользователя по его ID"""
        await self.db["login"].delete_one({"id": user_id.id})
        return user_id

    async def update_user(self, update_user: User) -> User:
        """ Обновление пользователя """
        await self.db["login"].update_one(
            {"id": update_user.id},
            {"$set": update_user.model_dump()}
        )

        return await self.get_user(update_user.id)

    async def get_order(self, order_id: str) -> Optional[Orders]:
        """ Получение всех заказов """
        orders_data = await self.db["Orders"].find_one({"id": order_id})
        if orders_data:
            return Orders(**orders_data)
        else:
            return None

    async def insert_order(self, order: Orders) -> Orders:
        """ Вставка нового заказа """
        await self.db["Orders"].insert_one(order.model_dump())
        return order

    async def delete_order(self, order: Orders):
        """ Удаление заказа """
        await self.db["Orders"].delete_one({"id": order.id})
        return order

    async def update_order(self, order: Orders) -> Orders:
        """ Обновление заказа"""
        await self.db["Orders"].update_one(
            {"id": order.id},
            {"$set": order.model_dump()}
        )

        return await self.get_order(order.id)

    async def get_all_orders(self) -> list[Mapping[str, Any] | Any]:
        """ Получение всех заказов """
        return await self.db["Orders"].find().to_list(None)

    async def insert_reqwest(self, reqwest: Reqwest) -> Reqwest:
        """ Вставка нового обращения"""
        await self.db["reqwest"].insert_one(reqwest.model_dump())
        return reqwest

    async def delete_reqwest(self, reqwest: Reqwest):
        """ Удаление обращения """
        await self.db["reqwest"].delete_one({"id": reqwest.id})
        return reqwest

    async def update_reqwest(self, reqwest: Reqwest) -> Reqwest:
        """
        Обновление обращения
        :param reqwest: Новое обращение
        :return:
        """
        await self.db["reqwest"].update_one(
            {"id": reqwest.id},
            {"$set": reqwest.model_dump()}
        )

        return await self.get_reqwest(reqwest.id)

    async def get_all_reqwest(self) -> list[Mapping[str, Any] | Any]:
        """ Получение всех обращений"""
        return await self.db["reqwest"].find().to_list(None)

    async def get_reqwest(self, reqwest_id: str) -> Optional[Reqwest]:
        """
                Получения обращения через его айди
        :param reqwest_id: ID обращения
        :return: Обращение
        """
        orders_data = await self.db["reqwest"].find_one({"id_": reqwest_id})
        if orders_data:
            return Reqwest(**orders_data)
        else:
            return None
