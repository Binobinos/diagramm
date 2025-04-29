from aiogram import Router, F
from aiogram import types

from func.dob_func_ import help_menu
from main import *

router = Router()
logging.basicConfig(level=config.LOGGING_LEVEL, format="%(asctime)s %(levelname)s %(message)s")

@router.callback_query(F.data.startswith("help"))
async def help_(callback: types.CallbackQuery):
    logging.info(f"пользователь {callback.from_user.username} открыл справку")
    _id = callback.data.split("_")[1]
    texts = {
        "💲 Оплата": "оплата",
        "📂 Цена-образование": "оплата",
        "🔑 Безопасность": "цена",
        "🛠 Гарантии": "гарантии"
    }
    print(list(texts.values())[int(_id)])
    await help_menu(callback.from_user.id, list(texts.values())[int(_id)], texts.keys())
    await callback.answer()
