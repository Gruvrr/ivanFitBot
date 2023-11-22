from aiogram import Router
from aiogram.types import Message
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
        await state.set_state(Meal.is_new_cycle)
        await message.answer(text="Начинается новый цикл? (да/нет)")


@router.message(Meal.is_new_cycle)
async def check_new_cycle(message: Message, state: FSMContext):
    if message.text.lower() == 'да':
        await state.update_data(is_new_cycle=True)
    else:
        await state.update_data(is_new_cycle=False)
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
    await state.set_state(Meal.week_number)
    await message.answer(text="Напиши номер недели для этого питания")


@router.message(Meal.week_number)
async def res(message: Message, state: FSMContext):
    await state.update_data(week_number=message.text)
    data = await state.get_data()
    conn = connect()
    try:
        with conn.cursor() as cursor:
            if data.get('is_new_cycle'):
                cursor.execute("""UPDATE nutrition_plan_meal SET is_active = %s;""", (False,))
            # Добавление в таблицу meals
            query_meals = """
            INSERT INTO meals (name, description) VALUES (%s, %s) RETURNING id;
            """
            values_meals = (
                data.get('name'), data.get('description')
            )
            cursor.execute(query_meals, values_meals)
            meal_id = cursor.fetchone()[0]  # Получение ID вставленного приема пищи

            # Добавление в таблицу nutrition_plan_meal
            query_nutrition_plan = """
            INSERT INTO nutrition_plan_meal (week_number, mealid, date_add, is_active) VALUES (%s, %s, CURRENT_DATE, %s);
            """
            values_nutrition_plan = (
                data.get('week_number'), meal_id, True
            )
            cursor.execute(query_nutrition_plan, values_nutrition_plan)

            conn.commit()

    except Exception as e:
        print("Error saving data to database:", e)
    finally:
        if conn:
            conn.close()

    await state.clear()
    await message.answer("Прием пищи успешно добавлен✅")




