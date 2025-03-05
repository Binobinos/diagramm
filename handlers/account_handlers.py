from aiogram import Router

from main import *

router = Router()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


@router.callback_query(F.data == "my_accounts")
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


@router.callback_query(F.data == "create_account")
async def start_create_account(callback: types.CallbackQuery, state: FSMContext):
    logging.info(f"пользователь {callback.from_user.username} начала регистрацию")
    await start_registration(callback.from_user.id, state)
    await callback.answer()


@router.callback_query(F.data == "delete_account")
async def start_create_account(callback: types.CallbackQuery, state: FSMContext):
    logging.info(f"пользователь {callback.from_user.username} удаляет аккаунт")
    acc = await mongo_db.get_user(callback.from_user.id)
    await mongo_db.delete_user(acc)
    await start_registration(callback.from_user.id, state)
    del user_menu_messages[callback.from_user.id]
    await callback.message.answer("Аккаунт удалён")


@router.callback_query(F.data == "cancel")
async def cancel_registration(callback: types.CallbackQuery, state: FSMContext):
    logging.info(f"пользователь {callback.from_user.username} отменил регистрацию")
    await state.clear()
    await show_main_menu(callback.from_user.id)
    await callback.answer("Регистрация отменена")


@router.callback_query(F.data == "back_to_parallels")
async def back_to_parallels(callback: types.CallbackQuery, state: FSMContext):
    logging.info(f"пользователь {callback.from_user.username} Вернулся к паралелям")
    await state.set_state(Registration.select_parallel)
    await send_or_edit_menu(
        callback.from_user.id,
        "Выберите параллель:",
        parallels_kb(parallels)
    )
    await callback.answer()
