from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    gender = State()
    first_name = State()
    last_name = State()
    age = State()
    phone_number = State()
    email = State()
    city = State()