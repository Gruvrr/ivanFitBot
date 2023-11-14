import logging
import time
from aiogram import Bot, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
import handlers.questionary
from keyboards import inline
from utils.db import connect, close
from handlers.main_menu import main_menu, main_manu_sub
from typing import Union
from os import getenv
from dotenv import load_dotenv

load_dotenv()
router = Router()
admin_id = getenv("ADMIN_ID")


@router.message(Command('menu'))
async def send_menu(message: Message):
    if str(message.from_user.id) == admin_id:
        buttons = [
            [KeyboardButton(text=command) for command in ["/add_link", "/add_meal"]],
            [KeyboardButton(text=command) for command in ["/create_user", "/send_training"]]
        ]
        markup = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
        await message.answer("Выберите команду:", reply_markup=markup)
    else:
        await message.answer("У вас нет доступа к этому меню.")


@router.message(CommandStart())
async def get_start(event: Union[Message, CallbackQuery]):
    if isinstance(event, Message):
        message = event
    else:
        message = event.message
    conn = connect()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT telegram_user_id, subscription_days from users WHERE telegram_user_id = {message.from_user.id}")
            logging.info("Connected to the database")
            result = cursor.fetchone()
            time.sleep(1)
            if not result:
                print("Начало выполнения функции get_start")
                await message.answer(
                    text="Для продолжения прими <a href='https://drive.google.com/file/d/1U99TKxSujWCUsdDMbeBEWDy0skMLxWdV/view?usp=sharing'>политику конфиденциальности</a> и <a href='https://drive.google.com/file/d/1s95OsgiqLXni3uwudW_Ts5F2-9bg_rOF/view?usp=sharing'>публичную оферту</a>",
                    parse_mode='HTML',
                                     reply_markup=inline.accept_button)
            else:
                user_id, subscription_days = result

                if subscription_days != 0:
                    await main_manu_sub(message, subscription_days)
                else:
                    await main_menu(message)
    except Exception as _ex:
        print("ERROR", _ex)
    finally:
        close(conn)
        print("[INFO] Postgresql connection close")


@router.callback_query(lambda c: c.data == "accept" or c.data == "want_pay" or c.data == "about")
async def hello_msg(callback_query: CallbackQuery, bot: Bot, state: FSMContext):
    conn = connect()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT telegram_user_id from users WHERE telegram_user_id = {callback_query.from_user.id}")
            if not cursor.fetchone():
                print("Начало выполнения функции hello_msg")
                await handlers.questionary.new_profile(callback_query.message, state)
                await callback_query.answer()
            else:
                await callback_query.message.answer(f'Подписка на "Проект 13" включает в себя:\n'
                                       f"▪️12 тренировок по 25-45 минут\n"
                                       f"▪️Меню на 4 недели\n"
                                       f"▪️Чат с единомышленниками\n" 
                                       f"▪️Поддержка 24/7\n\n"
                                       f"После оплаты возможна задержка до 20 минут", reply_markup=inline.subscribe_keyboard
                                       )
                await callback_query.answer()
    except Exception as _ex:
        print("ERROR", _ex)
    finally:
        close(conn)
        print("[INFO] Postgresql connection close")


async def start_msg(message: Message):
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT first_name from users WHERE telegram_user_id = {message.from_user.id}")
        first_name = cursor.fetchone()[0]
        print(first_name)
    await message.answer(f"Привет, {first_name}\n"
                         f'Рад Видеть тебя на "Проекте 13"\n'
                         f"Поздравляю, это твой первый шаг на пути к здоровому и подтянутому телу! \n"
                         f"Теперь мы вместе будем уверенно двигаться вперёд, становясь с каждым днём красивее, активнее и выносливее💪")


