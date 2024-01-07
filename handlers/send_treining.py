import datetime
import time

from aiogram import Bot
from utils.db import connect, close
from dotenv import load_dotenv
from os import getenv
import logging


load_dotenv()
anna_id = getenv('ANNA_ID')
admin_id = getenv('ADMIN_ID')


async def send_training_links(bot: Bot):
    conn = connect()
    cursor = conn.cursor()
    count = 0

    try:
        today = datetime.datetime.now()
        day_of_week = today.weekday()
        logging.info(f"Starting send_training_links for day of week: {day_of_week}")

        if day_of_week in [0, 2, 4]:  # Понедельник, Среда, Пятница
            cursor.execute("SELECT telegram_user_id FROM users WHERE is_subscription_active = TRUE")
            active_users = cursor.fetchall()
            logging.info(f"Found {len(active_users)} active users.")
            try:
                for user in active_users:

                    count += 1
                    user_id = user[0]
                    logging.info(f"Starting processing user: {user_id}")
                    logging.info(f"Processing user: {user_id}")

                    # Проверяем, были ли уже отправлены какие-либо тренировки
                    try:
                        cursor.execute("""
                            SELECT MAX(training_number)
                            FROM user_trainings
                            WHERE user_id = %s AND is_sent = TRUE
                        """, (user_id,))
                        last_sent_training_number = cursor.fetchone()[0]
                        logging.info(f"Last sent training number for user {user_id}: {last_sent_training_number}")

                        if last_sent_training_number is None:
                            logging.info(f"No trainings sent previously for user {user_id}. Fetching first active training.")
                            cursor.execute("""
                                SELECT id, training_number, training_url
                                FROM training_links
                                WHERE status = 'active'
                                ORDER BY training_number ASC
                                LIMIT 1
                            """)

                        else:
                            logging.info(f"Fetching next training for user {user_id}")
                            cursor.execute("""
                                SELECT t1.id, t1.training_number, t1.training_url
                                FROM training_links t1
                                WHERE t1.id > (
                                    SELECT ut.training_id
                                    FROM user_trainings ut
                                    WHERE ut.user_id = %s AND ut.is_sent = TRUE
                                    ORDER BY ut.training_id DESC
                                    LIMIT 1
                                )
                                ORDER BY t1.id ASC
                                LIMIT 1
                            """, (user_id,))

                        next_training = cursor.fetchone()
                        logging.info(f"Next training for user {user_id}: {next_training}")

                        if next_training:
                            id, training_number, training_url = next_training

                            await bot.send_message(chat_id=user_id, text=f'{training_url}')
                            cursor.execute("""
                                    INSERT INTO user_trainings (user_id, training_number, training_id, is_sent, sent_date)
                                    VALUES (%s, %s, %s, TRUE, %s)
                                    ON CONFLICT (user_id, training_number)
                                    DO UPDATE SET is_sent = TRUE, sent_date = %s, training_id = %s;
                                """, (user_id, training_number, id, today, today, id))
                            conn.commit()
                            logging.info(f"Finished processing user: {user_id}")
                        else:
                            logging.info(f"User {user_id} has completed all trainings. Sending message.")
                            await bot.send_message(chat_id=user_id,
                                                   text='На данный момент, вы прошли все тренировки. '
                                                        'Новые тренировки появятся совсем скоро!')
                    except Exception as e:
                        logging.error(f"Error while processing user {user_id}: {e}")
                        continue
            except Exception as e:
                logging.error(f"Error in circle for: {e}")

    except Exception as e:
        logging.error(f"Error in send_training_links: {e}")
        conn.rollback()

    finally:
        await bot.send_message(chat_id=anna_id, text=f"Сегодня тренировки получили - {count} человек.")
        await bot.send_message(chat_id=admin_id, text=f"Сегодня тренировки получили - {count} человек.")
        cursor.close()
        close(conn)
        logging.info("Database connection closed.")
