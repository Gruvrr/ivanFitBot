from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.dispatcher.router import Router
from utils.db import connect, close
from keyboards.inline import back_in_meal_menu

router = Router()


@router.callback_query(lambda c: c.data.startswith("meal_") if c.data else False)
async def handle_meal_selection(query: CallbackQuery):
    meal_id = query.data.split("_")[1]

    conn = connect()
    cursor = conn.cursor()

    try:
        # Запрос для получения описания приема пищи по ID
        cursor.execute("SELECT name, description FROM meals WHERE id = %s;", (meal_id,))
        meal_data = cursor.fetchone()

        if meal_data:
            meal_name, meal_description = meal_data
            await query.message.answer(
                f"{meal_name}\n\n{meal_description}", reply_markup=back_in_meal_menu)
        else:
            await query.message.answer("Прием пищи не найден.")

    except Exception as e:
        print(f"Error: {e}")
        await query.message.answer("Произошла ошибка при извлечении данных.")

    finally:
        cursor.close()
        close(conn)

    await query.answer()
