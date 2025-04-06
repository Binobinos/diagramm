import logging
from typing import List

from aiogram.utils.keyboard import InlineKeyboardBuilder

import config
from func.prices import calculating_the_price
from model.user import User
from model.order import Orders
from model.reqwest import Reqwest
logging.basicConfig(level=config.LOGGING_LEVEL, format="%(asctime)s %(levelname)s %(message)s")


def main_kb(builder, ad=2, text="⬅️ Назад", callback_data="main_menu"):
    builder.button(text=text, callback_data=callback_data)
    builder.adjust(ad)
    return builder.as_markup()


# Меню
def main_menu_kb(acc: User):
    builder = InlineKeyboardBuilder()
    builder.button(text="📙 Предметы", callback_data="my_predmet")
    builder.button(text="🙍‍♂️ Мой аккаунт", callback_data="my_accounts")
    builder.button(text="ℹ️ Помощь", callback_data="help")
    builder.button(text="🛠 Тех-поддержка", callback_data="Technical_support")
    builder.button(text="🛒 Корзина", callback_data="order")
    builder.button(text="📚 ДЗ", callback_data="homework")
    builder.adjust(2)
    if acc.user_level == "admin":
        builder.button(text="💼 Заказы", callback_data="Orders_0")
        builder.button(text="❓ Обращения в Тех-поддержку 💭", callback_data="Technical_support_0")
        builder.button(text="⚙️ Настройки бота", callback_data="_")
        builder.button(text="📊 Статистика", callback_data="_")
        builder.button(text="⚙️ Изменить текст меню", callback_data="_")
        builder.adjust(1)
    return builder.as_markup()


def orders_menu_kb(orders: List[Orders], start: int = 0):
    builder = InlineKeyboardBuilder()
    if not start + 6 > len(orders):
        for number, order in enumerate(orders[start:start + 6]):
            builder.button(text=f"Заказ {number + 1 + start} - {order.username}",
                           callback_data=f"*order-new_{order.id}")
        if not start == 0:
            builder.button(text=f"<<", callback_data=f"Orders_{start - 6}")
            builder.button(text=f">>", callback_data=f"Orders_{start + 6}")
        else:
            builder.button(text=f">>", callback_data=f"Orders_{start + 6}")
    else:
        for number, order in enumerate(orders[start:]):
            builder.button(text=f"Заказ {number + 1 + start} - {order.username}",
                           callback_data=f"*order-new_{order.id}")
        builder.button(text=f"<<", callback_data=f"Orders_{start - 6}")
    builder.button(text="⚙️ Изменить текст меню", callback_data="_")
    return main_kb(builder, ad=1)


def technical_support_menu_kb(reqwest: List[Reqwest], start: int = 0):
    builder = InlineKeyboardBuilder()
    if not start + 6 > len(reqwest):
        for number, order in enumerate(reqwest[start:start + 6]):
            builder.button(text=f"{order.messages[:32]} - {order.username}",
                           callback_data=f"*order-new_{order.id_}")
        if not start == 0:
            builder.button(text=f"<<", callback_data=f"Technical_support_{start - 6}")
            builder.button(text=f">>", callback_data=f"Technical_support_{start + 6}")
        else:
            builder.button(text=f">>", callback_data=f"Technical_support_{start + 6}")
    else:
        for number, order in enumerate(reqwest[start:]):
            builder.button(text=f"{order.messages[:32]} - {order.username}",
                           callback_data=f"*Technical-support_{order.id_}")
        builder.button(text=f"<<", callback_data=f"Technical_support_{start - 6}")
    builder.button(text="⚙️ Изменить текст меню", callback_data="_")
    return main_kb(builder, ad=1)


def help_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="💲 Оплата", callback_data="help_1")
    builder.button(text="📂 Цена-образование", callback_data="help_2")
    builder.button(text="🔑 Безопасность", callback_data="help_3")
    builder.button(text="🛠 Гарантии", callback_data="help_4")
    return main_kb(builder, ad=1)


def support_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="📙 популярный вопрос 1", callback_data="_")
    builder.button(text="📂 популярный вопрос 2", callback_data="_")
    builder.button(text="🔑 популярный вопрос 3", callback_data="_")
    builder.button(text="🛠 популярный вопрос 4", callback_data="_")
    return main_kb(builder, ad=1)


