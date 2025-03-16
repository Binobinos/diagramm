from aiogram import Router, F
from aiogram import types

from dob_func.dob_func import *
from keyboards.keyboard import order_admin_menu_kb
from model.order import Orders

router = Router()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
type_items = {"Работа на уроке": 1, "Самостоятельная работа": 1.04, "Проверочная работа": 1.05,
              "Контрольная работа": 1.06}


@router.callback_query(F.data == "order")
async def show_my_order(callback: types.CallbackQuery):
    logging.info(f"пользователь {callback.from_user.username} открыл корзиину")
    await show_order(callback.from_user.id)
    await callback.answer()


@router.callback_query(F.data.startswith("*order-new_"))
async def show_admin_order(callback: types.CallbackQuery):
    logging.info(f"пользователь {callback.from_user.username} открыл корзиину")
    ids = callback.data.split('_')[1]
    order = await mongo_db.get_order(ids)
    await show_client_order(order, callback.from_user.id)
    await callback.answer()


@router.callback_query(F.data.startswith("Orders_"))
async def start_create_account(callback: types.CallbackQuery):
    start = int(callback.data.split("_")[1])
    logging.info(f"Админ {callback.from_user.username} переходит в заказы c {start}")
    await show_orders_menu(callback.from_user.id, start)


@router.callback_query(F.data.startswith("Technical_support_"))
async def Technical_support_menu(callback: types.CallbackQuery):
    start = int(callback.data.split("_")[2])
    logging.info(f"Админ {callback.from_user.username} переходит в заказы c {start}")
    await Technical_support_orders_menu(callback.from_user.id, start)


@router.callback_query(F.data == "add_corzin")
async def back_to_main(callback: types.CallbackQuery):
    acc = await create_temp_order(callback.from_user.id)
    logging.info(
        f"пользователь {callback.from_user.username} Добавляет в карзину товар \n"
        f"{show_tofar(acc)} \n и переходит в главное меню")
    await show_main_menu(callback.from_user.id)
    await callback.answer()


@router.callback_query(F.data == "order_zakaz")
async def back_to_main(callback: types.CallbackQuery):
    acc = await create_temp_order(callback.from_user.id)
    logging.info(
        f"пользователь {callback.from_user.username} Добавляет в карзину товар \n"
        f"{show_tofar(acc)} \n и переходит в корзину")
    await show_my_order(callback)


@router.callback_query(F.data == "pay")
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
