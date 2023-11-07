from keyboards import inline
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from keyboards.inline import generate_meal_keyboard, next_button, next_button2, next_button3
from utils.db import connect, close

router = Router()


@router.callback_query(lambda c: c.data == "meal")
async def send_meal(callback: CallbackQuery):
    keyboard = await generate_meal_keyboard()
    if keyboard:
        await callback.message.answer(text=f"Питание для вас ⬇️⬇️⬇️", reply_markup=keyboard)
    else:
        await callback.message.answer("Нет питания")


async def send_breakfast(message: Message):
    meal_name: str = "Завтрак"
    conn = connect()
    cursor = conn.cursor()
    keyboard = next_button

    try:
        cursor.execute("SELECT meal_description FROM meals WHERE meal_name = %s;", (meal_name,))
        meal_description = cursor.fetchone()
        if meal_description:
            await message.answer(f"Описание для {meal_name}:\n\n{meal_description[0]}", reply_markup=keyboard)
        else:
            await message.answer(f"Описание для {meal_name} не найдено.")

    except Exception as e:
        print(f"Error: {e}")
        await message.answer("Произошла ошибка при извлечении данных.")

    finally:
        cursor.close()
        close(conn)


@router.callback_query(lambda c: c.data == "next1")
async def send_dinner(callback: CallbackQuery):
    meal_name = "Обед"
    conn = connect()
    cursor = conn.cursor()
    keyboard = next_button2

    try:
        cursor.execute("SELECT meal_description FROM meals WHERE meal_name = %s;", (meal_name,))
        meal_description = cursor.fetchone()
        if meal_description:
            await callback.message.answer(f"{meal_description[0]}", reply_markup=keyboard)
        else:
            await callback.message.answer(f"Описание для {meal_name} не найдено.")

    except Exception as e:
        print(f"Error: {e}")
        await callback.message.answer("Произошла ошибка при извлечении данных.")

    finally:
        cursor.close()
        close(conn)


@router.callback_query(lambda c: c.data == "next2")
async def send_supper(callback: CallbackQuery):
    meal_name = "Ужин"
    conn = connect()
    cursor = conn.cursor()
    keyboard = next_button3

    try:
        cursor.execute("SELECT meal_description FROM meals WHERE meal_name = %s;", (meal_name,))
        meal_description = cursor.fetchone()
        if meal_description:
            await callback.message.answer(f"{meal_description[0]}", reply_markup=keyboard)
        else:
            await callback.message.answer(f"Описание для {meal_name} не найдено.")

    except Exception as e:
        print(f"Error: {e}")
        await callback.message.answer("Произошла ошибка при извлечении данных.")

    finally:
        cursor.close()
        close(conn)
