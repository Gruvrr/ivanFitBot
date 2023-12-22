import time
from handlers.meal_handler import manage_nutrition
from aiogram import Bot
from datetime import datetime, timedelta
from utils.db import connect, close
import logging
from os import getenv
from dotenv import load_dotenv
load_dotenv()

admin_id = getenv("ADMIN_ID")

logger = logging.getLogger(__name__)


async def check_meal_every_day(bot: Bot):
    conn = connect()
    cursor = conn.cursor()

    users_today = []
    users_in_two_days = []

    try:
        cursor.execute("""
            SELECT usm.telegram_user_id, u.first_name, u.last_name, u.subscription_days, usm.end_date
            FROM user_meal_plan usm
            JOIN users u ON usm.telegram_user_id = u.telegram_user_id
            WHERE u.is_subscription_active = true;

        """)
        users = cursor.fetchall()
        logger.info(f"Извлечение активных пользователей успешно!")

        for user in users:
            telegram_user_id,first_name, last_name, subscription_days, end_date = user
            full_name = f"{first_name} {last_name}"
            current_date = datetime.now().date()

            if end_date == current_date:
                logger.info(f"Сработало условие - если сегодня заканчивается план питания или он был завершен давно для пользователя - {telegram_user_id}")
                users_today.append(full_name)
                new_start_date = datetime.now().date() + timedelta(days=1)
                create_new_user_meal_plan(cursor, telegram_user_id, new_start_date)
                await bot.send_message(telegram_user_id, text=f"""Ваш план питания изменен!""")
                time.sleep(1)
                await manage_nutrition(telegram_user_id, bot)
            elif end_date == datetime.now().date() + timedelta(days=2) and subscription_days > 2:
                logger.info(
                    f"Сработало условие - если план питания заканчивается через 2 дня для пользователя - {telegram_user_id}")
                users_in_two_days.append(full_name)
                await bot.send_message(telegram_user_id, f"Ваш план питания изменится через два дня."
                                                         f"Подготовьте, пожалуйста,  продукты на следующие 7 дней.")
                description_meal = get_next_nutrition_plan_description(telegram_user_id)
                await bot.send_message(telegram_user_id, text=description_meal)
        if users_today:
            users_today_str = ', '.join(users_today)
            await bot.send_message(admin_id, text=f"Сегодня план питания изменен для: {users_today_str}")

        if users_in_two_days:
            users_in_two_days_str = ', '.join(users_in_two_days)
            await bot.send_message(admin_id, text=f"Через два дня план питания изменится для: {users_in_two_days_str}")
        conn.commit()

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        logger.info(
            f"Произошла ошибка - {e}")

        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def get_next_nutrition_plan_description(telegram_user_id: int) -> str:
    """ Получает описание следующего плана питания для пользователя по его Telegram ID. """
    conn = connect()
    try:
        with conn.cursor() as cursor:
            # Получение текущего nutrition_plan_meal_id для пользователя
            cursor.execute(
                "SELECT nutrition_plan_meal_id FROM user_meal_plan WHERE telegram_user_id = %s",
                (telegram_user_id,)
            )
            result = cursor.fetchone()

            if result and result[0]:
                current_nutrition_plan_meal_id = result[0]
                print(current_nutrition_plan_meal_id)
                # Получение следующего nutrition_plan_meal_id
                cursor.execute(
                    "SELECT nutrition_plan_meal_id FROM nutrition_week_plan WHERE nutrition_plan_meal_id > %s ORDER BY id ASC LIMIT 1",
                    (current_nutrition_plan_meal_id,)
                )
                next_result = cursor.fetchone()
                if next_result and next_result[0]:
                    next_nutrition_plan_meal_id = next_result[0]
                    # Получение описания следующего плана питания
                    return get_week_nutrition_description(next_nutrition_plan_meal_id)
                else:
                    return "Следующий план питания не найден"
            else:
                return "Текущий план питания для данного пользователя не найден"
    except Exception as e:
        print("Произошла ошибка: " + str(e))
        return "Ошибка при получении данных"
    finally:
        conn.close()


def get_week_nutrition_description(nutrition_plan_meal_id: int) -> str:
    print(nutrition_plan_meal_id)
    #Получаем описание недельного плана питания по ID плана питания
    conn = connect()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT description FROM nutrition_week_plan WHERE nutrition_plan_meal_id = %s",
                (nutrition_plan_meal_id,)
            )
            result = cursor.fetchone()

            if result:
                return result[0]
            else:
                return "Описание не найдено"
    except Exception as e:
        print("Произошла ошибка при получении данных: " + str(e))
        return "Ошибка при получении данных"
    finally:
        conn.close()


def create_new_user_meal_plan(cursor, telegram_user_id, start_date):
    # Получение текущего nutrition_plan_meal_id
    cursor.execute("""
        SELECT week_number, nutrition_plan_meal_id
        FROM user_meal_plan
        WHERE telegram_user_id = %s
        ORDER BY end_date DESC
        LIMIT 1;
    """, (telegram_user_id,))
    result = cursor.fetchone()

    if result:
        current_week_number, current_nutrition_plan_meal_id = result

        # Определение следующего week_number
        next_week_number = 1 if current_week_number >= 4 else current_week_number + 1

        # Нахождение минимального id для следующего week_number
        cursor.execute("""
            SELECT MIN(id)
            FROM nutrition_plan_meal
            WHERE week_number = %s AND id > %s;
        """, (next_week_number, current_nutrition_plan_meal_id))
        next_nutrition_plan_meal_id_result = cursor.fetchone()

        if next_nutrition_plan_meal_id_result:
            next_nutrition_plan_meal_id = next_nutrition_plan_meal_id_result[0]

            # Создание новой записи в user_meal_plan
            new_end_date = start_date + timedelta(days=6)
            cursor.execute("""
                INSERT INTO user_meal_plan (telegram_user_id, week_number, start_date, end_date, nutrition_plan_meal_id)
                VALUES (%s, %s, %s, %s, %s);
            """, (telegram_user_id, next_week_number, start_date, new_end_date, next_nutrition_plan_meal_id))