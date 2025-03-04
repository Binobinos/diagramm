from aiogram import Router, types
from aiogram.types import Message
import logging
router = Router()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
from keyboards import *
from main import *
@router.callback_query(F.data == "help")
async def help_(callback: types.CallbackQuery):
    logging.info(f"пользователь {callback.from_user.username} открыл справку")
    await help_menu(callback.from_user.id)
    await callback.answer()


@router.callback_query(F.data == "help_1")
async def help_1(callback: types.CallbackQuery):
    logging.info(f"пользователь {callback.from_user.username} открыл справку")
    await help_1_menu(callback.from_user.id)
    await callback.answer()


@router.callback_query(F.data == "help_2")
async def help_2(callback: types.CallbackQuery):
    logging.info(f"пользователь {callback.from_user.username} открыл справку")
    await help_2_menu(callback.from_user.id)
    await callback.answer()


@router.callback_query(F.data == "help_3")
async def help_3(callback: types.CallbackQuery):
    logging.info(f"пользователь {callback.from_user.username} открыл справку")
    await help_3_menu(callback.from_user.id)
    await callback.answer()


@router.callback_query(F.data == "help_4")
async def help_4(callback: types.CallbackQuery):
    logging.info(f"пользователь {callback.from_user.username} открыл справку")
    await help_4_menu(callback.from_user.id)
    await send_admins("тест отправки всем админам", help_menu_kb())
    await callback.answer()



async def help_menu(user_id: int):
    logging.info(f"пользователь {user_id} открыл меню помощи")
    text = (
        "❔ Выберите интересующий вас раздел"
    )
    await send_or_edit_menu(user_id, text, help_menu_kb())


async def help_1_menu(user_id: int):
    logging.info(f"пользователь {user_id} открыл меню помощи")
    text = (
        "оплата"
    )
    await send_or_edit_menu(user_id, text, help_menu_kb())


async def help_2_menu(user_id: int):
    logging.info(f"пользователь {user_id} открыл меню помощи")
    text = (
        "❔ цена"
    )
    await send_or_edit_menu(user_id, text, help_menu_kb())


async def help_3_menu(user_id: int):
    logging.info(f"пользователь {user_id} открыл меню помощи")
    text = (
        "❔ безопасность"
    )
    await send_or_edit_menu(user_id, text, help_menu_kb())


async def help_4_menu(user_id: int):
    logging.info(f"пользователь {user_id} открыл меню помощи")
    text = (
        "❔ гарантии"
    )
    await send_or_edit_menu(user_id, text, help_menu_kb())

