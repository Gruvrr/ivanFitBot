import logging
from aiogram import Bot
from utils.db import connect, close
from keyboards.inline import pay_button


async def manage_count_nutrition(bot: Bot):
        conn = connect()
        cursor = conn.cursor()
        try:
            # Получаем значение count_active_days из таблицы meals
            cursor.execute("SELECT count_active_days FROM meals")
            count_active_days = cursor.fetchone()[0]

            if count_active_days == 2:
                # Если count_active_days равно 2, получаем список пользователей с активной подпиской
                cursor.execute(
                    "SELECT telegram_user_id FROM users WHERE is_subscription_active = True"
                )
                users = cursor.fetchall()

                # Отправляем сообщение каждому пользователю
                for user in users:
                    telegram_user_id = user[0]
                    await bot.send_message(
                        telegram_user_id,
                        "Через 2 дня обновится план питания."
                    )

        except Exception as e:
            logging.error(f"Error in update_meal_plan_notifications: {e}")

        finally:
            cursor.close()
            close(conn)


async def manage_subscriptions(bot: Bot):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT telegram_user_id, subscription_days FROM users WHERE is_subscription_active = True"
        )
        users = cursor.fetchall()

        for user in users:
            telegram_user_id, subscription_days = user
            new_subscription_days = subscription_days - 1

            if new_subscription_days <= 0:
                new_subscription_days = 0
                cursor.execute(
                    "UPDATE users SET is_subscription_active = False, subscription_days = %s WHERE telegram_user_id = %s",
                    (new_subscription_days, telegram_user_id)
                )
            else:
                cursor.execute(
                    "UPDATE users SET subscription_days = %s WHERE telegram_user_id = %s",
                    (new_subscription_days, telegram_user_id)
                )

            if new_subscription_days == 2:
                await bot.send_message(telegram_user_id, "Ваша подписка закончится через 2 дня.", reply_markup=pay_button)

        conn.commit()

    except Exception as e:
        logging.error(f"Error in manage_subscriptions: {e}")

    finally:
        cursor.close()
        close(conn)
