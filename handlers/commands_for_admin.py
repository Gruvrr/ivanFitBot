import pandas as pd
from aiogram import Bot, Router
from aiogram.types import Message
from utils.db import connect, close

router = Router()


@router.message(commands=['get_active_users'])
async def get_active_users(message: Message, bot:Bot):
    conn = connect()  # Устанавливаем соединение с базой данных
    cursor = conn.cursor()
    try:
        # Выполняем запрос к базе данных
        cursor.execute("""
            SELECT id, telegram_user_id, gender, first_name, last_name, birth_date, phone_number, email, city, is_subscription_active 
            FROM users 
            WHERE is_subscription_active = true;
        """)
        rows = cursor.fetchall()

        # Преобразуем результат в DataFrame
        df = pd.DataFrame(rows, columns=["id", "telegram_user_id", "gender", "first_name", "last_name", "birth_date",
                                         "phone_number", "email", "city", "is_subscription_active"])

        # Сохраняем DataFrame в Excel-файл
        excel_filename = "active_users.xlsx"
        df.to_excel(excel_filename, index=False)

        # Отправляем файл пользователю
        with open(excel_filename, 'rb') as file:
            await bot.send_document(chat_id=message.chat.id, document=file)
    except Exception as e:
        await message.reply(f"Произошла ошибка: {e}")
    finally:
        cursor.close()
        close(conn)

