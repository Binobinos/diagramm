import asyncio
import datetime
from uuid import uuid4

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import helps_handlers
import config
from DB.db import DB
from keyboards.keyboard import *
from model.order import Orders
from model.reqwest import Reqwest
from handlers import states_handlers
from model.temp_Order import Temp_order
from handlers import object_handlers
from states.states import Registration, EditAccount, Support
from dob_func.dob_func import send_or_edit_menu
from dob_func.dob_func import start_registration, show_main_menu, show_order,show_client_order,show_orders_menu,show_tofar,send_admins,start_help
from handlers import account_handlers

storage = MemoryStorage()
db = Dispatcher(storage=storage)
bot = Bot(token=config.BOT_TOKEN)
mongo_db = DB(config.MONGO_DB_URL, "login")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
parallels = {
    "5": [["А", "Б", "В", "Г", "Д", "Е", "Ж", "З", 'У'],
          ['Биология', "География", "ИЗО", "Английский язык", "Информатика", "Литература", "Математика", "Музыка",
           "ОДНКР", "Русский язык", "Труд", "Учебный Курс", "Физра"]],
    "6": [["А", "Б", "В", "Г", "Д", "Е", "Ж", "З", "И", 'У'],
          ['Биология', "География", "ИЗО", "Английский язык", "Информатика", "Литература", "Математика", "Музыка",
           "ОДНКР", "Русский язык", "Труд", "Обществознание", "Физра"]],
    "7": [["А", "Б", "В", "Г", "Д", "Е", "Ж", "З", "И"],
          ['Биология', "География", "Вероятность и Статистика", "ИЗО", "Английский язык", "Информатика", "Литература",
           "Алгебра", "Геометрия", "Музыка",
           "ОДНКР", "Русский язык", "Труд", "Обществознание", "Физра", "Физика"]],
    "8": [["А", "Б", "В", "Г", "Д", "Е", "Ж", "З", "К"],
          ['Биология', "География", "Вероятность и Статистика", "Английский язык", "Информатика", "Литература",
           "Алгебра", "Геометрия", "Музыка",
           "ОДНКР", "Русский язык", "Труд", "Обществознание", "Физра", "Физика", "ОБЖ"]],
    "9": [["А", "Б", "В", "Г", "Д", "Е", "Ж", "К"],
          ['Биология', "География", "Вероятность и Статистика", "Английский язык", "Информатика", "Литература",
           "Алгебра", "Геометрия", "Музыка",
           "ОДНКР", "Русский язык", "Труд", "Обществознание", "Физра", "Физика", 'ОБЖ']],
    "10": [["А", "Б", "В", "Г", "К"],
           ['Биология', "География", "Вероятность и Статистика", "Английский язык", "Информатика", "Литература",
            "Алгебра и начало мат. анализа", "Геометрия", "Музыка",
            "ОДНКР", "Русский язык", "Труд", "Обществознание", "Физра", "Физика", 'ОБЖ']],
    "11": [["А", "Б", "В", "Г", "К"],
           ['Биология', "География", "Вероятность и Статистика", "Английский язык", "Информатика", "Литература",
            "Алгебра и начало мат. анализа", "Геометрия", "Музыка",
            "ОДНКР", "Русский язык", "Труд", "Обществознание", "Физра", "Физика", 'ОБЖ']]
}
type_items = {"Работа на уроке": 1, "Самостоятельная работа": 1.04, "Проверочная работа": 1.05,
              "Контрольная работа": 1.06}


# Обработчики
@db.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.from_user.username
    acc: User = await mongo_db.get_user(user_id)
    if acc is None:
        logging.info(f"пользователь {user_name} нажал start")
        await message.answer("👋 Добро пожаловать! Для начала создайте свой первый аккаунт.")
        await start_registration(user_id, state)
    else:
        if not acc.ban:
            await show_main_menu(user_id)
        else:
            logging.info(f"забаненный пользователь {user_name} нажал start")
            await message.answer("👋 Вы забанены")


