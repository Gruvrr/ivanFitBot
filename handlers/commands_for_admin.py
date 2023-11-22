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
                SELECT 
                    u.id, 
                    u.telegram_user_id, 
                    u.gender, 
                    u.first_name, 
                    u.last_name, 
                    u.birth_date, 
                    u.phone_number, 
                    u.email, 
                    u.city, 
                    u.is_subscription_active,
                    ump.week_number AS "номер недели питания",
                    ump.start_date AS "дата начала питания",
                    ump.end_date AS "дата окончания питания",
                    MAX(p.timestamp) AS "дата последней оплаты"
                FROM users u
                LEFT JOIN user_meal_plan ump ON u.telegram_user_id = ump.telegram_user_id
                LEFT JOIN payments p ON u.telegram_user_id = p.telegram_user_id
                WHERE u.is_subscription_active = true
                GROUP BY u.id, ump.week_number, ump.start_date, ump.end_date
                ORDER BY u.id;
            """)
            rows = cursor.fetchall()

            df = pd.DataFrame(rows, columns=[
                "id", "telegram_user_id", "gender", "first_name", "last_name",
                "birth_date", "phone_number", "email", "city", "is_subscription_active", "номер недели питания",
                "дата начала питания", "дата окончания питания", "дата последней оплаты"
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