from aiogram.fsm.state import StatesGroup, State


class User(StatesGroup):
    gender = State()
    first_name = State()
    last_name = State()
    birth_date = State()
    phone_number = State()
    email = State()
    city = State()
    training_number = State()
    telegram_user_id = State()
    count_active_days = State()
    count_subscription = State()
    week_number = State()
    start_date = State()
    end_date = State()
    nutrition_plan_meal_id = State()


class WeekNutrition(StatesGroup):
    nutrition_plan_meal_id = State()
    description = State()


class Form(StatesGroup):
    gender = State()
    first_name = State()
    last_name = State()
    birth_date = State()
    phone_number = State()
    email = State()
    city = State()



class Link(StatesGroup):
    number = State()
    link = State()


class Meal(StatesGroup):
    is_new_cycle = State()
    name = State()
    description = State()
    week_number = State()


class Question(StatesGroup):
    text = State()