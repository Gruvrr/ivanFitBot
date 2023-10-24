import datetime
from aiogram import Bot
from utils.db import connect, close


async def send_training_links(bot: Bot):
    conn = connect()
    cursor = conn.cursor()

    try:
        today = datetime.datetime.now()
        day_of_week = today.weekday()

        if day_of_week in [0, 2, 4]:
            cursor.execute("SELECT id FROM users WHERE is_subscription_active = TRUE")
            active_users = cursor.fetchall()

            for user in active_users:
                user_id = user[0]

                cursor.execute("""
                    SELECT training_number, training_url
                    FROM user_trainings
                    JOIN training_links ON user_trainings.training_number = training_links.training_number
                    WHERE user_id = %s AND is_sent = FALSE
                    ORDER BY training_number ASC
                    LIMIT 1
                """, (user_id,))
                next_training = cursor.fetchone()

                if next_training:
                    training_number, training_url = next_training
                    await bot.send_message(chat_id=user_id, text=f'Ссылка на вашу тренировку: {training_url}')

                    cursor.execute("""
                        UPDATE user_trainings
                        SET is_sent = TRUE, sent_date = %s
                        WHERE user_id = %s AND training_number = %s
                    """, (today, user_id, training_number))
                    conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()

    finally:
        cursor.close()
        close(conn)
