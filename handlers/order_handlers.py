from uuid import uuid4

from aiogram import Router, F
from aiogram import types

from func.dob_func_ import *
from func.func_order import show_client_order, show_orders_menu, technical_support_orders_menu, create_temp_order, \
    show_order
from func.func_text import show_product
from keyboards.keyboard import order_admin_menu_kb
from model.order import Orders

router = Router()
logging.basicConfig(level=config.LOGGING_LEVEL, format="%(asctime)s %(levelname)s %(message)s")

@router.callback_query(F.data == "order")
async def show_my_order(callback: types.CallbackQuery):
    """ Открывает корзину"""
    logging.info(f"пользователь {callback.from_user.username} открыл корзину")
    await show_order(callback.from_user.id)
    await callback.answer()


@router.callback_query(F.data.startswith("*order-new_"))
async def show_admin_order(callback: types.CallbackQuery):
    """ Просмотр корзины пользователя"""
    logging.info(f"пользователь {callback.from_user.username} открыл корзину")
    ids = callback.data.split('_')[1]
    order = await mongo_db.get_order(ids)
    await show_client_order(order, callback.from_user.id)
    await callback.answer()


@router.callback_query(F.data.startswith("Orders_"))
async def admin_show_orders(callback: types.CallbackQuery):
    """ Меню заказов для админов """
    start = int(callback.data.split("_")[1])
    logging.info(f"Админ {callback.from_user.username} переходит в заказы c {start}")
    await show_orders_menu(callback.from_user.id, start)


@router.callback_query(F.data.startswith("Technical_support_"))
async def technical_support_menu(callback: types.CallbackQuery):
    """ Открывает меню заказов администратору """
    start = int(callback.data.split("_")[2])
    logging.info(f"Админ {callback.from_user.username} переходит в заказы c {start}")
    await technical_support_orders_menu(callback.from_user.id, start)


@router.callback_query(F.data.startswith("*Technical-support_"))
async def show_admin_order(callback: types.CallbackQuery):
    """ Открывает корзину пользователя """
    logging.info(f"пользователь {callback.from_user.username} открыл корзину")
    print(callback.data)
    ids = callback.data.split('_')[1]
    order = await mongo_db.get_reqwest(ids)
    print(order)
    await show_client_reqwest(order, callback.from_user.id)
    await callback.answer()


@router.callback_query(F.data == "add_basket")
async def add_basket_main(callback: types.CallbackQuery):
    """ Добавляет товар в корзину и переходит в главное меню """
    acc = await create_temp_order(callback.from_user.id)
    logging.info(
        f"пользователь {callback.from_user.username} Добавляет в корзину товар \n"
        f"{show_product(acc)} \n и переходит в главное меню")
    await show_main_menu(callback.from_user.id)
    await callback.answer()


@router.callback_query(F.data == "Order_show")
async def add_basket_order(callback: types.CallbackQuery):
    """ Добавляет товар в корзину и переходит в корзину """
    acc = await create_temp_order(callback.from_user.id)
    logging.info(
        f"пользователь {callback.from_user.username} Добавляет в корзину товар \n"
        f"{show_product(acc)} \n и переходит в корзину")
    await show_my_order(callback)


@router.callback_query(F.data.lower() == "pay")
async def add_orders(callback: types.CallbackQuery):
    """ Пост-Оплата товара """
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
        f"пользователь {callback.from_user.username} оплачивает товар \n"
        f"{show_product(acc)}")
    await show_main_menu(callback.from_user.id)
