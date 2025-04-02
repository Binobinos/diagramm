import datetime

from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from dob_func.dob_func import *
from keyboards.keyboard import support_admin_menu_kb, classes_kb
from model.User import User
from model.reqwest import Reqwest
from states.states import *

router = Router()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
type_items = {"Работа на уроке": 1, "Самостоятельная работа": 1.04, "Проверочная работа": 1.05,
              "Контрольная работа": 1.06}


@router.message(EditAccount.edit_fio)
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
    await show_main_menu(router, user_id)


@router.message(Support.message)
async def edit_fio(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    messages = message.text.strip()
    acc = await mongo_db.get_user(user_id)
    logging.info(f"пользователь {message.from_user.username} отправил сообщение тех поддержке:\n{messages}")
    request = Reqwest(id_=str(uuid4())[:8], user_id=user_id, username=message.from_user.username, messages=messages,
                      type="Сообщение")
    await mongo_db.insert_reqwest(request)
    await message.answer("✅ Сообщение успешно отправленною")
    await state.clear()
    await send_admins(f"{datetime.date.today()} - {messages}", support_admin_menu_kb(user_id), acc)


@router.message(Registration.enter_fio)
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
