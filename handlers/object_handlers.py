from aiogram import Router, F
from aiogram import types

from func.dob_func_ import *
from func.prices import calculating_the_price
from keyboards.keyboard import accounts_cht_kb, accounts_type_kb, accounts_tip_o_kb, edit_zacaz_kb
from model.temp_order import TempOrder

router = Router()
logging.basicConfig(level=config.LOGGING_LEVEL, format="%(asctime)s %(levelname)s %(message)s")
type_items = {"Работа на уроке": 1, "Самостоятельная работа": 1.04, "Проверочная работа": 1.05,
              "Контрольная работа": 1.06}


@router.callback_query(F.data == "my_predmet")
async def show_my_object(callback: types.CallbackQuery):
    logging.info(f"пользователь {callback.from_user.username} открыл меню выбора предмета")
    await show_object_menu(callback.from_user.id)
    await callback.answer()


@router.callback_query(F.data.startswith("predmet_"))
async def show_account(callback: types.CallbackQuery):
    """
    Выбор Четверти
    :param callback: Nots
    :return: Nots
    """
    user_id = callback.from_user.id
    object = callback.data.split("_")[1]
    acc = await mongo_db.get_user(user_id)
    acc.temp_order["предмет"] = object
    await mongo_db.update_user(acc)
    text = (
        f"Вы выбрали {object}\n"
        "Выберите Четверть:"
    )
    logging.info(f"пользователь {callback.from_user.username} выбрал предмет {object}")
    await send_or_edit_menu(user_id, text, accounts_cht_kb())
    await callback.answer()


@router.callback_query(F.data.startswith("CHT_"))
async def type_assessment(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    quarter = callback.data.split("_")[1]
    acc = await mongo_db.get_user(user_id)
    acc.temp_order["Четверть"] = quarter
    await mongo_db.update_user(acc)
    text = (
        f"Вы выбрали {quarter}-ую Четверть\n"
        "Выберите Тип Оценки:"
    )
    logging.info(f"пользователь {callback.from_user.username} выбрал четверть {quarter}")
    await send_or_edit_menu(user_id, text, accounts_type_kb(type_items))
    await callback.answer()


@router.callback_query(F.data.startswith("tip_"))
async def choosing_evaluations(callback: types.CallbackQuery):
    """
    Выбор Четверти
    :param callback: Nots
    :return: Nots
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
    await send_or_edit_menu(user_id, text, accounts_tip_o_kb(acc))
    await callback.answer()


@router.callback_query(F.data.startswith("type_"))
async def select_class(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    predmets = callback.data.split("_")[1]
    acc = await mongo_db.get_user(user_id)
    acc.temp_order["Оценка"] = predmets
    logging.info(f"пользователь {callback.from_user.username} выбрал оценку {predmets}")
    await mongo_db.update_user(acc)
    acc = await mongo_db.get_user(user_id)
    temp_order = TempOrder(id=str(uuid4()), object=acc.temp_order["предмет"], quarter=acc.temp_order["Четверть"],
                           type=acc.temp_order["Тип оценки"], estimation=acc.temp_order["Оценка"], price=int(
            calculating_the_price({acc.temp_order["Тип оценки"]: {"1 Оценка": 0, "2 Оценка": acc.temp_order["Оценка"],
                                                                  "предмет": acc.temp_order["предмет"]}})))
    acc.order.products.append(temp_order)
    acc.temp_order = {}
    text = (
        f"🔍 Информация об Заказе:\n\n"
        f"ФИО - {acc.full_name}\n"
        f"Класс - {acc.parallel} {acc.class_name}\n"
        f"{show_product(acc)}\n"
        "Всё верно?"
    )
    logging.info(f"пользователь {callback.from_user.username} подтверждает товар")
    await send_or_edit_menu(user_id, text, edit_zacaz_kb())
    await callback.answer()
