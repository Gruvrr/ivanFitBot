import time
import datetime
from aiogram.filters import Command
import psycopg2
from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import Bot
import handlers.main_menu
from utils.states import Form, Question
import re
from dotenv import load_dotenv
from os import getenv
from keyboards.inline import gender_keyboard


load_dotenv()
router = Router()
host = getenv("LOCALHOST")
user = getenv("MYBOTUSER")
password = getenv("MYPASSWORD")
database = getenv("MYNAMEDB")
admin_id = getenv("ADMIN_ID")
anna_id = getenv("ANNA_ID")
token = getenv("TOKEN")
bot = Bot(token=token)
PHONE_REGEX = r'(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(?([0-9][0-9][0-9])\)?\s*(?:[.-]\s*)?)?([0-9][0-9][0-9])\s*(?:[.-]\s*)?([0-9][0-9][0-9][0-9]))'


@router.callback_query(lambda c: c.data == "quick_answer")
async def send_question(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Question.text)
    await callback.message.answer(text=f"✍️Напишите свой вопрос и отправьте\n\n"
                              f"Желательно, что бы он был короткий, но точный и содержал ключевые слова")


@router.message(Question.text)
async def res_question(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    data = await state.get_data()
    msg = (f"Пользователь с таким nickname - @{message.from_user.username}, задает вопрос:\n"
           f"{data.get('text')}")
    await bot.send_message(chat_id=admin_id, text=msg)


async def new_profile(message: Message, state: FSMContext):
    await message.answer(text="Укажите ваш пол", reply_markup=gender_keyboard)


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
    await state.set_state(Form.birth_date)
    await message.answer(text="Введите вашу дату рождения в формате ДД.ММ.ГГГГ")


@router.message(Form.birth_date)
async def phone_number(message: Message, state: FSMContext):
    text = message.text
    try:
        birth_date = datetime.datetime.strptime(text, '%d.%m.%Y')
    except ValueError:
        await message.reply("Некорректный формат даты. Пожалуйста, попробуйте еще раз.")
        return

    today = datetime.datetime.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    if 0 <= age <= 95:
        await state.update_data(birth_date=birth_date)
        await state.set_state(Form.phone_number)
        await message.answer(text="Введите ваш номер телефона")
    else:
        await message.answer("Введите реалистичную дату рождения.")


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
            INSERT INTO users (telegram_user_id, gender, first_name, last_name, birth_date, phone_number, email, city, subscription_days, subscription_purchases)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                message.from_user.id, data.get('gender'), data.get('first_name'), data.get('last_name'),
                data.get('birth_date'), data.get('phone_number'), data.get('email'), data.get('city'), 0, 0
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

