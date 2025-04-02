from aiogram import Router, F
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from dob_func.dob_func import *
from keyboards.keyboard import classes_kb, parallels_kb_edit, parallels_kb, edit_account_kb
from main import *
from model.User import User
from states.states import Registration, EditAccount

router = Router()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


@router.callback_query(F.data == "my_accounts")
async def show_account(callback: types.CallbackQuery, router: Router):
    """
    Отображение информации об аккаунте
    :param callback: Функция Вызова телеграмма
    :return: Nots
    """
    user_id = callback.from_user.id
    acc: User = await mongo_db.get_user(user_id)
    logging.info(f"пользователь {callback.from_user.username} нажал на аккаунт {show_acc(acc)}")
    text = (
        f"🔍 Информация об аккаунте:\n\n"
        f"{show_acc(acc)}\n\n"
        "Выберите действие:"
    )

    await send_or_edit_menu(router,
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
async def back_to_parallels(callback: types.CallbackQuery, state: FSMContext,router:Router):
    logging.info(f"пользователь {callback.from_user.username} Вернулся к паралелям")
    await state.set_state(Registration.select_parallel)
    await send_or_edit_menu(router,
        callback.from_user.id,
        "Выберите параллель:",
        parallels_kb(parallels)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("paralleledit_"))
async def edit_parallel(callback: types.CallbackQuery, state: FSMContext,router:Router):
    parallel = callback.data.split("_")[1]
    account = await mongo_db.get_user(callback.from_user.id)
    account.parallel = parallel
    logging.info(f"пользователь {callback.from_user.username} изменил параллель своего аккаунта на {parallel}")
    await mongo_db.update_user(account)
    await state.clear()
    await callback.message.answer("✅ Параллель успешно изменена!")
    await show_main_menu(callback.from_user.id)


@router.callback_query(F.data.startswith("edit_"))
async def start_edit_account(callback: types.CallbackQuery, state: FSMContext,router:Router):
    user_id = callback.from_user.id
    action = callback.data
    logging.info(f"пользователь {callback.from_user.username} изменяет аккаунт")
    if action == "edit_fio":
        logging.info(f"пользователь {callback.from_user.username} изменяет ФИО")
        await state.set_state(EditAccount.edit_fio)
        await send_or_edit_menu(router,
            user_id,
            "Введите новое ФИО:",
            InlineKeyboardBuilder().button(text="⬅️ Назад", callback_data="main_menu").as_markup()
        )
    elif action == "edit_parallel":
        logging.info(f"пользователь {callback.from_user.username} изменяет паралель")
        await state.set_state(EditAccount.edit_parallel)
        await send_or_edit_menu(router,
            user_id,
            "Выберите новую параллель:",
            parallels_kb_edit(parallels)
        )
    elif action == "edit_class":
        logging.info(f"пользователь {callback.from_user.username} изменяет класс")
        await state.set_state(EditAccount.edit_class)
    await callback.answer()


@router.callback_query(F.data.startswith("class_"))
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


@router.callback_query(F.data.startswith("parallel_"))
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
