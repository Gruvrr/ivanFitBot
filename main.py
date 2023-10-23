import asyncio
import logging
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from os import getenv
from dotenv import load_dotenv
from keyboards import inline
from handlers import handler, questionary, pay, promocode



load_dotenv()

dp = Dispatcher()
token = getenv('TOKEN')
admin_id = getenv("ADMIN_ID")

print(f"{token}, Admin_id = {admin_id}")


async def start_bot(bot: Bot):
    await bot.send_message(admin_id, text="Bot is start")


async def stop_bot(bot: Bot):
    await bot.send_message(admin_id, text="Бот остановлен")


async def start():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - [%(levelname)s] = %(name)s - "
                               "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s")
    bot = Bot(token=token, parse_mode='HTML')
    dp.message.register(handler.get_start, Command("start"))
    dp.callback_query(handler.hello_msg, lambda c: c.data == "accept")
    dp.include_routers(questionary.router,
                                handler.router,
                                pay.router)
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(start())
