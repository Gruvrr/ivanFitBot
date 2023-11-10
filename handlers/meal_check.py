import asyncio
import time
from handlers.meal_handler import manage_nutrition
from aiogram import Bot
from datetime import datetime, timedelta
from utils.db import connect, close


async def check_meal_every_day(bot: Bot):
    conn = connect()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT usm.telegram_user_id, usm.end_date
            FROM user_meal_plan usm
            JOIN users u ON usm.telegram_user_id = u.telegram_user_id
            WHERE u.is_subscription_active = true;

        """)
        users = cursor.fetchall()

        for user in users:
            telegram_user_id, end_date = user

            if end_date == datetime.now().date():
                # Создание новой записи в user_send_meal
                new_start_date = datetime.now().date() + timedelta(days=1)
                new_end_date = new_start_date + timedelta(days=7)
                create_new_user_meal_plan(cursor, telegram_user_id, new_start_date, new_end_date)
                await bot.send_message(telegram_user_id, text=f"""Ваш план питания изменен!""")
                time.sleep(3)
                await manage_nutrition(telegram_user_id, bot)

            elif end_date == datetime.now().date() + timedelta(days=2):
                # План питания изменится через два дня
                await bot.send_message(telegram_user_id, "Ваш план питания изменится через два дня.")

        conn.commit()

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def get_next_week_plan(cursor, telegram_user_id):
    # Найти текущий week_number пользователя
    cursor.execute("""
        SELECT npm.week_number
        FROM user_send_meal usm
        JOIN nutrition_plan_meal npm ON usm.nutrition_plan_meal_id = npm.id
        WHERE usm.telegram_user_id = %s
        ORDER BY usm.end_date DESC
        LIMIT 1;
    """, (telegram_user_id,))
    current_week_number = cursor.fetchone()[0]

    # Определить номер следующей недели, учитывая цикличность
    next_week_number = current_week_number + 1 if current_week_number < 4 else 1

    # Выбрать план питания для следующей недели
    cursor.execute("""
        SELECT m.name 
        FROM nutrition_plan_meal npm
        JOIN meals m ON npm.mealid = m.id
        WHERE npm.week_number = %s
        AND npm.is_active = true;
    """, (next_week_number,))
    meals = cursor.fetchall()

    return "\n".join(meal[0] for meal in meals)


def create_new_user_meal_plan(cursor, telegram_user_id, start_date, end_date):
    # Определение номера следующей недели
    cursor.execute("""
        SELECT week_number
        FROM user_meal_plan
        WHERE telegram_user_id = %s
        ORDER BY end_date DESC
        LIMIT 1;
    """, (telegram_user_id,))
    result = cursor.fetchone()
    current_week_number = result[0] if result else 0
    next_week_number = current_week_number + 1 if current_week_number < 4 else 1

    # Проверка существования записи для пользователя
    cursor.execute("""
        SELECT COUNT(*) FROM user_meal_plan
        WHERE telegram_user_id = %s AND week_number = %s;
    """, (telegram_user_id, next_week_number))
    count = cursor.fetchone()[0]

    # Обновление или вставка записи
    if count > 0:
        # Обновление существующей записи
        cursor.execute("""
            UPDATE user_meal_plan
            SET start_date = %s, end_date = %s, nutrition_plan_meal_id = %s
            WHERE telegram_user_id = %s AND week_number = %s;
        """, (start_date, end_date, telegram_user_id, next_week_number))
    else:
        # Создание новой записи
        cursor.execute("""
            INSERT INTO user_meal_plan (telegram_user_id, week_number, start_date, end_date)
            VALUES (%s, %s, %s, %s);
        """, (telegram_user_id, next_week_number, start_date, end_date))



