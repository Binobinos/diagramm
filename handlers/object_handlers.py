from dob_func.dob_func import *
from aiogram import Router, types
router = Router()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

@router.callback_query(F.data == "my_predmet")
async def show_my_predmet(callback: types.CallbackQuery):
    logging.info(f"пользователь {callback.from_user.username} открыл меню выбора предмета")
    await show_predmets_menu(callback.from_user.id)
    await callback.answer()


@router.callback_query(F.data.startswith("predmet_"))
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


@router.callback_query(F.data.startswith("CHT_"))
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


@router.callback_query(F.data.startswith("tip_"))
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


@router.callback_query(F.data.startswith("type_"))
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
