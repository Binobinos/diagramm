from decouple import config
from aiogram.fsm.storage.memory import MemoryStorage

BOT_TOKEN = config("BOT_TOKEN")
MONGO_DB_URL = config("MONGO_DB_URL")
storage = MemoryStorage()