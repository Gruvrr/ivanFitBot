import logging

from aiogram.types import Message, CallbackQuery
from keyboards.inline import main_menu_keyboard
from aiogram import Router
from keyboards.inline import success_trening_keyboard
from typing import Union
from utils.db import connect, close
router = Router()


async def main_menu(message: Message):
    await message.answer(f"<b>Главное меню.</b> \n"
                         f"👉 Выберите действие:👈", reply_markup=main_menu_keyboard)


@router.callback_query(lambda c: c.data == "main_menu")
async def main_menu_not_subscription(callback: CallbackQuery):
    await callback.message.answer(text=f"<b>Главное меню.</b> \n"
                         f"👉 Выберите действие:👈", reply_markup=main_menu_keyboard)
    await callback.answer()


async def main_manu_sub(event: Union[Message, CallbackQuery], sub: int):
    if isinstance(event, Message):
        message = event
    else:
        message = event.message
    await message.answer(text=f"У тебя есть действующая подписка.\n"
                         f"До конца подписки осталось {sub}", reply_markup=success_trening_keyboard)


@router.callback_query(lambda c: c.data == "next3")
async def main_meny_subscription_days(callback: CallbackQuery) -> int:
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT subscription_days FROM users WHERE telegram_user_id = %s", (callback.from_user.id,))
        result = cursor.fetchone()
        await callback.message.answer(text=f"У тебя есть действующая подписка.\n"
                                  f"До конца подписки осталось {result[0]}", reply_markup=success_trening_keyboard)
    except Exception as e:
        print(f"[ERROR] {e}")
        logging.error(f"Error: {e}")
    finally:
        cursor.close()
        close(conn)


@router.callback_query(lambda c: c.data == "back_main_menu")
async def main_menu_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT is_subscription_active FROM users WHERE telegram_user_id = %s", (user_id,))
        result = cursor.fetchone()
        is_subscription_active = result[0]
        if is_subscription_active:
            await main_meny_subscription_days(callback)
        else:
            await main_menu_not_subscription(callback)

    except Exception as e:
        print(f"[ERROR] {e}")
        logging.error(f"Error: {e}")

    finally:
        cursor.close()
        close(conn)
