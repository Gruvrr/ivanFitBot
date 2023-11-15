import os
import pandas as pd
from aiogram import Bot, Router
from aiogram.types import Message, InputFile, BufferedInputFile
from aiogram.filters import Command
from utils.db import connect, close
from os import getenv
from dotenv import load_dotenv
load_dotenv()
router = Router()

admin_id = getenv("ADMIN_ID")
anna_id = getenv("ANNA_ID")


@router.message(Command('get_active_users'))
async def get_active_users(message: Message, bot: Bot):
    if str(message.from_user.id) == admin_id or str(message.from_user.id) == anna_id:

        chat_id = message.chat.id
        conn = connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id, telegram_user_id, gender, first_name, last_name, birth_date, phone_number, email, city, is_subscription_active 
                FROM users 
                WHERE is_subscription_active = true;
            """)
            rows = cursor.fetchall()

            df = pd.DataFrame(rows, columns=[
                "id", "telegram_user_id", "gender", "first_name", "last_name",
                "birth_date", "phone_number", "email", "city", "is_subscription_active"
            ])

            excel_filename = "active_users.xlsx"
            df.to_excel(excel_filename, index=False)

            # Создаем объект BufferedInputFile из файла
            document = BufferedInputFile.from_file(path=excel_filename)

            # Отправляем документ
            await bot.send_document(chat_id=chat_id, document=document)
        except Exception as e:
            await message.answer(f"Произошла ошибка: {e}")
        finally:
            cursor.close()
            close(conn)
    else:
        await message.answer("Эта команда только для администратора.")
        return