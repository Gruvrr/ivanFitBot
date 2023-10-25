import time
from handlers.handler import start_msg
from aiogram import Router
from aiogram.types import Message

from handlers.manual_send_treining import send_training_link_first_time
from handlers.meal_handler import send_breakfast

router = Router


async def send_messages_after_pay(message: Message):
    time.sleep(3)
    await start_msg(message)
    time.sleep(4)
    await message.answer(f"В проекте тебя ждёт:\n"
                         f"▪️12 тренировок по 30-45 минут\n"
                         f"▪️Меню на 4 недели\n"
                         f"▪️Чат с единомышленниками \n"
                         f"▪️Прямые эфиры \n"
                         f"▪️Поддержка 24/7")
    time.sleep(5)
    await send_training_link_first_time(message)
    time.sleep(5)
    await message.answer(f"Питание - это  50% успеха!🔥 \n"
                         f"Поэтому четко соблюдайте рацион, и вы получите результат, о котором даже не мечтали!💃\n"
                         f"План питания на ближайшие 7 дней!")
    time.sleep(3)
    await send_breakfast(message)