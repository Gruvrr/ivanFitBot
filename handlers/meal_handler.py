from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from utils.db import connect, close
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import logging

logger = logging.getLogger(__name__)


router = Router()


async def send_meal_options(message: Message):
    current_week = 1  # Здесь можно задать логику для определения текущей недели
    conn = connect()
    cursor = conn.cursor()

    try:
        # Получаем ID пользователя
        telegram_user_id = message.from_user.id

        cursor.execute("""
            INSERT INTO user_meal_plan (telegram_user_id, week_number, nutrition_plan_meal_id, start_date, end_date)
            SELECT %s, %s, nutrition_plan_meal.mealid, NOW()::date, NOW()::date + 6
            FROM nutrition_plan_meal
            WHERE week_number = %s AND is_active = true
            LIMIT 1;
            """, (telegram_user_id, current_week, current_week))
        conn.commit()

        # Запрос для получения ID и названий приемов пищи
        cursor.execute("""
            SELECT meals.id, meals.name 
            FROM nutrition_plan_meal 
            JOIN meals ON meals.id = nutrition_plan_meal.mealid 
            WHERE nutrition_plan_meal.week_number = %s AND nutrition_plan_meal.is_active = true;
            """, (current_week,))
        meals = cursor.fetchall()

        if not meals:
            await message.answer("Приемы пищи на эту неделю не найдены.")
            return

        # Создание кнопок с использованием ID приемов пищи
        buttons = [InlineKeyboardButton(text=meal[1], callback_data="meal_" + str(meal[0])) for meal in meals]

        # Создание отдельной кнопки "Next 3"
        next3_button = InlineKeyboardButton(text="В главное меню!", callback_data="next3")

        # Создание клавиатуры с кнопками и добавление кнопки "Next 3"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[button] for button in buttons] + [[next3_button]])

        await message.answer("Выберите прием пищи", reply_markup=keyboard)

    except Exception as e:
        print(f"Error: {e}")
        await message.answer("Произошла ошибка при обработке запроса.")

    finally:
        cursor.close()
        close(conn)


@router.callback_query(lambda c: c.data == "back_in_meal_menu")
async def send_meal_options_callback(callback: CallbackQuery):
    telegram_user_id = callback.from_user.id
    conn = connect()
    cursor = conn.cursor()
    try:
        # Выполнение запроса для получения номера текущей недели
        cursor.execute("""
            SELECT week_number
            FROM user_meal_plan
            WHERE telegram_user_id = %s
            ORDER BY id DESC
            LIMIT 1;
        """, (telegram_user_id,))
        result = cursor.fetchone()

        if result:
            current_week = result[0]
        else:
            current_week = 1  # Установите значение по умолчанию, если записей не найдено

        # Запрос для получения названий приемов пищи на текущей неделе
        cursor.execute("""
            SELECT meals.id, meals.name 
            FROM nutrition_plan_meal 
            JOIN meals ON meals.id = nutrition_plan_meal.mealid 
            WHERE nutrition_plan_meal.week_number = %s AND nutrition_plan_meal.is_active = true;
        """, (current_week,))
        meals = cursor.fetchall()

        if not meals:
            await callback.answer("Приемы пищи на эту неделю не найдены.")
            return

        # Создание кнопок с использованием названий приемов пищи
        buttons = [InlineKeyboardButton(text=meal[1], callback_data=f"meal_{meal[0]}") for meal in meals]

        # Создание отдельной кнопки "Next 3" (или "В главное меню")
        next3_button = InlineKeyboardButton(text="В главное меню", callback_data="next3")

        # Создание клавиатуры с кнопками и добавление кнопки "Next 3" (или "В главное меню")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[button] for button in buttons] + [[next3_button]])

        await callback.message.answer("Выберите прием пищи", reply_markup=keyboard)

    except Exception as e:
        print(f"Error: {e}")
        await callback.message.answer("Произошла ошибка при обработке запроса.")
    finally:
        cursor.close()
        close(conn)


async def manage_nutrition(telegram_user_id, bot: Bot):
    logger.info(f"Началась функция менеджера питания")
    conn = connect()
    cursor = conn.cursor()
    # Выполнение запроса для получения номера текущей недели
    cursor.execute("""
            SELECT week_number
            FROM user_meal_plan
            WHERE telegram_user_id = %s 
            ORDER BY id DESC
            LIMIT 1;
            """, (telegram_user_id,))
    result = cursor.fetchone()

    if result:
        current_week = result[0]
    else:
        current_week = 1
    try:
        cursor.execute("""
            SELECT meals.id, meals.name 
            FROM nutrition_plan_meal 
            JOIN meals ON meals.id = nutrition_plan_meal.mealid 
            WHERE nutrition_plan_meal.week_number = %s AND nutrition_plan_meal.is_active = true;
            """, (current_week,))
        meals = cursor.fetchall()

        if not meals:
            await bot.send_message(chat_id=telegram_user_id, text="Приемы пищи на эту неделю не найдены.")
            return

        # Создание кнопок с использованием ID приемов пищи
        buttons = [InlineKeyboardButton(text=meal[1], callback_data="meal_" + str(meal[0])) for meal in meals]

        next3_button = InlineKeyboardButton(text="В главное меню!", callback_data="next3")

        keyboard = InlineKeyboardMarkup(inline_keyboard=[[button] for button in buttons] + [[next3_button]])

        await bot.send_message(chat_id=telegram_user_id, text="Выберите прием пищи", reply_markup=keyboard)


    except Exception as e:
        print(f"Error: {e}")
        await bot.send_message(chat_id=telegram_user_id, text="Произошла ошибка при обработке запроса.")

    finally:
        cursor.close()
        close(conn)
        logger.info(f"Функция менеджера питания закончилась")
