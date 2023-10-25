import logging
from aiogram import Bot
from utils.db import connect, close


async def manage_subscriptions(bot: Bot):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT telegram_user_id, days_left FROM users WHERE is_subscription_active = True")
        users = cursor.fetchall()

        for user in users:
            telegram_user_id, days_left = user
            new_days_left = days_left - 1

            if new_days_left <= 0:
                new_days_left = 0
                cursor.execute(
                    "UPDATE users SET is_subscription_active = False, days_left = %s WHERE telegram_user_id = %s",
                    (new_days_left, telegram_user_id))
            else:
                cursor.execute("UPDATE users SET days_left = %s WHERE telegram_user_id = %s",
                               (new_days_left, telegram_user_id))

            if new_days_left == 2:
                await bot.send_message(telegram_user_id, "Ваша подписка закончится через 2 дня.")

        conn.commit()

    except Exception as e:
        logging.error(f"Error in manage_subscriptions: {e}")

    finally:
        cursor.close()
        close(conn)
