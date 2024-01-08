from datetime import datetime
from aiogram.filters import Command
import psycopg2
from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import Bot
from utils.states import User
import re
from dotenv import load_dotenv
from os import getenv
from keyboards.inline import user_gender_keyboard
import logging



load_dotenv()
host = getenv("LOCALHOST")
user = getenv("MYBOTUSER")
password = getenv("MYPASSWORD")
database = getenv("MYNAMEDB")
router = Router()
admin_id = getenv("ADMIN_ID")
token = getenv("TOKEN")
bot = Bot(token=token)
PHONE_REGEX = r'(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(?([0-9][0-9][0-9])\)?\s*(?:[.-]\s*)?)?([0-9][0-9][0-9])\s*(?:[.-]\s*)?([0-9][0-9][0-9][0-9]))'


@router.message(Command("create_user"))
async def new_profile(message: Message, state: FSMContext):
    await message.answer(text="Укажите пол пользователя", reply_markup=user_gender_keyboard)


@router.callback_query(F.data.casefold().in_(["male1", "female1"]))
async def say_first_name_user(callback: CallbackQuery, state: FSMContext):
    gender = "мужской" if callback.data == "male1" else "женский"
    await state.update_data(gender=gender)
    await state.set_state(User.first_name)
    await callback.message.edit_text(text="Введите имя пользователя!")
    await callback.answer()


