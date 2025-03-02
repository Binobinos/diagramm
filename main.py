import asyncio
import datetime
from uuid import uuid4

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from model.reqwest import Reqwest
import config
from DB.db import DB
from keyboards.keyboard import *
from model.temp_Order import Temp_order
from states.states import Registration, EditAccount, Support

bot = Bot(token=config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

mongo_db = DB(config.MONGO_DB_URL, "login")
user_menu_messages = {}
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

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

async def send_admins(text: str, keyboard, user: User):
    admins = await mongo_db.get_admins()
    for admin in admins:
        await send_or_edit_menu(admin.id,
                                f"Пользователь {user.username} - {user.id} Отправил запрос:\n{text.capitalize()}",
                                keyboard)


def show_acc(acc: User):
    return (f"Имя - {acc.full_name.capitalize()}\nКласс - {acc.parallel} {acc.class_name}\nБаланс - "
            f"{acc.balance}₽\nУровень аккаунта - {acc.desired_rating}")


def show_tofar(acc: User, _id=-1):
    return (f"ID - {acc.order.products[_id].id[:8]}\n"
            f"Тип оценки - {acc.order.products[_id].type}\n"
            f"Четверть - {acc.order.products[_id].quarter}\n"
            f"Предмет - {acc.order.products[_id].object}\n"
            f"Оценка - {acc.order.products[_id].estimation}\n"
            f"Цена - {acc.order.products[_id].price}\n")


async def show_main_menu(user_id: int):
    logging.info(f"пользователь {user_id} открыл главное меню")
    text = (
        "🌟 Главное меню:\n\n"
        "Здесь вы можете управлять своими аккаунтами, "
        "настраивать параметры и получать помощь."
    )
    acc = await mongo_db.get_user(user_id)
    await send_or_edit_menu(user_id, text, main_menu_kb(acc))


async def show_predmets_menu(user_id: int):
    logging.info(f"пользователь {user_id} открыл меню выбора предмета")
    text = (
        "🎉 Здравствуйте! Вот список ваших предметов "
        "📙 Выберите Предмет из доступных"
    )
    account: User = await mongo_db.get_user(user_id)
    await send_or_edit_menu(user_id, text, predmet_menu_kb(parallels=parallels, paralell=str(account.parallel)))


async def show_order(user_id: int):
    logging.info(f"пользователь {user_id} открыл корзину")
    a = list()
    acc = await mongo_db.get_user(user_id)
    b = 0.00
    for number, i in enumerate(acc.order.products):
        a.append(
            str(f"Товар №{int(number) + 1} : \n {show_tofar(acc, number)}"))
        b = float(sum(list(acc.order.products[number].price for number, i in enumerate(acc.order.products))))
    if acc.order.products:
        text = (
            "🎉 Здравствуйте! Это ваша корзина\n"
            f"📙 Вы можете удалить или изменить ваши товары\n============\n{"\n -------------------- \n".join(a)}\n"
            f"\n============\n Общая цена заказа {b} рублей ₽"
        )
        logging.info(f"у пользователя {user_id} корзина:\n{"\n -------------------- \n".join(a)}")
        await send_or_edit_menu(user_id, text, order_kb_show(acc))
    else:
        text = (
            "🎉 Здравствуйте! Это ваша корзина\n"
            f"📙 Корзина пока пуста.. Желаете перейти к покупкам?\n"
        )
        logging.info(f"у пользователя {user_id} пустая корзина")
        await send_or_edit_menu(user_id, text, korzin_null())


async def send_or_edit_menu(user_id: int, text: str, keyboard):
    try:
        if user_id in user_menu_messages:
            await bot.edit_message_text(
                chat_id=user_id,
                message_id=user_menu_messages[user_id],
                text=text,
                reply_markup=keyboard
            )
        else:
            msg = await bot.send_message(user_id, text, reply_markup=keyboard)
            user_menu_messages[user_id] = msg.message_id
    except Exception:
        msg = await bot.send_message(user_id, text, reply_markup=keyboard)
        user_menu_messages[user_id] = msg.message_id


async def start_registration(user_id: int, state: FSMContext):
    logging.info(f"пользователь {user_id} начал регистрацию")
    await state.set_state(Registration.select_parallel)
    await send_or_edit_menu(
        user_id,
        "📚 Выберите параллель:",
        parallels_kb(parallels)
    )


async def start_help(user_id: int, state: FSMContext):
    logging.info(f"пользователь {user_id} начал тех-поддержку")
    await state.set_state(Support.message)
    await send_or_edit_menu(
        user_id,
        "Введите сообщение тех поддержке",
        support_menu_kb()
    )


# Обработчики
@dp.message(Command("start"))
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


@dp.callback_query(F.data == "order")
async def show_my_order(callback: types.CallbackQuery):
    logging.info(f"пользователь {callback.from_user.username} открыл корзиину")
    await show_order(callback.from_user.id)
    await callback.answer()


async def show_orders_menu(user_id: int, start=0):
    logging.info(f"админ {user_id} открыл меню заказов")
    orders = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    text = (
        "🌟 Заказы:\n\n"
        "Здесь вы можете управлять заказами\n"
        f"Активных заказов: {len(orders)}"
    )
    await send_or_edit_menu(user_id, text, orders_menu_kb(orders, start))


@dp.callback_query(F.data.startswith("Orders_"))
async def start_create_account(callback: types.CallbackQuery):
    start = int(callback.data.split("_")[1])
    logging.info(f"Админ {callback.from_user.username} переходит в заказы c {start}")
    await show_orders_menu(callback.from_user.id, start)


"""
                Помощь и её меню

"""


@dp.callback_query(F.data == "help")
async def help_(callback: types.CallbackQuery):
    logging.info(f"пользователь {callback.from_user.username} открыл справку")
    await help_menu(callback.from_user.id)
    await callback.answer()


@dp.callback_query(F.data == "help_1")
async def help_1(callback: types.CallbackQuery):
    logging.info(f"пользователь {callback.from_user.username} открыл справку")
    await help_1_menu(callback.from_user.id)
    await callback.answer()


@dp.callback_query(F.data == "help_2")
async def help_2(callback: types.CallbackQuery):
    logging.info(f"пользователь {callback.from_user.username} открыл справку")
    await help_2_menu(callback.from_user.id)
    await callback.answer()


@dp.callback_query(F.data == "help_3")
async def help_3(callback: types.CallbackQuery):
    logging.info(f"пользователь {callback.from_user.username} открыл справку")
    await help_3_menu(callback.from_user.id)
    await callback.answer()


@dp.callback_query(F.data == "help_4")
async def help_4(callback: types.CallbackQuery):
    logging.info(f"пользователь {callback.from_user.username} открыл справку")
    await help_4_menu(callback.from_user.id)
    await send_admins("тест отправки всем админам", help_menu_kb())
    await callback.answer()


async def help_menu(user_id: int):
    logging.info(f"пользователь {user_id} открыл меню помощи")
    text = (
        "❔ Выберите интересующий вас раздел"
    )
    await send_or_edit_menu(user_id, text, help_menu_kb())


async def help_1_menu(user_id: int):
    logging.info(f"пользователь {user_id} открыл меню помощи")
    text = (
        "оплата"
    )
    await send_or_edit_menu(user_id, text, help_menu_kb())


async def help_2_menu(user_id: int):
    logging.info(f"пользователь {user_id} открыл меню помощи")
    text = (
        "❔ цена"
    )
    await send_or_edit_menu(user_id, text, help_menu_kb())


async def help_3_menu(user_id: int):
    logging.info(f"пользователь {user_id} открыл меню помощи")
    text = (
        "❔ безопасность"
    )
    await send_or_edit_menu(user_id, text, help_menu_kb())


async def help_4_menu(user_id: int):
    logging.info(f"пользователь {user_id} открыл меню помощи")
    text = (
        "❔ гарантии"
    )
    await send_or_edit_menu(user_id, text, help_menu_kb())


"""


"""


@dp.callback_query(F.data == "my_accounts")
async def show_account(callback: types.CallbackQuery):
    """
    Отображение информации об аккаунте
    :param callback: Функция Вызова телеграмма
    :return: None
    """
    user_id = callback.from_user.id
    acc: User = await mongo_db.get_user(user_id)
    logging.info(f"пользователь {callback.from_user.username} нажал на аккаунт {show_acc(acc)}")
    text = (
        f"🔍 Информация об аккаунте:\n\n"
        f"{show_acc(acc)}\n\n"
        "Выберите действие:"
    )

    await send_or_edit_menu(
        user_id,
        text,
        edit_account_kb()
    )
    await callback.answer()


@dp.callback_query(F.data == "create_account")
async def start_create_account(callback: types.CallbackQuery, state: FSMContext):
    logging.info(f"пользователь {callback.from_user.username} начала регистрацию")
    await start_registration(callback.from_user.id, state)
    await callback.answer()


@dp.callback_query(F.data == "delete_account")
async def start_create_account(callback: types.CallbackQuery, state: FSMContext):
    logging.info(f"пользователь {callback.from_user.username} удаляет аккаунт")
    acc = await mongo_db.get_user(callback.from_user.id)
    await mongo_db.delete_user(acc)
    await start_registration(callback.from_user.id, state)
    del user_menu_messages[callback.from_user.id]
    await callback.message.answer("Аккаунт удалён")


@dp.callback_query(F.data == "cancel")
async def cancel_registration(callback: types.CallbackQuery, state: FSMContext):
    logging.info(f"пользователь {callback.from_user.username} отменил регистрацию")
    await state.clear()
    await show_main_menu(callback.from_user.id)
    await callback.answer("Регистрация отменена")


@dp.callback_query(F.data == "back_to_parallels")
async def back_to_parallels(callback: types.CallbackQuery, state: FSMContext):
    logging.info(f"пользователь {callback.from_user.username} Вернулся к паралелям")
    await state.set_state(Registration.select_parallel)
    await send_or_edit_menu(
        callback.from_user.id,
        "Выберите параллель:",
        parallels_kb(parallels)
    )
    await callback.answer()


@dp.callback_query(F.data == "main_menu")
async def back_to_main(callback: types.CallbackQuery):
    logging.info(f"пользователь {callback.from_user.username} переходит в главное меню")
    await show_main_menu(callback.from_user.id)
    await callback.answer()


@dp.callback_query(F.data == "add_corzin")
async def back_to_main(callback: types.CallbackQuery):
    acc = await mongo_db.get_user(callback.from_user.id)
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
    logging.info(
        f"пользователь {callback.from_user.username} Добавляет в карзину товар \n"
        f"{show_tofar(acc)} \n и переходит в главное меню")
    await show_main_menu(callback.from_user.id)
    await callback.answer()


@dp.callback_query(F.data == "order_zakaz")
async def back_to_main(callback: types.CallbackQuery):
    acc = await mongo_db.get_user(callback.from_user.id)
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
    logging.info(
        f"пользователь {callback.from_user.username} Добавляет в карзину товар \n"
        f"{show_tofar(acc)} \n и переходит в корзину")
    await show_my_order(callback)


@dp.callback_query(F.data == "pay")
async def back_to_main(callback: types.CallbackQuery):
    acc = await mongo_db.get_user(callback.from_user.id)
    acc.order.price = sum(item.price * item.discount for item in acc.order.products)
    acc.order.discount = map(lambda x: sum(x) / len(x), list(item.price * item.discount for item in acc.order.products))
    await mongo_db.update_user(acc)
    logging.info(
        f"пользователь {callback.from_user.username} п в карзину товар \n"
        f"{show_tofar(acc)} \n и переходит в корзину")
    await show_main_menu(callback.from_user.id)


# Выбор предмета
@dp.callback_query(F.data == "my_predmet")
async def show_my_predmet(callback: types.CallbackQuery):
    logging.info(f"пользователь {callback.from_user.username} открыл меню выбора предмета")
    await show_predmets_menu(callback.from_user.id)
    await callback.answer()


@dp.callback_query(F.data.startswith("predmet_"))
async def show_account(callback: types.CallbackQuery):
    """
    Выбор Четверти
    :param callback: None
    :return: None
    """
    user_id = callback.from_user.id
    predmets = callback.data.split("_")[1]
    acc = await mongo_db.get_user(user_id)
    acc.temp_order["предмет"] = predmets
    await mongo_db.update_user(acc)
    text = (
        f"Вы выбрали {predmets}\n"
        "Выберите Четверть:"
    )
    logging.info(f"пользователь {callback.from_user.username} выбрал предмет {predmets}")
    await send_or_edit_menu(
        user_id,
        text,
        accounts_cht_kb()
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("CHT_"))
async def show_type(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    predmets = callback.data.split("_")[1]
    acc = await mongo_db.get_user(user_id)
    acc.temp_order["Четверть"] = predmets
    await mongo_db.update_user(acc)
    text = (
        f"Вы выбрали {predmets}-ую Четверть"
        "\nВыберите Тип Оценки:"
    )
    logging.info(f"пользователь {callback.from_user.username} выбрал четверть {predmets}")
    await send_or_edit_menu(
        user_id,
        text,
        accounts_type_kb(type_items)
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("tip_"))
async def show_account_(callback: types.CallbackQuery):
    """
    Выбор Четверти
    :param callback: None
    :return: None
    """
    user_id = callback.from_user.id
    predmets = callback.data.split("_")[1]
    acc = await mongo_db.get_user(user_id)
    acc.temp_order["Тип оценки"] = predmets
    await mongo_db.update_user(acc)
    text = (
        f"Вы выбрали {predmets}\n"
        "Выберите Оценку:"
    )
    logging.info(f"пользователь {callback.from_user.username} выбрал тип оценки {predmets}")
    await send_or_edit_menu(
        user_id,
        text,
        accounts_tip_o_kb(acc)
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("type_"))
async def select_class(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    predmets = callback.data.split("_")[1]
    acc = await mongo_db.get_user(user_id)
    acc.temp_order["Оценка"] = predmets
    logging.info(f"пользователь {callback.from_user.username} выбрал оценку {predmets}")
    await mongo_db.update_user(acc)
    acc = await mongo_db.get_user(user_id)
    temp_order = Temp_order(id=str(uuid4()), object=acc.temp_order["предмет"], quarter=acc.temp_order["Четверть"],
                            type=acc.temp_order["Тип оценки"], estimation=acc.temp_order["Оценка"], price=int(
            calculating_the_price({acc.temp_order["Тип оценки"]: {"1 Оценка": 0, "2 Оценка": acc.temp_order["Оценка"],
                                                                  "предмет": acc.temp_order["предмет"]}})))
    acc.order.products.append(temp_order)
    acc.temp_order = {}
    text = (
        f"🔍 Информация об Заказе:\n\nФИО - {acc.full_name}\nКласс - {acc.parallel} {acc.class_name}\n{show_tofar(acc)}"
        "\nВсё верно?"
    )
    logging.info(f"пользователь {callback.from_user.username} подтверждает товар")
    await send_or_edit_menu(
        user_id,
        text,
        edit_zacaz_kb()
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("parallel_"))
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


@dp.callback_query(F.data.startswith("paralleledit_"))
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


@dp.callback_query(F.data.startswith("class_"))
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


@dp.callback_query(F.data.startswith("edit_"))
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


@dp.callback_query(F.data.startswith("answer_"))
async def send_answer(callback: types.CallbackQuery):
    id_ = int(callback.data.split("_")[1])
    await send_or_edit_menu(
        id_,
        f"Вам п️р️и️ш️л️о️ сообщение от администрации в {datetime.date.today()}!\n{callback.data.split("_")[2]}",
        InlineKeyboardBuilder().button(text="⬅️ В главное меню", callback_data="main_menu").as_markup()
    )
    logging.info(f"пользователь {callback.from_user.username} получмл ответ")
    await callback.answer()


@dp.message(Registration.enter_fio)
async def enter_fio(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    fio = message.text.strip().lower()

    if len(fio.split()) != 3:
        await message.answer("Введите полное ФИО ")
        logging.info(f"пользователь {message.from_user.username} ввёл неверное ФИО")
        return
    for i in fio.split():
        if len(i) < 2:
            await message.answer("ФИО должно быть длиннее одной буквы")
            logging.info(f"пользователь {message.from_user.username} ввёл неверное ФИО меньше двух букв")
            return
        for j in i:
            if not j.lower() in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя":
                await message.answer("ФИО должно содержать Только Буквы")
                logging.info(f"пользователь {message.from_user.username} ввёл неверное ФИО не русские буквы")
                return

    data = await state.get_data()
    acc_ = await mongo_db.get_user_fio(fio)
    if acc_ is None:
        await mongo_db.insert_user(
            User(id=user_id, username=message.from_user.username, full_name=fio, parallel=data["parallel"],
                 class_name=data["class_name"].split()[1]))
        acc = await mongo_db.get_user(user_id)
        await state.clear()
        await message.answer("✅ Аккаунт успешно создан!")
        logging.info(f"пользователь {message.from_user.username} создал аккаунт\n {acc.model_dump()}")
        await show_main_menu(user_id)
    else:
        await message.answer("❌Такой аккаунт уже есть")
        logging.info(f"пользователь {message.from_user.username} пытается войти в аккаунт \n{acc_.model_dump()}")
        await state.set_state(EditAccount.edit_class)
        data = await state.get_data()
        await send_or_edit_menu(
            user_id,
            "Выберите новый класс:",
            classes_kb(parallels=parallels, parallel=data['parallel'])
        )


@dp.message(EditAccount.edit_fio)
async def edit_fio(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    fio = message.text.strip().lower()  # Убираем лишние пробелы по краям
    parts = fio.split()
    if len(parts) != 3:
        await message.answer("Введите полное ФИО в формате 'Фамилия Имя Отчество'.")
        logging.info(f"пользователь {message.from_user.username} ввёл неправильно ФИО")
        return

    surname, name, patronymic = parts

    if not len(surname) >= 2 and not len(name) >= 2 and not len(patronymic) >= 2:
        await message.answer("ФИО должно содержать только буквы кириллицы и дефисы.")
        logging.info(f"пользователь {message.from_user.username} ввёл неправильно ФИО")
        return

    account = await mongo_db.get_user(user_id)
    account.full_name = fio
    await mongo_db.update_user(account)
    await state.clear()
    await message.answer("✅ ФИО успешно изменено!")
    logging.info(f"пользователь {message.from_user.username} изменил ФИО на {fio}")
    await show_main_menu(user_id)


@dp.message(Support.message)
async def edit_fio(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    messages = message.text.strip()
    acc = await mongo_db.get_user(user_id)
    logging.info(f"пользователь {message.from_user.username} отправил сообщение тех поддержке:\n{messages}")
    request = Reqwest(id_=str(uuid4())[:8],user_id=user_id,username=message.from_user.username,)
    await message.answer("✅ Сообщение успешно отправленною")
    await state.clear()
    await send_admins(f"{datetime.date.today()} - {messages}", support_admin_menu_kb(user_id), acc)
    # await show_main_menu(user_id)


@dp.callback_query(F.data == "Technical_support")
async def support(callback: types.CallbackQuery, state: FSMContext):
    logging.info(f"пользователь {callback.from_user.username} нажал на тех-поддержку")
    await start_help(callback.from_user.id, state)
    await callback.answer()


async def main():
    logging.info(f"Бот запущен")
    print(datetime.date.today())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.info(f"Программа запущена")
    asyncio.run(main())
