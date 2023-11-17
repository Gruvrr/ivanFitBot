from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from utils.states import WeekNutrition
from aiogram.filters import Command
from utils.db import connect, close
from os import getenv
from dotenv import load_dotenv
load_dotenv()
router = Router()
admin_id = getenv("ADMIN_ID")


@router.message(Command('add_week_nutrition'))
async def add_nutrition_plan_meal_id(message: Message, state: FSMContext):
    if message.from_user.id != int(admin_id):
        await message.answer("У тебя нет прав использовать эту команду")
    else:
        await state.set_state(WeekNutrition.nutrition_plan_meal_id)
        await message.answer(text="Введи айди из таблицы nutrition_plan_meal")


@router.message(WeekNutrition.nutrition_plan_meal_id)
async def add_description(message: Message, state: FSMContext):
    await state.update_data(nutrition_plan_meal_id=message.text)
    await state.set_state(WeekNutrition.description)
    await message.answer(text="Напиши описания для недельного питания")


@router.message(WeekNutrition.description)
async def add_week_nutrition(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    data = await state.get_data()
    nutrition_plan_meal_id = data.get('nutrition_plan_meal_id')
    description = data.get('description')
    conn = connect()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO nutrition_week_plan (nutrition_plan_meal_id, description) VALUES (%s, %s)",
                (nutrition_plan_meal_id, description)
            )
            conn.commit()
            await message.answer("Данные успешно добавлены в таблицу.")
    except Exception as e:
        await message.answer("Произошла ошибка при добавлении данных: " + str(e))
    finally:
        close(conn)
        await state.clear()