@router.message(User.first_name)
async def say_last_name_user(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await state.set_state(User.last_name)
    await message.answer(text="Введите фамилию пользователя")


@router.message(User.last_name)
async def birth_day_user(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await state.set_state(User.birth_date)
    await message.answer(text="Введите дату рождения пользователя в формате ДД.ММ.ГГГГ")


@router.message(User.birth_date)
async def user_phone_number(message: Message, state: FSMContext):
    text = message.text
    try:
        birth_date = datetime.strptime(text, '%d.%m.%Y')
    except ValueError:
        await message.reply("Некорректный формат даты. Пожалуйста, попробуйте еще раз.")
        return

    today = datetime.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    if 0 <= age <= 95:
        await state.update_data(birth_date=birth_date)
        await state.set_state(User.phone_number)
        await message.answer(text="Введите номер телефона пользователя")
    else:
        await message.answer("Введите реалистичную дату рождения.")


@router.message(User.phone_number)
async def get_user_email(message: Message, state: FSMContext):
    if re.match(PHONE_REGEX, message.text):
        phone = message.text.replace('+', '')  # Удаляем знак "+"
        await state.update_data(phone_number=phone)
        await state.set_state(User.email)
        await message.answer(text="Введите email пользователя")
    else:
        await message.answer("Введите корректный номер телефона.")


@router.message(User.email)
async def get_user_city(message: Message, state: FSMContext):
    if "@" in message.text:  # Простая проверка email на наличие символа "@"
        await state.update_data(email=message.text)
        await state.set_state(User.city)
        await message.answer(text="Введите город пользователя")
    else:
        await message.answer("Введите корректный email")


@router.message(User.city)
async def get_user_training_number(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await state.set_state(User.training_number)
    await message.answer(text="Введите номер активной тренировки.")


@router.message(User.training_number)
async def get_telegram_user_id(message: Message, state: FSMContext):
    await state.update_data(training_number=message.text)
    await state.set_state(User.telegram_user_id)
    await message.answer(text="Введите telegram user id")


@router.message(User.telegram_user_id)
async def get_telegram_user_id(message: Message, state: FSMContext):
    await state.update_data(telegram_user_id=message.text)
    await state.set_state(User.count_active_days)
    await message.answer(text="Введите количество активных дней.")


@router.message(User.count_active_days)
async def get_telegram_user_id(message: Message, state: FSMContext):
    await state.update_data(count_active_days=message.text)
    await state.set_state(User.count_subscription)
    await message.answer(text="Введите количество подписок.")


@router.message(User.count_subscription)
async def get_telegram_user_id(message: Message, state: FSMContext):
    await state.update_data(count_subscription=message.text)
    await state.set_state(User.week_number)
    await message.answer(text="Введите номер недели для питания .")


@router.message(User.week_number)
async def get_telegram_user_id(message: Message, state: FSMContext):
    await state.update_data(week_number=message.text)
    await state.set_state(User.start_date)
    await message.answer(text="Введите дату начала плана питания.")


@router.message(User.start_date)
async def get_start_date(message: Message, state: FSMContext):
    date_text = message.text.strip()
    date_format = '%d.%m.%Y'

    # Проверяем, соответствует ли введенная дата формату ДД.ММ.ГГГГ
    if re.match(r'^\d{2}.\d{2}.\d{4}$', date_text):
        try:
            # Пытаемся преобразовать текст в дату
            start_date = datetime.strptime(date_text, date_format)

            await state.update_data(start_date=start_date)
            await state.set_state(User.end_date)  # Устанавливаем новое состояние
            await message.answer("Введите дату окончания периода питания (в формате ДД.ММ.ГГГГ):")
        except ValueError:
            await message.answer("Некорректная дата. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ.")
    else:
        await message.answer("Некорректный формат даты. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ.")


@router.message(User.end_date)
async def get_end_date(message: Message, state: FSMContext):
    date_text = message.text.strip()
    date_format = '%d.%m.%Y'

    # Проверяем, соответствует ли введенная дата формату ДД.ММ.ГГГГ
    if re.match(r'^\d{2}.\d{2}.\d{4}$', date_text):
        try:
            # Пытаемся преобразовать текст в дату
            end_date = datetime.strptime(date_text, date_format)

            await state.update_data(end_date=end_date)
            await state.set_state(User.nutrition_plan_meal_id)  # Устанавливаем новое состояние
            await message.answer("Введите айди для недели питания этого пользователя")
        except ValueError:
            await message.answer("Некорректная дата. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ.")
    else:
        await message.answer("Некорректный формат даты. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ.")


@router.message(User.nutrition_plan_meal_id)
async def res(message: Message, state: FSMContext):
    await state.update_data(nutrition_plan_meal_id=message.text)
    data = await state.get_data()
    logging.info(f"Received data: {data}")

    connection = None
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        logging.info("Connected to the database")

        with connection.cursor() as cursor:
            # Вставка пользователя
            logging.info("Inserting user data into the database")
            query = """
            INSERT INTO users (telegram_user_id, gender, first_name, last_name, birth_date, phone_number, email, city, subscription_days, subscription_purchases, is_subscription_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                data.get('telegram_user_id'), data.get('gender'), data.get('first_name'), data.get('last_name'),
                data.get('birth_date'), data.get('phone_number'), data.get('email'), data.get('city'), data.get('count_active_days'), data.get('count_subscription'), "True"
            )
            cursor.execute(query, values)
            logging.info(f"User {data.get('telegram_user_id')} inserted")

            # Вставка записи в user_meal_plan
            logging.info("Inserting data into user_meal_plan")
            insert_query = """
                        INSERT INTO user_meal_plan (telegram_user_id, week_number, start_date, end_date, nutrition_plan_meal_id)
                        VALUES (%s, %s, %s, %s, %s)
                        """
            values = (data.get('telegram_user_id'), data.get('week_number'), data.get('start_date'), data.get('end_date'), data.get('nutrition_plan_meal_id'))
            cursor.execute(insert_query, values)
            logging.info(f"Meal plan for user {data.get('telegram_user_id')} inserted")

            # Выборка и вставка тренировки
            logging.info("Selecting and inserting training data")
            select_training_query = """
                        SELECT training_number FROM training_links
                        WHERE training_number = %s AND status = 'active'
                        ORDER BY date_added ASC
                        LIMIT 1
                        """

            cursor.execute(select_training_query, (data.get('training_number'),))
            training_num = cursor.fetchone()

            if training_num:
                number = training_num[0]
                logging.info(f"Training number {number} selected")

                insert_sent_training_query = """
                            INSERT INTO user_trainings (user_id, training_number, is_sent, sent_date)
                            VALUES (%s, %s, 'true', NOW())"""
                cursor.execute(insert_sent_training_query, (data.get('telegram_user_id'), number))
                logging.info(f"Training {number} inserted for user {data.get('telegram_user_id')}")

            connection.commit()
            logging.info("Transaction committed")

    except Exception as e:
        logging.error(f"Error saving data to database: {e}", exc_info=True)
        if connection:
            connection.rollback()
            logging.info("Transaction rolled back")

    finally:
        if connection:
            connection.close()
            logging.info("Database connection closed")

    await state.clear()
    await message.answer("Пользователь успешно добавлен!✅")