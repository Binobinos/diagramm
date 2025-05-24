from aiogram import Router, F
from aiogram import types
from aiogram.filters import Command


from func.dob_func_ import help_menu, send_photo_with_buttons
from main import *

router = Router()
logging.basicConfig(level=config.LOGGING_LEVEL, format="%(asctime)s %(levelname)s %(message)s")

@router.callback_query(F.data.startswith("help"))
async def help_(callback: types.CallbackQuery):
    logging.info(f"пользователь {callback.from_user.username} открыл справку")
    _id = callback.data.split("_")[1]
    texts = {
        "💲 Оплата": "У нас доступны различные способы оплаты, включая банковские карты, электронные кошельки и "
                    "криптовалюты. Оплата проходит быстро и безопасно.",
        "📂 Ценообразование": "Наши цены формируются с учетом качества услуг и рыночной конкуренции. Мы предлагаем "
                             "гибкую систему скидок для постоянных клиентов.",
        "🔑 Безопасность": "Ваши данные защищены современными методами шифрования. Мы гарантируем конфиденциальность "
                          "и безопасность всех операций.",
        "🛠 Гарантии": "Мы предоставляем гарантии на все услуги. В случае возникновения проблем, наша поддержка "
                      "поможет их быстро решить."
    }
    print(list(texts.values())[int(_id)])
    await send_photo_with_buttons(callback.from_user.id, r"\#Тест")
    await help_menu(callback.from_user.id, list(texts.values())[int(_id)], texts.keys(), current=_id)
    await callback.answer()


@router.message(Command('help'))
async def help_command(callback: types.CallbackQuery):
    await callback.answer("123")
