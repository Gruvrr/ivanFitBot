import logging
from aiogram import Bot
from utils.db import connect, close
from keyboards.inline import pay_button


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
