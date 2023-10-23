import time

import psycopg2
from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext

import handlers.main_menu
from utils.states import Form
from aiogram.filters import Command
import re
from dotenv import load_dotenv
from os import getenv
from keyboards.inline import gender_keyboard


load_dotenv()
host = getenv("LOCALHOST")
user = getenv("MYBOTUSER")
password = getenv("MYPASSWORD")
database = getenv("MYNAMEDB")
router = Router()
PHONE_REGEX = r'(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(?([0-9][0-9][0-9])\)?\s*(?:[.-]\s*)?)?([0-9][0-9][0-9])\s*(?:[.-]\s*)?([0-9][0-9][0-9][0-9]))'


async def new_profile(message: Message, state: FSMContext):
    print("All good")
    await state.set_state(Form.age)
    await message.answer(text="Как вы бы предпочли, чтобы к вам обращались?", reply_markup=gender_keyboard)


@router.callback_query(F.data.casefold().in_(["male", "female"]))
async def say_first_name(callback: CallbackQuery, state: FSMContext):
    gender = "мужской" if callback.data == "male" else "женский"
    print(gender)
    await state.update_data(gender=gender)
    await state.set_state(Form.first_name)
    await callback.message.edit_text(text="Введите ваше имя!")
    await callback.answer()


@router.message(Form.first_name)
async def say_last_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await state.set_state(Form.last_name)
    await message.answer(text="Введите вашу фамилию")


@router.message(Form.last_name)
async def birth_day(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await state.set_state(Form.age)
    await message.answer(text="Введите ваш возраст")


@router.message(Form.age)
async def phone_number(message: Message, state: FSMContext):
    if message.text.isdigit():
        age = int(message.text)
        if 0 <= age <= 95:
            await state.update_data(age=message.text)
            await state.set_state(Form.phone_number)
            await message.answer(text="Введите ваш номер телефона")
        else:
            await message.answer("Введите реалистичный возраст.")
    else:
        await message.answer("Возраст должен быть указан только цифрами.")


@router.message(Form.phone_number)
async def get_email(message: Message, state: FSMContext):
    if re.match(PHONE_REGEX, message.text):
        phone = message.text.replace('+', '')  # Удаляем знак "+"
        await state.update_data(phone_number=phone)
        await state.set_state(Form.email)
        await message.answer(text="Введите ваш email")
    else:
        await message.answer("Введите корректный номер телефона.")


@router.message(Form.email)
async def get_city(message: Message, state: FSMContext):
    if "@" in message.text:  # Простая проверка email на наличие символа "@"
        await state.update_data(email=message.text)
        await state.set_state(Form.city)
        await message.answer(text="Введите ваш город")
    else:
        await message.answer("Введите корректный email")


@router.message(Form.city)
async def res(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    data = await state.get_data()

    connection = None
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        with connection.cursor() as cursor:
            query = """
            INSERT INTO users (telegram_user_id, gender, first_name, last_name, age, phone_number, email, city, subscription_days, subscription_purchases)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                message.from_user.id, data.get('gender'), data.get('first_name'), data.get('last_name'),
                data.get('age'), data.get('phone_number'), data.get('email'), data.get('city'), 0, 0
            )
            cursor.execute(query, values)
            connection.commit()

    except Exception as e:
        print("Error saving data to database:", e)
    finally:
        if connection:
            connection.close()

    await state.clear()
    await message.answer("Регистрация успешно пройдена✅")
    time.sleep(3)
    await handlers.main_menu.main_menu(message)

