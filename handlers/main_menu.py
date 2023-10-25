from aiogram.types import Message, CallbackQuery
from keyboards.inline import main_menu_keyboard
from aiogram import Router
from keyboards.inline import success_trening_keyboard
from typing import Union
router = Router()


async def main_menu(message: Message):
    await message.answer(f"<b>Главное меню.</b> \n"
                         f"👉 Выберите действие:👈", reply_markup=main_menu_keyboard)


@router.callback_query(lambda c: c.data == "main_menu")
async def main_menu_callback(callback: CallbackQuery):
    await callback.message.answer(f"<b>Главное меню.</b> \n"
                         f"👉 Выберите действие:👈", reply_markup=main_menu_keyboard)
    await callback.answer()


async def main_manu_sub(event: Union[Message, CallbackQuery], sub: int):
    if isinstance(event, Message):
        message = event
    else:
        message = event.message
    await message.answer(f"У тебя есть действующая подписка.\n"
                         f"До конца подписки осталось {sub}", reply_markup=success_trening_keyboard)
