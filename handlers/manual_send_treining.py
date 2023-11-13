from aiogram import types, Router, Bot
from aiogram.types import Message
from utils.db import connect, close
import datetime
from os import getenv
import logging
from dotenv import load_dotenv

load_dotenv()  # Это нужно для того, чтобы загрузить переменные окружения из .env файла
admin_id = getenv("ADMIN_ID")


async def send_training_link_now(message: Message, bot: Bot):
    if str(message.from_user.id) != admin_id:
        await message.answer("Эта команда для администратора!")
        return

    conn = connect()
    cursor = conn.cursor()
    try:
        today = datetime.datetime.now()
        cursor.execute("SELECT telegram_user_id FROM users WHERE is_subscription_active = TRUE")
        active_users = cursor.fetchall()
        logging.info(f"Found {len(active_users)} active users.")
        for user in active_users:
            user_id = user[0]
            cursor.execute("""
                    SELECT MAX(training_number)
                    FROM user_trainings
                    WHERE user_id = %s AND is_sent = TRUE
                """, (user_id,))
            last_sent_training_number = cursor.fetchone()[0]
            if last_sent_training_number is None:
                logging.info(f"No trainings sent previously for user {user_id}. Fetching first active training.")
                cursor.execute("""
                        SELECT id, training_number, training_url
                        FROM training_links
                        WHERE status = 'active'
                        ORDER BY training_number ASC
                        LIMIT 1
                    """)
                next_training = cursor.fetchone()
                if next_training:
                    id, training_number, training_url = next_training
                    logging.info(f"Sending training link {training_url} to user {user_id}")
                    await bot.send_message(chat_id=user_id, text=f'{training_url}')
                    cursor.execute("""
                            INSERT INTO user_trainings (user_id, training_number, training_id, is_sent, sent_date)
                            VALUES (%s, %s, %s, TRUE, %s)
                        """, (user_id, training_number, id, today))
                    conn.commit()
    except Exception as e:
        logging.error(f"Error in send_training_links: {e}")
        conn.rollback()
    finally:
        cursor.close()
        close(conn)
        logging.info("Database connection closed.")


async def send_training_link_first_time(message: Message, user_id):
    conn = connect()
    cursor = conn.cursor()
    try:
        today = datetime.datetime.now()
        # Проверяем, активна ли подписка у пользователя
        cursor.execute("""
            SELECT id FROM users WHERE is_subscription_active = TRUE AND telegram_user_id = %s
        """, (user_id,))
        user = cursor.fetchone()
        print(user)
        if user is None:
            logging.info(f"Пользователь с id {user_id} не имеет активной подписки.")
        else:
            # Выбираем первую тренировку со статусом 'active', которая не была отправлена пользователю
            cursor.execute("""
                SELECT tl.training_number, tl.training_url
                FROM training_links tl
                WHERE tl.status = 'active' AND tl.training_number NOT IN (
                    SELECT ut.training_number
                    FROM user_trainings ut
                    WHERE ut.user_id = %s AND ut.is_sent = TRUE
                )
                ORDER BY tl.training_number ASC
                LIMIT 1
            """, (user_id,))

            next_training = cursor.fetchone()

            if next_training:
                training_number, training_url = next_training
                logging.info(f"Sending training link to user {user_id}")
                # Отправляем сообщение пользователю со ссылкой на тренировку
                await message.answer(text=f'{training_number}: {training_url}')
                # Вставляем запись о тренировке в user_trainings
                cursor.execute("""
                    INSERT INTO user_trainings (user_id, training_number, is_sent, sent_date)
                    VALUES (%s, %s, TRUE, %s)
                    ON CONFLICT (user_id, training_number)
                    DO UPDATE SET is_sent = TRUE, sent_date = %s;
                """, (user_id, training_number, today, today))
                conn.commit()
                logging.info(f"Training link sent and user_trainings table updated for user {user_id}")
            else:
                logging.info(f"No active training link found for user {user_id}")

    except Exception as e:
        logging.error(f"Error: {e}")
        conn.rollback()

    finally:
        cursor.close()
        close(conn)

