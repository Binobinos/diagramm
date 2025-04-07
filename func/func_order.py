import logging
from uuid import uuid4

import func.prices as pc
from config import mongo_db
from func.dob_func_ import send_or_edit_menu
from func.func_text import show_product, show_orders
from keyboards.keyboard import order_kb_show, korzin_null, orders_admin_menu_kb, orders_menu_kb, \
    technical_support_menu_kb
from model.order import Orders
from model.reqwest import Reqwest
from model.temp_order import TempOrder


async def create_temp_order(user_id: int):
    acc = await mongo_db.get_user(user_id)
    price_dict = {acc.temp_order["Тип оценки"]: {
        "1 Оценка": 0,
        "2 Оценка": acc.temp_order["Оценка"],
        "предмет": acc.temp_order["предмет"]}}
    price = int(pc.calculating_the_price(price_dict))
    temp_order = TempOrder(id=str(uuid4()),
                           object=acc.temp_order["предмет"],
                           quarter=acc.temp_order["Четверть"],
                           type=acc.temp_order["Тип оценки"],
                           estimation=acc.temp_order["Оценка"],
                           price=price)
    acc.order.products.append(temp_order)
    acc.temp_order = {}
    await mongo_db.update_user(acc)
    acc = await mongo_db.get_user(user_id)
    return acc


async def show_order(user_id: int):
    logging.info(f"пользователь {user_id} открыл корзину")
    a = list()
    acc = await mongo_db.get_user(user_id)
    b = 0.00
    for number, i in enumerate(acc.order.products):
        text = str(f"Товар №{int(number) + 1} : \n {show_product(acc, number)}")
        a.append(text)
        b = float(sum(list(acc.order.products[number].price for number, i in enumerate(acc.order.products))))
    if acc.order.products:
        text = (
            "🎉 Здравствуйте! Это ваша корзина\n"
            f"📙 Вы можете удалить или изменить ваши товары\n============\n{"\n --------------------".join(a)}"
            f"============\n Общая цена заказа {b} рублей ₽"
        )
        logging.info(f"у пользователя {user_id} корзина:{"\n -------------------- \n".join(a)}")
        await send_or_edit_menu(user_id, text, order_kb_show(acc))
    else:
        text = (
            "🎉 Здравствуйте! Это ваша корзина\n"
            f"📙 Корзина пока пуста.. Желаете перейти к покупкам?\n"
        )
        logging.info(f"у пользователя {user_id} пустая корзина")
        await send_or_edit_menu(user_id, text, korzin_null())


async def show_client_order(order: Orders, admin_id):
    logging.info(f"Админ {admin_id} Смотрит корзину пользователя {order.username} - {order.id}")
    a = list()
    b = 0.00
    for number, i in enumerate(order.products):
        text = str(f"Товар №{int(number) + 1} : \n {show_orders(order, number)}")
        a.append(text)
        b = float(sum(list(order.products[number].price for number, i in enumerate(order.products))))
    text = (
        "🎉 Здравствуйте! Это ваша корзина\n"
        f"📙 Вы можете удалить или изменить ваши товары\n============\n{"--------------------\n".join(a)}"
        f"============\n Общая цена заказа {b} рублей ₽"
    )
    await send_or_edit_menu(admin_id, text, orders_admin_menu_kb())


async def show_orders_menu(user_id: int, start=0):
    logging.info(f"админ {user_id} открыл меню заказов")
    orders = await mongo_db.get_all_orders()
    orders = list(Orders(**i) for i in orders)[::-1]
    text = (
        "🌟 Заказы:\n\n"
        "Здесь вы можете управлять заказами\n"
        f"Активных заказов: {len(orders)}"
    )
    await send_or_edit_menu(user_id, text, orders_menu_kb(orders, start))


async def technical_support_orders_menu(user_id: int, start=0):
    logging.info(f"админ {user_id} открыл меню заказов")
    orders = await mongo_db.get_all_reqwest()
    orders = list(Reqwest(**i) for i in orders)[::-1]
    text = (
        "🌟 Обращения:\n\n"
        "Здесь вы можете отвечать на обращения\n"
        f"Активных Обращений: {len(orders)}"
    )
    await send_or_edit_menu(user_id, text, technical_support_menu_kb(orders, start))
