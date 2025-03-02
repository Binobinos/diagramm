from typing import Optional, List

from motor.motor_asyncio import AsyncIOMotorClient

from model.User import User


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
