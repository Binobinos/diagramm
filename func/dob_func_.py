import json
import logging

from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

import config
from keyboards.keyboard import (help_menu_kb,
                                support_menu_kb,
                                parallels_kb,
                                orders_admin_menu_kb,
                                predmet_menu_kb,
                                main_menu_kb, predmet_help_menu_kb)
from model.reqwest import Reqwest
from model.user import User
from states.states import Support, Registration

user_menu_messages = {}

mongo_db = config.mongo_db
parallels = config.parallels


async def send_photo_with_buttons(user_id: int, caption: str):
    photo = "https://avatars.mds.yandex.net/i?id=542bef1a9cddbf575433c7d1abb43d4c_l-12483207-images-thumbs&n=13"  # для URL

    await config.bot.send_photo(
        chat_id=user_id,
        photo=photo,
        caption=caption,
        parse_mode=ParseMode.MARKDOWN_V2
    )

async def send_or_edit_menu(user_id: int, text: str, keyboard):
    print(user_menu_messages)
    try:
        if user_id in user_menu_messages:
            await config.bot.edit_message_text(
                chat_id=user_id,
                message_id=user_menu_messages[user_id],
                text=text,
                reply_markup=keyboard
            )
        else:
            msg = await config.bot.send_message(user_id, text, reply_markup=keyboard)
            user_menu_messages[user_id] = msg.message_id
    except Exception as e:
        msg = await config.bot.send_message(user_id, text, reply_markup=keyboard)
        user_menu_messages[user_id] = msg.message_id


async def show_client_reqwest(order: Reqwest, admin_id):
    logging.info(f"Админ {admin_id} Смотрит корзину пользователя {order.username} - {order.user_id}")
    text = (
        f"🎉 Здравствуйте! Это Запрос от {order.username}\n"
        f"📙 Время - {order.datetime}. Тип - {order.type}\n{order.messages}"
    )
    await send_or_edit_menu(admin_id, text, orders_admin_menu_kb())


async def send_admins(text: str, keyboard, user: User):
    admins = await mongo_db.get_admins()
    for admin in admins:
        await send_or_edit_menu(admin.id,
                                f"Пользователь {user.username} - {user.id} Отправил запрос:\n{text.capitalize()}",
                                keyboard)


async def show_main_menu(user_id: int):
    logging.info(f"пользователь {user_id} открыл главное меню")
    text = (
        "🌟 Главное меню:\n\n"
        "Здесь вы можете управлять своими аккаунтами, "
        "настраивать параметры и получать помощь."
    )
    acc = await mongo_db.get_user(user_id)
    await send_or_edit_menu(user_id, text, main_menu_kb(acc))


async def start_help(user_id: int, state: FSMContext):
    logging.info(f"пользователь {user_id} начал тех-поддержку")
    await state.set_state(Support.message)
    await send_or_edit_menu(
        user_id,
        "Введите сообщение тех поддержке",
        support_menu_kb()
    )

async def show_object_menu(user_id: int):
    logging.info(f"пользователь {user_id} открыл меню выбора предмета")
    text = (
        "🎉 Здравствуйте! Вот список ваших предметов "
        "📙 Выберите Предмет из доступных"
    )
    account: User = await mongo_db.get_user(user_id)
    predmet = {}  # Инициализация переменной перед использованием
    with open(r'D:\pythonProject1\API\user_school_class.json', 'r', encoding="utf-8") as file:
        data: list = json.load(file)
        for i in data:
            if i[0] == f"{account.parallel} {account.class_name.lower()}":
                predmet = i[1]["предметы"]
                break
    await send_or_edit_menu(user_id, text, predmet_menu_kb(parallels=list(predmet.keys())))


async def show_object_home_menu(user_id: int):
    logging.info(f"пользователь {user_id} открыл меню выбора оценок предмета")
    text = (
        "🎉 Здравствуйте! Вот список ваших предметов "
        "📙 Выберите Предмет из доступных"
    )
    account: User = await mongo_db.get_user(user_id)
    predmet = {}  # Инициализация переменной перед использованием
    with open(r'D:\pythonProject1\API\user_school_class.json', 'r', encoding="utf-8") as file:
        data: list = json.load(file)
        for i in data:
            if i[0] == f"{account.parallel} {account.class_name.lower()}":
                predmet = i[1]["предметы"]
                break
    await send_or_edit_menu(user_id, text, predmet_help_menu_kb(parallels=list(predmet.keys())))


async def start_registration(user_id: int, state: FSMContext):
    logging.info(f"пользователь {user_id} начал регистрацию")
    await state.set_state(Registration.select_parallel)
    await send_or_edit_menu(
        user_id,
        "📚 Выберите параллель:",
        parallels_kb(parallels)
    )


async def help_menu(user_id: int, text: str, buttons, current=0):
    logging.info(f"пользователь {user_id} открыл меню помощи")
    await send_or_edit_menu(user_id, text, help_menu_kb(buttons, current))
print("", flush=True)
float("101")