@db.callback_query(F.data == "main_menu")
async def back_to_main(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_name = callback.from_user.username
    acc: User = await mongo_db.get_user(user_id)
    if acc is None:
        logging.info(f"пользователь {user_name} нажал start")
        await callback.answer("👋 Добро пожаловать! Для начала создайте свой первый аккаунт.")
        await start_registration(user_id, state)
    else:
        if not acc.ban:
            logging.info(f"пользователь {callback.from_user.username} переходит в главное меню")
            await show_main_menu(callback.from_user.id)
            await callback.answer()
        else:
            logging.info(f"забаненный пользователь {user_name} нажал start")
            await callback.answer("👋 Вы забанены")


@db.callback_query(F.data == "order")
async def show_my_order(callback: types.CallbackQuery):
    logging.info(f"пользователь {callback.from_user.username} открыл корзиину")
    await show_order(callback.from_user.id)
    await callback.answer()


@db.callback_query(F.data.startswith("*order-new_"))
async def show_admin_order(callback: types.CallbackQuery):
    logging.info(f"пользователь {callback.from_user.username} открыл корзиину")
    ids = callback.data.split('_')[1]
    order = await mongo_db.get_order(ids)
    await show_client_order(order, callback.from_user.id)
    await callback.answer()


@db.callback_query(F.data.startswith("Orders_"))
async def start_create_account(callback: types.CallbackQuery):
    start = int(callback.data.split("_")[1])
    logging.info(f"Админ {callback.from_user.username} переходит в заказы c {start}")
    await show_orders_menu(callback.from_user.id, start)
async def create_temp_order(user_id:int):
    acc = await mongo_db.get_user(user_id)
    acc.order.products.append(
        Temp_order(id=str(uuid4()), object=acc.temp_order["предмет"], quarter=acc.temp_order["Четверть"],
                   type=acc.temp_order["Тип оценки"], estimation=acc.temp_order["Оценка"],
                   price=int(
                       calculating_the_price({acc.temp_order["Тип оценки"]: {"1 Оценка": 0,
                                                                             "2 Оценка":
                                                                                 acc.temp_order[
                                                                                     "Оценка"],
                                                                             "предмет":
                                                                                 acc.temp_order[
                                                                                     "предмет"]}}))))
    acc.temp_order = {}
    await mongo_db.update_user(acc)
    return acc


@db.callback_query(F.data == "add_corzin")
async def back_to_main(callback: types.CallbackQuery):
    acc = await create_temp_order(callback.from_user.id)
    logging.info(
        f"пользователь {callback.from_user.username} Добавляет в карзину товар \n"
        f"{show_tofar(acc)} \n и переходит в главное меню")
    await show_main_menu(callback.from_user.id)
    await callback.answer()


@db.callback_query(F.data == "order_zakaz")
async def back_to_main(callback: types.CallbackQuery):
    acc = await create_temp_order(callback.from_user.id)
    logging.info(
        f"пользователь {callback.from_user.username} Добавляет в карзину товар \n"
        f"{show_tofar(acc)} \n и переходит в корзину")
    await show_my_order(callback)


@db.callback_query(F.data == "pay")
async def back_to_main(callback: types.CallbackQuery):
    acc = await mongo_db.get_user(callback.from_user.id)
    acc.order.price = sum(item.price * item.discount for item in acc.order.products)
    acc.order.full_name = acc.full_name
    acc.order.username = acc.username
    acc.order.parallel = acc.parallel
    acc.order.class_name = acc.class_name
    await mongo_db.insert_order(acc.order)
    acc.order = Orders(id=str(uuid4()), product=[])
    await mongo_db.update_user(acc)
    await send_admins(f"🎉 Вам пришёл заказ!", order_admin_menu_kb(), acc)
    logging.info(
        f"пользователь {callback.from_user.username} п в карзину товар \n"
        f"{show_tofar(acc)} \n и переходит в корзину")
    await show_main_menu(callback.from_user.id)


@db.callback_query(F.data.startswith("parallel_"))
async def select_parallel(callback: types.CallbackQuery, state: FSMContext):
    parallel = callback.data.split("_")[1]
    await state.update_data(parallel=parallel)
    await state.set_state(Registration.select_class)
    logging.info(f"пользователь {callback.from_user.username} выбрал параллель {parallel}")
    await send_or_edit_menu(
        callback.from_user.id,
        f"Выбрана параллель {parallel}. Теперь выберите класс:",
        classes_kb(parallel=parallel, parallels=parallels)
    )
    await callback.answer()


@db.callback_query(F.data.startswith("class_"))
async def select_class(callback: types.CallbackQuery, state: FSMContext):
    class_name = callback.data.split("_")[1]
    await state.update_data(class_name=class_name)
    await state.set_state(Registration.enter_fio)
    await send_or_edit_menu(
        callback.from_user.id,
        "Введите ФИО, (Не допускайте ошибок, пример: Иван Иванович Иванов):",
        InlineKeyboardBuilder().button(text="❌ Отмена", callback_data="back_to_parallels").as_markup()
    )
    logging.info(f"пользователь {callback.from_user.username} Вводит Фио")
    await callback.answer()


@db.callback_query(F.data == "Technical_support")
async def support(callback: types.CallbackQuery, state: FSMContext):
    logging.info(f"пользователь {callback.from_user.username} нажал на тех-поддержку")
    await start_help(callback.from_user.id, state)
    await callback.answer()


@db.callback_query(F.data == "_")
async def error(callback: types.CallbackQuery):
    await callback.answer()
    text = (
        "🌟 Функция в разработке 😓...\n"
        "Но вы можете перейти к тестированию других функций"
    )
    await send_or_edit_menu(callback.from_user.id, text, error_menu_kb())


@db.callback_query(F.data.startswith("paralleledit_"))
async def edit_parallel(callback: types.CallbackQuery, state: FSMContext):
    parallel = callback.data.split("_")[1]
    account = await mongo_db.get_user(callback.from_user.id)
    account.parallel = parallel
    logging.info(f"пользователь {callback.from_user.username} изменил параллель своего аккаунта на {parallel}")
    await mongo_db.update_user(account)
    await state.clear()
    await callback.message.answer("✅ Параллель успешно изменена!")
    await callback.answer()
    await show_main_menu(callback.from_user.id)


@db.callback_query(F.data.startswith("edit_"))
async def start_edit_account(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    action = callback.data
    logging.info(f"пользователь {callback.from_user.username} изменяет аккаунт")
    if action == "edit_fio":
        logging.info(f"пользователь {callback.from_user.username} изменяет ФИО")
        await state.set_state(EditAccount.edit_fio)
        await send_or_edit_menu(
            user_id,
            "Введите новое ФИО:",
            InlineKeyboardBuilder().button(text="⬅️ Назад", callback_data="main_menu").as_markup()
        )
    elif action == "edit_parallel":
        logging.info(f"пользователь {callback.from_user.username} изменяет паралель")
        await state.set_state(EditAccount.edit_parallel)
        await send_or_edit_menu(
            user_id,
            "Выберите новую параллель:",
            parallels_kb_edit(parallels)
        )
    elif action == "edit_class":
        logging.info(f"пользователь {callback.from_user.username} изменяет класс")
        await state.set_state(EditAccount.edit_class)
    await callback.answer()



@db.callback_query(F.data.startswith("answer_"))
async def send_answer(callback: types.CallbackQuery):
    id_ = int(callback.data.split("_")[1])
    await send_or_edit_menu(
        id_,
        f"Вам п️р️и️ш️л️о️ сообщение от администрации в {datetime.date.today()}!\n{callback.data.split("_")[2]}",
        InlineKeyboardBuilder().button(text="⬅️ В главное меню", callback_data="main_menu").as_markup()
    )
    logging.info(f"пользователь {callback.from_user.username} получмл ответ")
    await callback.answer()


async def main():
    logging.info(f"Бот запущен")
    db.include_router(object_handlers.router)
    db.include_router(helps_handlers.router)
    db.include_router(account_handlers.router)
    db.include_router(states_handlers.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await db.start_polling(bot)


if __name__ == "__main__":
    logging.info(f"Программа запущена")
    asyncio.run(main())
