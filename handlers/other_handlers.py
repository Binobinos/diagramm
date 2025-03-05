import datetime

from aiogram import Router, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from dob_func.dob_func import *
from keyboards.keyboard import error_menu_kb
from model.User import User

router = Router()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
type_items = {"Работа на уроке": 1, "Самостоятельная работа": 1.04, "Проверочная работа": 1.05,
              "Контрольная работа": 1.06}


@router.message(Command("start"))
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


@router.callback_query(F.data == "main_menu")
async def back_to_main(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_name = callback.from_user.username
    acc: User = await mongo_db.get_user(user_id)
    if acc is None:
        logging.info(f"пользователь {user_name} нажал start")
        await callback.answer("👋 Добро пожаловать! Для начала создайте свой первый аккаунт.")
        await start_registration(user_id, state)
    else:
        if not acc.ban:
            logging.info(f"пользователь {callback.from_user.username} переходит в главное меню")
            await show_main_menu(callback.from_user.id)
            await callback.answer()
        else:
            logging.info(f"забаненный пользователь {user_name} нажал start")
            await callback.answer("👋 Вы забанены")


@router.callback_query(F.data == "Technical_support")
async def support(callback: types.CallbackQuery, state: FSMContext):
    logging.info(f"пользователь {callback.from_user.username} нажал на тех-поддержку")
    await start_help(callback.from_user.id, state)
    await callback.answer()


@router.callback_query(F.data == "_")
async def error(callback: types.CallbackQuery):
    await callback.answer()
    text = (
        "🌟 Функция в разработке 😓...\n"
        "Но вы можете перейти к тестированию других функций"
    )
    await send_or_edit_menu(callback.from_user.id, text, error_menu_kb())


@router.callback_query(F.data.startswith("answer_"))
async def send_answer(callback: types.CallbackQuery):
    id_ = int(callback.data.split("_")[1])
    await send_or_edit_menu(
        id_,
        f"Вам п️р️и️ш️л️о️ сообщение от администрации в {datetime.date.today()}!\n{callback.data.split("_")[2]}",
        InlineKeyboardBuilder().button(text="⬅️ В главное меню", callback_data="main_menu").as_markup()
    )
    logging.info(f"пользователь {callback.from_user.username} получмл ответ")
    await callback.answer()
