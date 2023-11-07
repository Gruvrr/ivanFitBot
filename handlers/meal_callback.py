# meal_callback.py
from aiogram import Dispatcher
from aiogram.types import CallbackQuery
from aiogram import Router, F
from utils.db import connect, close
from keyboards.inline import generate_meal_keyboard

router = Router()
dp = Dispatcher()


@router.callback_query(lambda c: c.data.startswith('meal:'))
async def on_meal_button_press(callback_query: CallbackQuery):
    meal_name = callback_query.data.split(':')[1]
    conn = connect()
    cursor = conn.cursor()
    keyboard = await generate_meal_keyboard()

    try:
        cursor.execute("SELECT meal_description FROM meals WHERE meal_name = %s;", (meal_name,))
        meal_description = cursor.fetchone()
        if meal_description:
            await callback_query.message.answer(f"Описание для {meal_name}:\n\n{meal_description[0]}", reply_markup=keyboard)
        else:
            await callback_query.message.answer(f"Описание для {meal_name} не найдено.", reply_markup=keyboard)

    except Exception as e:
        print(f"Error: {e}")
        await callback_query.message.answer("Произошла ошибка при извлечении данных.", reply_markup=keyboard)

    finally:
        cursor.close()
        close(conn)

    await callback_query.answer()
