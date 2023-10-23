from aiogram import Bot, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
import handlers.questionary
from keyboards import inline
from utils.db import connect, close
from handlers.main_menu import main_menu
router = Router()



@router.message(CommandStart())
async def get_start(message: Message):
    conn = connect()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT telegram_user_id from users WHERE telegram_user_id = {message.from_user.id}")
            if not cursor.fetchone():
                print("Начало выполнения функции get_start")
                await message.answer(text="Для продолжения прими пользовательское соглашение и публичную оферту ",
                                     reply_markup=inline.accept_button)
            else:
                await main_menu(message)
    except Exception as _ex:
        print("ERROR", _ex)
    finally:
        close(conn)
        print("[INFO] Postgresql connection close")


@router.callback_query(lambda c: c.data == "accept" or c.data == "want_pay")
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
                await callback_query.message.answer(f"Подписка на Проект 13 включает в себя:"
                                       f"▪️12 тренировок по 30-45 минут\n\n"
                                       f"▪️Меню на 4 недели\n"
                                       f"▪️Чат с единомышленниками\n" 
                                       f"▪️Прямые эфиры\n" 
                                       f"▪️Поддержка 24/7\n\n"
                                       f"После оплаты возможна задержка до 20 минут", reply_markup=inline.subscribe_keyboard
                                       )
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
                         f"Рад Видеть тебя на проекте 13\n"
                         f"Поздравляю, ты уже сделал первый шаг на пути к здоровому и подтянутому телу! \n"
                         f"Теперь вместе со мной ты будешь уверенно двигаться вперёд, становясь с каждым днём активнее, выносливее и сильнее 💪")