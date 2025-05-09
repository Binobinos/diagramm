import asyncio

from aiogram import Router, F
from aiogram import types as tp
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from API.api_school import *
from func.dob_func_ import *
from keyboards.keyboard import error_menu_kb
from model.user import User

router = Router()
logging.basicConfig(level=config.LOGGING_LEVEL, format="%(asctime)s %(levelname)s %(message)s")
type_items = config.type_items


@router.message(Command("start"))
async def cmd_start(message: tp.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.from_user.username
    acc: User = await mongo_db.get_user(user_id)
    if acc is None:
        logging.info(f"пользователь {user_name} нажал start")
        await message.answer("👋 Добро пожаловать! Для начала создайте свой первый аккаунт.")
        await start_registration(user_id, state)
    else:
        if not acc.is_ban:
            await show_main_menu(user_id)
        else:
            logging.info(f"забаненный пользователь {user_name} нажал start")
            await message.answer("👋 Вы забанены")


@router.callback_query(F.data == "main_menu")
async def back_to_main(callback: tp.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_name = callback.from_user.username
    acc: User = await mongo_db.get_user(user_id)
    if acc is None:
        logging.info(f"пользователь {user_name} нажал start")
        await callback.answer("👋 Добро пожаловать! Для начала создайте свой первый аккаунт.")
        await start_registration(user_id, state)
    else:
        if not acc.is_ban:
            logging.info(f"пользователь {callback.from_user.username} переходит в главное меню")
            await show_main_menu(callback.from_user.id)
            await callback.answer()
        else:
            logging.info(f"забаненный пользователь {user_name} нажал start")
            await callback.answer("👋 Вы забанены")


@router.callback_query(F.data == "Technical_support")
async def support(callback: tp.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_name = callback.from_user.username
    acc: User = await mongo_db.get_user(user_id)
    if not acc.is_ban:
        logging.info(f"пользователь {user_name} нажал на тех-поддержку")
        await start_help(user_id, state)
        await callback.answer()
    else:
        logging.info(f"забаненный пользователь {user_name} нажал start")
        await callback.answer("👋 Вы забанены")


@router.callback_query(F.data == "_")
async def error(callback: tp.CallbackQuery):
    """ Ошибка хандлера"""
    await callback.answer()
    text = (
        "🌟 Функция в разработке 😓...\n"
        "Но вы можете перейти к тестированию других функций"
    )
    await send_or_edit_menu(callback.from_user.id, text, error_menu_kb())


@router.callback_query(F.data.startswith("answer_"))
async def send_answer(callback: tp.CallbackQuery):
    """ Отправляет пользователю сообщение от администрации"""
    id_ = int(callback.data.split("_")[1])
    await send_or_edit_menu(id_,
                            f"Вам п️р️и️ш️л️о️ сообщение от администрации в {datetime.date.today()}!\n"
                            f"{callback.data.split("_")[2]}",
                            InlineKeyboardBuilder().button(text="⬅️ В главное меню",
                                                           callback_data="main_menu").as_markup())
    logging.info(f"пользователь {callback.from_user.username} получил ответ")
    await callback.answer()

last = None


@router.callback_query(F.data == "homework")
async def homework(callback: tp.CallbackQuery):
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
                get_homework,
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


@router.callback_query(F.data == "evaluations")
async def show_my_object(callback: tp.CallbackQuery):
    logging.info(f"пользователь {callback.from_user.username} открыл меню выбора предмета оценки")
    await show_object_home_menu(callback.from_user.id)
    await callback.answer()


@router.callback_query(F.data.startswith("es_"))
async def evaluations(callback: tp.CallbackQuery):
    """ Показывает оценки пользователя"""
    objects = callback.data.split("_")[1]
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
            if objects != "all":
                result = await asyncio.to_thread(
                    print_ozen,
                    f"{objects}", f"{acc.parallel} {acc.class_name.lower()}",
                    acc.full_name.split()[0] + " " + acc.full_name.split()[1], auth
                )
            else:
                predmet = {}  # Инициализация переменной перед использованием
                with open(r'D:\pythonProject1\API\user_school_class.json', 'r', encoding="utf-8") as file:
                    data: list = json.load(file)
                    for i in data:
                        if i[0] == f"{acc.parallel} {acc.class_name.lower()}":
                            predmet = i[1]["предметы"]
                            break
                predmets = list(predmet.keys())
                result = ""
                for name in predmets:
                    result += await asyncio.to_thread(
                        print_ozen,
                        f"{name}", f"{acc.parallel} {acc.class_name.lower()}",
                        acc.full_name.split()[0] + " " + acc.full_name.split()[1], auth
                    )

        # Останавливаем анимацию
        stop_event.set()
        await animation_task

        # Удаляем сообщение с прогрессом
        await progress_msg.delete()

        # Отправляем финальное сообщение
        print(len(result))
        await send_or_edit_menu(id_, f"{result}",
                                InlineKeyboardBuilder().button(text="⬅️ В главное меню",
                                                               callback_data="main_menu").as_markup())

    except Exception as e:
        stop_event.set()
        await progress_msg.edit_text(f"❌ Ошибка: {str(e)}")
        logging.error(f"Ошибка: {str(e)}")
