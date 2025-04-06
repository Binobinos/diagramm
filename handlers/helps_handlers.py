from aiogram import Router, F
from aiogram import types

from dob_func.dob_func_ import help_menu, help_1_menu, help_2_menu, help_3_menu, help_4_menu, send_admins
from keyboards.keyboard import help_menu_kb
from main import *

router = Router()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


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
    await callback.answer()
