import datetime
from aiogram import Bot
from utils.db import connect, close
import logging
from dotenv import load_dotenv
from os import getenv

load_dotenv()
anna_id = getenv('ANNA_ID')


async def send_training_links(bot: Bot):
    conn = connect()
    cursor = conn.cursor()
    count = 0

    try:
        today = datetime.datetime.now()
        day_of_week = today.weekday()

        if day_of_week in [0, 2, 4]:  # Понедельник, Среда, Пятница
            cursor.execute("SELECT telegram_user_id FROM users WHERE is_subscription_active = TRUE")
            active_users = cursor.fetchall()
            print(active_users)

            for user in active_users:
                count += 1
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
                print(f"Это тренировка для отправки - {next_training}", )

                if next_training:
                    training_number, training_url = next_training
                    print(f"Сейчас отправится ссылка")

                    print(user_id)
                    await bot.send_message(chat_id=user_id, text=f'Ссылка на вашу тренировку: {training_url}')
                    print("Ссылка отправлена")

                    cursor.execute("""
                        INSERT INTO user_trainings (user_id, training_number, is_sent, sent_date)
                        VALUES (%s, %s, TRUE, %s)
                        ON CONFLICT (user_id, training_number)
                        DO UPDATE SET is_sent = TRUE, sent_date = %s;
                    """, (user_id, training_number, today, today))
                    conn.commit()
                else:
                    await bot.send_message(chat_id=user_id,
                                           text='На данный момент, вы прошли все тренировки. '
                                                'Новые тренировки появятся совсем скоро!')
            #await bot.send_message(chat_id=anna_id, text=f"Сегодня тренировки получили - {count} человек.")

    except Exception as e:
        logging.error(f"Error: {e}")
        conn.rollback()

    finally:
        cursor.close()
        close(conn)
