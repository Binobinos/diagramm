import asyncio
import datetime

from aiogram import Router, F
from aiogram import types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from Nots.test import *
from dob_func.dob_func_ import *
from keyboards.keyboard import error_menu_kb
from model.user import User

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
    """ Ошибка хандлера"""
    await callback.answer()
    text = (
        "🌟 Функция в разработке 😓...\n"
        "Но вы можете перейти к тестированию других функций"
    )
    await send_or_edit_menu(callback.from_user.id, text, error_menu_kb())


@router.callback_query(F.data.startswith("answer_"))
async def send_answer(callback: types.CallbackQuery):
    """ Отправляет пользователю сообщение от администрации"""
    id_ = int(callback.data.split("_")[1])
    await send_or_edit_menu(id_,
                            f"Вам п️р️и️ш️л️о️ сообщение от администрации в {datetime.date.today()}!\n"
                            f"{callback.data.split("_")[2]}",
                            InlineKeyboardBuilder().button(text="⬅️ В главное меню",
                                                           callback_data="main_menu").as_markup())
    logging.info(f"пользователь {callback.from_user.username} получил ответ")
    await callback.answer()


@router.callback_query(F.data == "homework")
async def homework(callback: types.CallbackQuery):
    """ Показывает домашнею работу"""
    id_ = int(callback.from_user.id)
    acc = await mongo_db.get_user(id_)
    auth = SchoolAuth()

    # Отвечаем сразу и запускаем анимацию
    await callback.answer("⏳ Начинаю загрузку...")
    progress_msg = await callback.message.answer("🌑 Загрузка данных...")

    # Создаем флаг для остановки анимации
    stop_event = asyncio.Event()

    # Задача для анимации
    async def animate_progress():
        frames = ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"]
        while not stop_event.is_set():
            for frame in frames:
                if stop_event.is_set():
                    break
                await progress_msg.edit_text(f"{frame} Идёт загрузка...")
                await asyncio.sleep(0.3)

    # Запускаем анимацию
    animation_task = asyncio.create_task(animate_progress())

    try:
        result = "Ничего не задано или не найдено"
        if auth.login(config.USER_LOGIN, config.USER_PASSWORD):
            # Запускаем синхронную задачу в потоке
            result = await asyncio.to_thread(
                set_homework,
                f"{acc.parallel} {acc.class_name.lower()}",
                type="recent",
                auth=auth
            )

        # Останавливаем анимацию
        stop_event.set()
        await animation_task

        # Удаляем сообщение с прогрессом
        await progress_msg.delete()

        # Отправляем финальное сообщение
        await send_or_edit_menu(id_, f"{result}",
                                InlineKeyboardBuilder().button(text="⬅️ В главное меню",
                                                               callback_data="main_menu").as_markup())

    except Exception as e:
        stop_event.set()
        await progress_msg.edit_text(f"❌ Ошибка: {str(e)}")
        logging.error(f"Ошибка: {str(e)}")
