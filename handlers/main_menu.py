from aiogram.types import Message
from keyboards.inline import main_menu_keyboard


async def main_menu(message: Message):
    await message.answer(f"<b>Главное меню.</b> \n"
                         f"👉 Выберите действие:👈", reply_markup=main_menu_keyboard)
