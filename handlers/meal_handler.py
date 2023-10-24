from keyboards import inline
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from keyboards.inline import generate_meal_keyboard

router = Router()


@router.callback_query(lambda c: c.data == "meal")
async def send_meal(callback: CallbackQuery):
    keyboard = await generate_meal_keyboard()
    if keyboard:
        await callback.message.answer(text="Сработало питание", reply_markup=keyboard )
    else:
        await callback.message.answer("Нет питания")