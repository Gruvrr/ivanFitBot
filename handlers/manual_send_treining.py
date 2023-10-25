from aiogram import types, Router, Bot
from aiogram.types import Message
from utils.db import connect, close
import datetime
from os import getenv
import logging
from dotenv import load_dotenv

load_dotenv()  # Это нужно для того, чтобы загрузить переменные окружения из .env файла
admin_id = getenv("ADMIN_ID")


async def send_training_link_now(message: Message):
    if str(message.from_user.id) != admin_id:
        await message.answer("Эта команда для администратора!")
        return

    conn = connect()
    cursor = conn.cursor()
    try:
        today = datetime.datetime.now()
        cursor.execute("SELECT id FROM users WHERE is_subscription_active = TRUE")
        active_users = cursor.fetchall()
        if not active_users:
            logging.info("Нет пользователей с активной подпиской.")
        else:
            for user in active_users:
                user_id = user[0]
                # Проверяем, были ли уже отправлены какие-либо тренировки
                cursor.execute("""
                    SELECT MAX(training_number)
                    FROM user_trainings
                    WHERE user_id = %s AND is_sent = TRUE
                """, (user_id,))

                last_sent_training_number = cursor.fetchone()[0]

                if last_sent_training_number is None:
                    # Если тренировки не отправлялись, выбираем первую тренировку со статусом 'active'
                    cursor.execute("""
                        SELECT training_number, training_url
                        FROM training_links
                        WHERE status = 'active'
                        ORDER BY training_number ASC
                        LIMIT 1
                    """)
                else:
                    # Если тренировки отправлялись, выбираем следующую тренировку со статусом 'active'
                    cursor.execute("""
                        SELECT training_number, training_url
                        FROM training_links
                        WHERE status = 'active' AND training_number > %s
                        ORDER BY training_number ASC
                        LIMIT 1
                    """, (last_sent_training_number,))

                next_training = cursor.fetchone()

                if next_training:
                    training_number, training_url = next_training
                    logging.info(f"Sending training link to user {user_id}")
                    await message.answer(text=f'Тренировка №{training_number}: {training_url}')
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


async def send_training_link_first_time(message: Message):
    print("Сюда пришел")
    conn = connect()
    cursor = conn.cursor()
    try:
        today = datetime.datetime.now()
        cursor.execute("SELECT id FROM users WHERE is_subscription_active = TRUE")
        active_users = cursor.fetchall()
        if not active_users:
            logging.info("Нет пользователей с активной подпиской.")
        else:
            for user in active_users:
                user_id = user[0]
                # Проверяем, были ли уже отправлены какие-либо тренировки
                cursor.execute("""
                    SELECT MAX(training_number)
                    FROM user_trainings
                    WHERE user_id = %s AND is_sent = TRUE
                """, (user_id,))

                last_sent_training_number = cursor.fetchone()[0]

                if last_sent_training_number is None:
                    # Если тренировки не отправлялись, выбираем первую тренировку со статусом 'active'
                    cursor.execute("""
                        SELECT training_number, training_url
                        FROM training_links
                        WHERE status = 'active'
                        ORDER BY training_number ASC
                        LIMIT 1
                    """)
                else:
                    # Если тренировки отправлялись, выбираем следующую тренировку со статусом 'active'
                    cursor.execute("""
                        SELECT training_number, training_url
                        FROM training_links
                        WHERE status = 'active' AND training_number > %s
                        ORDER BY training_number ASC
                        LIMIT 1
                    """, (last_sent_training_number,))

                next_training = cursor.fetchone()

                if next_training:
                    training_number, training_url = next_training
                    logging.info(f"Sending training link to user {user_id}")
                    await message.answer(text=f'Тренировка №{training_number}: {training_url}')
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
