import logging
from uuid import uuid4

from aiogram import Bot
from aiogram.dispatcher import router
from aiogram.fsm.context import FSMContext

import config
from DB.db import DB
from dob_func.price import calculating_the_price
from keyboards.keyboard import help_menu_kb, support_menu_kb, parallels_kb, orders_admin_menu_kb, korzin_null, \
    order_kb_show, predmet_menu_kb, main_menu_kb, orders_menu_kb, Technical_support_menu_kb
from model.User import User
from model.order import Orders
from model.reqwest import Reqwest
from model.temp_Order import Temp_order
from states.states import Support, Registration

bot = Bot(token=config.BOT_TOKEN)
user_menu_messages = {}

mongo_db = DB(config.MONGO_DB_URL, "login")
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


async def create_temp_order(user_id: int):
    acc = await mongo_db.get_user(user_id)
    temp_order = Temp_order(id=str(uuid4()), object=acc.temp_order["предмет"], quarter=acc.temp_order["Четверть"],
                            type=acc.temp_order["Тип оценки"], estimation=acc.temp_order["Оценка"], price=int(
            calculating_the_price({acc.temp_order["Тип оценки"]: {"1 Оценка": 0,
                                                                  "2 Оценка": acc.temp_order["Оценка"],
                                                                  "предмет": acc.temp_order["предмет"]}})))
    acc.order.products.append(temp_order)
    acc.temp_order = {}
    await mongo_db.update_user(acc)
    acc = await mongo_db.get_user(user_id)
    return acc


async def show_orders_menu(router: router, user_id: int, start=0):
    logging.info(f"админ {user_id} открыл меню заказов")
    orders = await mongo_db.get_all_orders()
    orders = list(Orders(**i) for i in orders)[::-1]
    text = (
        "🌟 Заказы:\n\n"
        "Здесь вы можете управлять заказами\n"
        f"Активных заказов: {len(orders)}"
    )
    await send_or_edit_menu(router, user_id, text, orders_menu_kb(orders, start))


async def Technical_support_orders_menu(bot: router, user_id: int, start=0):
    logging.info(f"админ {user_id} открыл меню заказов")
    orders = await mongo_db.get_all_reqwest()
    orders = list(Reqwest(**i) for i in orders)[::-1]
    text = (
        "🌟 Обращения:\n\n"
        "Здесь вы можете отвечать на обращения\n"
        f"Активных Обращений: {len(orders)}"
    )
    await send_or_edit_menu(bot, user_id, text, Technical_support_menu_kb(orders, start))


async def show_order(bot: router, user_id: int):
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
            f"📙 Вы можете удалить или изменить ваши товары\n============\n{"\n --------------------".join(a)}"
            f"============\n Общая цена заказа {b} рублей ₽"
        )
        logging.info(f"у пользователя {user_id} корзина:{"\n -------------------- \n".join(a)}")
        await send_or_edit_menu(bot, user_id, text, order_kb_show(acc))
    else:
        text = (
            "🎉 Здравствуйте! Это ваша корзина\n"
            f"📙 Корзина пока пуста.. Желаете перейти к покупкам?\n"
        )
        logging.info(f"у пользователя {user_id} пустая корзина")
        await send_or_edit_menu(bot, user_id, text, korzin_null())


async def show_client_order(bot: router, order: Orders, admin_id):
    logging.info(f"Админ {admin_id} Смотрит корзину пользователя {order.username} - {order.id}")
    a = list()
    b = 0.00
    for number, i in enumerate(order.products):
        a.append(
            str(f"Товар №{int(number) + 1} : \n {show_orders(order, number)}"))
        b = float(sum(list(order.products[number].price for number, i in enumerate(order.products))))
    text = (
        "🎉 Здравствуйте! Это ваша корзина\n"
        f"📙 Вы можете удалить или изменить ваши товары\n============\n{"--------------------\n".join(a)}"
        f"============\n Общая цена заказа {b} рублей ₽"
    )
    await send_or_edit_menu(bot, admin_id, text, orders_admin_menu_kb())


