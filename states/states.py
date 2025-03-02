from aiogram.fsm.state import StatesGroup, State


class Registration(StatesGroup):
    select_parallel = State()
    select_class = State()
    enter_fio = State()
    password = State()


class EditAccount(StatesGroup):
    select_field = State()
    edit_parallel = State()
    edit_class = State()
    edit_fio = State()


class Authorization(StatesGroup):
    enter_password = State()


class Support(StatesGroup):
    message = State()
