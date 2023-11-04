from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from utils.states import Meal
from aiogram.filters import Command
from utils.db import connect, close
from os import getenv
from dotenv import load_dotenv
load_dotenv()
router = Router()
admin_id = getenv("ADMIN_ID")


@router.message(Command("add_meal"))
async def add_new_meal(message: Message, state: FSMContext):
    if message.from_user.id != int(admin_id):
        await message.answer("У тебя нет прав использовать эту команду")
    else:
        await state.set_state(Meal.name)
        await message.answer(text="Введи название приема пищи")


@router.message(Meal.name)
async def add_description(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Meal.description)
    await message.answer(text="Напиши описание приема пищи")


@router.message(Meal.description)
async def add_count_days(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(Meal.count_days)
    await message.answer(text="Напиши количество дней для текущего питания")


@router.message(Meal.count_days)
async def res(message: Message, state: FSMContext):
    await state.update_data(count_days=message.text)
    data = await state.get_data()
    conn = connect()
    try:
        with conn.cursor() as cursor:
            query = """
            INSERT INTO meals (meal_name, meal_description, count_active_days) VALUES (%s, %s, %s);
            """
            values = (
                data.get('name'), data.get('description'), data.get('count_days')
            )
            cursor.execute(query, values)
            conn.commit()

    except Exception as e:
        print("Error saving data to database:", e)
    finally:
        if conn:
            conn.close()

    await state.clear()
    await message.answer("Прием пищи успешно добавлен✅")



