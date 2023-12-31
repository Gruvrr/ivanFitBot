from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from utils.states import Link
from aiogram.filters import Command
from utils.db import connect, close
from os import getenv
from dotenv import load_dotenv
load_dotenv()
router = Router()
admin_id = int(getenv("ADMIN_ID"))


@router.message(Command("add_link"))
async def add_training_number(message: Message, state: FSMContext):
    print(type(admin_id), type(message.from_user.id))
    if message.from_user.id != int(admin_id):
        await message.answer("У тебя нет прав использовать эту команду")
    else:
        await state.set_state(Link.number)
        await message.answer(text="Введи номер тренировки")


@router.message(Link.number)
async def add_link(message: Message, state: FSMContext):
    await state.update_data(number=message.text)
    await state.set_state(Link.link)
    await message.answer(text="Введи ссылку на тренировку")


@router.message(Link.link)
async def res(message: Message, state: FSMContext):
    await state.update_data(link=message.text)
    data = await state.get_data()
    conn = connect()
    try:
        with conn.cursor() as cursor:
            # Добавление новой ссылки
            query = """
            INSERT INTO training_links (training_url, training_number, status, date_added)
            VALUES (%s, %s, 'active', NOW());
            """
            values = (data.get('link'), data.get('number'))
            cursor.execute(query, values)
            conn.commit()

            # Проверка количества ссылок и обновление статуса 13-й ссылки при необходимости
            query = """
            WITH ranked_links AS (
                SELECT id, ROW_NUMBER() OVER (ORDER BY date_added DESC) as rn
                FROM training_links
            )
            UPDATE training_links
            SET status = 'notactive'
            WHERE id IN (SELECT id FROM ranked_links WHERE rn = 13);
            """
            cursor.execute(query)
            conn.commit()

    except Exception as e:
        print("Error saving data to database:", e)
    finally:
        if conn:
            conn.close()

    await state.clear()
    await message.answer("Ссылка успешно добавлена✅")



@router.message(Command("get_links"))
async def get_all_links(message: Message):
    if message.from_user.id != admin_id:
        await message.answer(f"это команда для администратора бота")
    else:
        conn = connect()
        try:
            with conn.cursor() as cursor:
                query = """
                SELECT training_number FROM training_links;"""
                cursor.execute(query)
                number = cursor.fetchall()
                number_text = "\n".join(str(num[0]) for num in number)
                await message.answer(number_text)
        except Exception as e:
            print(f"Error: {e}")
            await message.answer(f"Произошла ошибка: {e}")
        finally:
            close(conn)

