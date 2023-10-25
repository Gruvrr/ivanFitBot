from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    gender = State()
    first_name = State()
    last_name = State()
    age = State()
    phone_number = State()
    email = State()
    city = State()


class Link(StatesGroup):
    number = State()
    link = State()


class Meal(StatesGroup):
    name = State()
    description = State()


class Question(StatesGroup):
    text = State()