import logging

from aiogram.fsm.context import FSMContext

import config
from keyboards.keyboard import (help_menu_kb,
                                support_menu_kb,
                                parallels_kb,
                                orders_admin_menu_kb,
                                predmet_menu_kb,
                                main_menu_kb)
from model.reqwest import Reqwest
from model.user import User
from states.states import Support, Registration

user_menu_messages = {}

mongo_db = config.mongo_db
parallels = config.parallels


async def send_or_edit_menu(user_id: int, text: str, keyboard):
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
    except Exception:
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
    await send_or_edit_menu(user_id, text, predmet_menu_kb(parallels=parallels, paralell=str(account.parallel)))


async def start_registration(user_id: int, state: FSMContext):
    logging.info(f"пользователь {user_id} начал регистрацию")
    await state.set_state(Registration.select_parallel)
    await send_or_edit_menu(
        user_id,
        "📚 Выберите параллель:",
        parallels_kb(parallels)
    )


async def help_menu(user_id: int, text: str, buttons):
    logging.info(f"пользователь {user_id} открыл меню помощи")
    await send_or_edit_menu(user_id, text, help_menu_kb(buttons))
