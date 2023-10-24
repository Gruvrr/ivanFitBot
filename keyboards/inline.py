from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from utils.db import connect, close
from aiogram import Router, F
router = Router()
accept_button = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text="Принять",
            callback_data="accept"
        )
    ]
],
    resize_keyboard=True
)


gender_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Как к парню", callback_data="male"),
    ],
    [
        InlineKeyboardButton(text="Как к девушке", callback_data="female")
    ]
],
    resize_keyboard=True
)

subscribe_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Купить - 777 р", callback_data='pay'),
    ],
    [
        InlineKeyboardButton(text="Активировать промокод", callback_data="promocode")
    ],
    [
        InlineKeyboardButton(text="В главное меню", callback_data="main_menu")
    ]
]
)

main_menu_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text="Оплатить",
            callback_data="want_pay"
        )
    ],
    [
        InlineKeyboardButton(
            text="О проекте",
            callback_data="about"
        ),
        InlineKeyboardButton(
            text="Помощь",
            callback_data="help"
        )
    ]
])


success_trening_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text="Тренировки",
            callback_data="trening"
        ),
        InlineKeyboardButton(
            text="Питание",
            callback_data="meal"
        )
    ],
    [
        InlineKeyboardButton(text="Помощь", callback_data="help")
    ]
])


async def generate_meal_keyboard():
    conn = connect()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT meal_name FROM meals;")
        meals = cursor.fetchall()

        # Собираем все кнопки в список
        buttons = [InlineKeyboardButton(text=meal[0], callback_data=f"meal:{meal[0]}") for meal in meals]

        # Создаем InlineKeyboardMarkup, передавая кнопки как список списков
        keyboard_markup = InlineKeyboardMarkup(inline_keyboard=[buttons])

        return keyboard_markup

    except Exception as e:
        print(f"Error: {e}")
        return None

    finally:
        cursor.close()
        conn.close()

