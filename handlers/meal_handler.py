from keyboards import inline
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from keyboards.inline import generate_meal_keyboard, next_button, next_button2, next_button3
from utils.db import connect, close
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime

router = Router()


async def send_meal_options(message: Message):
    current_week = 1
    conn = connect()
    cursor = conn.cursor()

    try:
        # Получаем ID пользователя
        telegram_user_id = message.from_user.id

        cursor.execute("""
            SELECT id 
            FROM user_send_meal 
            WHERE telegram_user_id = %s AND start_date = NOW()::date AND end_date = NOW()::date + 6;
            """, (telegram_user_id,))
        existing_record = cursor.fetchone()

        if existing_record:
            await message.answer("Запись о питании на текущую неделю уже существует.")
        else:
            # Создаем запись для текущей недели
            cursor.execute("""
                INSERT INTO user_send_meal (telegram_user_id, nutrition_plan_meal_id, start_date, end_date)
                SELECT %s, nutrition_plan_meal.mealid, NOW()::date, NOW()::date + 6
                FROM nutrition_plan_meal
                WHERE week_number = %s AND is_active = true;
                """, (telegram_user_id, current_week))

            await message.answer("Запись о питании на текущую неделю создана успешно.")

        # Остальной код для создания кнопок и клавиатуры остается без изменений

    except Exception as e:
        print(f"Error: {e}")
        await message.answer("Произошла ошибка при обработке запроса.")

    finally:
        cursor.close()
        close(conn)


@router.callback_query(lambda c: c.data == "meal")
async def handle_meal_callback(query: CallbackQuery):
    user_id = query.from_user.id

    conn = connect()
    cursor = conn.cursor()

    try:
        # Получаем номер недели пользователя из таблицы user_send_meal
        cursor.execute("""
            SELECT nutrition_plan_meal.week_number 
            FROM user_send_meal 
            JOIN nutrition_plan_meal ON nutrition_plan_meal.id = user_send_meal.nutrition_plan_meal_id 
            WHERE user_send_meal.telegram_user_id = %s
            ORDER BY user_send_meal.start_date DESC
            LIMIT 1;
        """, (user_id,))
        result = cursor.fetchone()

        if result:
            current_week = result[0]
        else:
            # Если информация о номере недели пользователя не найдена, установите значение по умолчанию (например, 1).
            current_week = 1

        # Остальной код для создания клавиатуры остается без изменений.
        cursor.execute("""
            SELECT meals.id, meals.name 
            FROM nutrition_plan_meal 
            JOIN meals ON meals.id = nutrition_plan_meal.mealid 
            WHERE nutrition_plan_meal.week_number = %s AND nutrition_plan_meal.is_active = true;
            """, (current_week,))
        meals = cursor.fetchall()

        if not meals:
            await query.message.answer("Приемы пищи на эту неделю не найдены.")
            return

        buttons = [InlineKeyboardButton(text=meal[1], callback_data="meal_" + str(meal[0])) for meal in meals]
        next3_button = InlineKeyboardButton(text="В главное меню", callback_data="next3")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[button] for button in buttons] + [[next3_button]])

        await query.message.answer("Выберите прием пищи", reply_markup=keyboard)

    except Exception as e:
        print(f"Error: {e}")
        await query.message.answer("Произошла ошибка при извлечении данных.")

    finally:
        cursor.close()
        close(conn)




