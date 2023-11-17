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
                # Создание новой записи в user_meal_plan

                new_start_date = datetime.now().date() + timedelta(days=1)
                create_new_user_meal_plan(cursor, telegram_user_id, new_start_date)
                await bot.send_message(telegram_user_id, text=f"""Ваш план питания изменен!""")
                time.sleep(1)
                await manage_nutrition(telegram_user_id, bot)

            elif end_date == datetime.now().date() + timedelta(days=2):
                # План питания изменится через два дня
                await bot.send_message(telegram_user_id, f"Ваш план питания изменится через два дня."
                                                         f"Подготовьте, пожалуйста,  продукты на следующие 7 дней.")
                description_meal = get_next_nutrition_plan_description(telegram_user_id)
                await bot.send_message(telegram_user_id, text=description_meal)

        conn.commit()

    except Exception as e:
        print(f"Произошла ошибка: {e}")
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
    """ Получаем описание недельного плана питания по ID плана питания. """
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
        SELECT week_number
        FROM user_meal_plan
        WHERE telegram_user_id = %s
        ORDER BY end_date DESC
        LIMIT 1;
    """, (telegram_user_id,))
    result = cursor.fetchone()

    if result:
        current_week_number = result[0]

        # Определение следующего week_number
        next_week_number = 1 if current_week_number >= 4 else current_week_number + 1

        # Нахождение минимального id для следующего week_number
        cursor.execute("""
            SELECT MIN(id)
            FROM nutrition_plan_meal
            WHERE week_number = %s;
        """, (next_week_number,))
        next_nutrition_plan_meal_id_result = cursor.fetchone()

        if next_nutrition_plan_meal_id_result:
            next_nutrition_plan_meal_id = next_nutrition_plan_meal_id_result[0]

            # Создание новой записи в user_meal_plan
            new_end_date = start_date + timedelta(days=7)
            cursor.execute("""
                INSERT INTO user_meal_plan (telegram_user_id, week_number, start_date, end_date, nutrition_plan_meal_id)
                VALUES (%s, %s, %s, %s, %s);
            """, (telegram_user_id, next_week_number, start_date, new_end_date, next_nutrition_plan_meal_id))