async def show_client_reqwest(bot: router, order: Reqwest, admin_id):
    logging.info(f"Админ {admin_id} Смотрит корзину пользователя {order.username} - {order.user_id}")
    text = (
        f"🎉 Здравствуйте! Это Запрос от {order.username}\n"
        f"📙 Время - {order.datetime}. Тип - {order.type}\n{order.messages}"
    )
    await send_or_edit_menu(bot, admin_id, text, orders_admin_menu_kb())


async def send_admins(bot: router, text: str, keyboard, user: User):
    admins = await mongo_db.get_admins()
    for admin in admins:
        await send_or_edit_menu(bot, admin.id,
                                f"Пользователь {user.username} - {user.id} Отправил запрос:\n{text.capitalize()}",
                                keyboard)


async def send_or_edit_menu(bot: router, user_id: int, text: str, keyboard):
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


def show_orders(acc: Orders, _id=-1):
    return (f"ID - {acc.products[_id].id[:8]}\n"
            f"Тип оценки - {acc.products[_id].type}\n"
            f"Четверть - {acc.products[_id].quarter}\n"
            f"Предмет - {acc.products[_id].object}\n"
            f"Оценка - {acc.products[_id].estimation}\n"
            f"Цена - {acc.products[_id].price}\n")


async def show_main_menu(bot: router, user_id: int):
    logging.info(f"пользователь {user_id} открыл главное меню")
    text = (
        "🌟 Главное меню:\n\n"
        "Здесь вы можете управлять своими аккаунтами, "
        "настраивать параметры и получать помощь."
    )
    acc = await mongo_db.get_user(user_id)
    await send_or_edit_menu(bot, user_id, text, main_menu_kb(acc))


async def start_help(bot: router, user_id: int, state: FSMContext):
    logging.info(f"пользователь {user_id} начал тех-поддержку")
    await state.set_state(Support.message)
    await send_or_edit_menu(bot,
        user_id,
        "Введите сообщение тех поддержке",
        support_menu_kb()
    )


async def show_predmets_menu(bot: router, user_id: int):
    logging.info(f"пользователь {user_id} открыл меню выбора предмета")
    text = (
        "🎉 Здравствуйте! Вот список ваших предметов "
        "📙 Выберите Предмет из доступных"
    )
    account: User = await mongo_db.get_user(user_id)
    await send_or_edit_menu(bot, user_id, text, predmet_menu_kb(parallels=parallels, paralell=str(account.parallel)))


async def start_registration(bot: router, user_id: int, state: FSMContext):
    logging.info(f"пользователь {user_id} начал регистрацию")
    await state.set_state(Registration.select_parallel)
    await send_or_edit_menu(bot,
        user_id,
        "📚 Выберите параллель:",
        parallels_kb(parallels)
    )


async def help_menu(bot: router, user_id: int):
    logging.info(f"пользователь {user_id} открыл меню помощи")
    text = (
        "❔ Выберите интересующий вас раздел"
    )
    await send_or_edit_menu(bot, user_id, text, help_menu_kb())


async def help_1_menu(bot: router, user_id: int):
    logging.info(f"пользователь {user_id} открыл меню помощи")
    text = (
        "оплата"
    )
    await send_or_edit_menu(bot, user_id, text, help_menu_kb())


async def help_2_menu(bot: router, user_id: int):
    logging.info(f"пользователь {user_id} открыл меню помощи")
    text = (
        "❔ цена"
    )
    await send_or_edit_menu(bot, user_id, text, help_menu_kb())


async def help_3_menu(bot: router, user_id: int):
    logging.info(f"пользователь {user_id} открыл меню помощи")
    text = (
        "❔ безопасность"
    )
    await send_or_edit_menu(bot, user_id, text, help_menu_kb())


async def help_4_menu(bot: router, user_id: int):
    logging.info(f"пользователь {user_id} открыл меню помощи")
    text = (
        "❔ гарантии"
    )
    await send_or_edit_menu(bot, user_id, text, help_menu_kb())
