import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from os import getenv
from dotenv import load_dotenv
from keyboards import inline
from handlers import (handler, questionary, pay, promocode, main_menu, add_links, send_treining, manual_send_treining,
                      add_nutrition, meal_handler, meal_callback, help, new_user, meal_check, commands_for_admin, add_week_nutrition)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from handlers.subscription_manager import manage_subscriptions


load_dotenv()

dp = Dispatcher()
token = getenv('TOKEN')
admin_id = getenv("ADMIN_ID")


async def start_bot(bot: Bot):
    await bot.send_message(admin_id, text="Bot is start")


async def stop_bot(bot: Bot):
    await bot.send_message(admin_id, text="Бот остановлен")


async def start():

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - [%(levelname)s] = %(name)s - "
                               "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s",
                        handlers=[logging.FileHandler("bot_logs.log", 'a', 'utf-8'),
                                  logging.StreamHandler()])
    bot = Bot(token=token, parse_mode='HTML')
    dp.message.register(handler.get_start, Command("start"))
    dp.message.register(manual_send_treining.send_training_link_now, Command("send_training"))
    dp.callback_query(handler.hello_msg, lambda c: c.data == "accept")
    dp.include_routers( handler.router, pay.router, main_menu.router, add_links.router,
                                add_nutrition.router, inline.router, meal_handler.router, meal_callback.router,
                                help.router, new_user.router, questionary.router, commands_for_admin.router, add_week_nutrition.router)
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_treining.send_training_links, args=[bot], trigger='cron', day_of_week='mon,wed,fri', hour=6)
    scheduler.add_job(manage_subscriptions, args=[bot], trigger='cron', day_of_week='mon,tue,wed,thu,fri,sat,sun', hour=9)
    scheduler.add_job(meal_check.check_meal_every_day, args=[bot], trigger='cron', day_of_week='mon,tue,wed,thu,fri,sat,sun', hour=10)
    scheduler.start()
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(start())