def orders_admin_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="Выполнил✅", callback_data="_")
    builder.button(text="Не выполнил ❌", callback_data="_")
    builder.button(text="", callback_data="_")
    builder.button(text="⚙️ Изменить текст меню", callback_data="_")
    return main_kb(builder, ad=1)


def error_menu_kb():
    builder = InlineKeyboardBuilder()
    return main_kb(builder, ad=1)


def support_admin_menu_kb(id_):
    builder = InlineKeyboardBuilder()
    builder.button(text="📙 популярный ответ 1", callback_data=f"answer_{id_}_123")
    return main_kb(builder, ad=1)


def order_admin_menu_kb():
    builder = InlineKeyboardBuilder()
    return main_kb(builder, ad=1)


def accounts_type_kb(type_osen):
    builder = InlineKeyboardBuilder()
    for i in type_osen.keys():
        builder.button(text=f"{i}", callback_data=f"tip_{i}")
    return main_kb(builder)


def accounts_tip_o_kb(acc: User):
    builder = InlineKeyboardBuilder()
    for i in range(0, 4):
        price = int(calculating_the_price(
            {acc.temp_order["Тип оценки"]: {"1 Оценка": 0, "2 Оценка": 5 - i, "предмет": acc.temp_order["предмет"]}}))
        builder.button(
            text=f"{5 - i} - {price} Руб",
            callback_data=f"type_{5 - i}")
    return main_kb(builder)


def accounts_cht_kb():
    builder = InlineKeyboardBuilder()
    for i in range(1, 5):
        builder.button(text=f"{i}-вая Четверть", callback_data=f"CHT_{i}")
    return main_kb(builder)


def predmet_menu_kb(paralell: str, parallels):
    builder = InlineKeyboardBuilder()
    for predmet in sorted(parallels[paralell][1]):
        builder.button(text=f"{predmet}", callback_data=f"predmet_{predmet}")
    return main_kb(builder)


# Меню редактирования аккаунта
def edit_account_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ ФИО", callback_data="edit_fio")
    builder.button(text="🏫 Класс", callback_data="edit_parallel")
    builder.button(text="🗑 Удалить", callback_data="delete_account")
    return main_kb(builder)


def edit_zacaz_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="Всё ок! 👍", callback_data="add_basket")
    builder.button(text="🗑 Удалить", callback_data="main_menu")
    builder.button(text="🛒 Корзина", callback_data="Order_show")
    return main_kb(builder, text="⬅️ В главное меню", callback_data="add_basket")


def korzin_null():
    builder = InlineKeyboardBuilder()
    builder.button(text="🙌Да!", callback_data="my_predmet")
    return main_kb(builder, text="⬅️ В главное меню", ad=1)


def order_kb_show(acc: User):
    builder = InlineKeyboardBuilder()
    for i in acc.order.products:
        # builder.button(text=f"Номер {i.id} - Изменить", callback_data=f"change_number_order_{i.id}")
        builder.button(text=f"Номер {i.id[:8]} - Удалить", callback_data=f"delete_number_order_{i.id}")
    builder.button(text=f"Оплатить", callback_data=f"pay")
    return main_kb(builder, text="⬅️ В главное меню", ad=1)


# Клавиатуры для регистрации
def parallels_kb(parallels):
    builder = InlineKeyboardBuilder()
    for parallel in parallels.keys():
        builder.button(text=f"{parallel} Параллель", callback_data=f"parallel_{parallel}")
    builder.adjust(2)
    return builder.as_markup()


def parallels_kb_edit(parallels):
    builder = InlineKeyboardBuilder()
    for parallel in parallels.keys():
        builder.button(text=f"{parallel} Параллель", callback_data=f"paralleledit_{parallel}")
    builder.adjust(2)
    return builder.as_markup()


def classes_kb(parallel: str, parallels):
    builder = InlineKeyboardBuilder()
    for class_name in parallels[parallel][0]:
        builder.button(text=f"{parallel} {class_name}", callback_data=f"class_{parallel} {class_name}")
    return main_kb(builder, callback_data="back_to_parallels")
