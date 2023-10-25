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


back_in_main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text="Назад, в главное меню",
            callback_data="command: start"
        )
    ]
],
    resize_keyboard=True
)


gender_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Мужской", callback_data="male"),
    ],
    [
        InlineKeyboardButton(text="Женский", callback_data="female")
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
        back_button = [InlineKeyboardButton(text="Вернуться в главное меню", callback_data="back_main_menu")]

        # Создаем InlineKeyboardMarkup, передавая кнопки как список списков
        keyboard_markup = InlineKeyboardMarkup(inline_keyboard=[buttons, back_button])

        return keyboard_markup

    except Exception as e:
        print(f"Error: {e}")
        return None

    finally:
        cursor.close()
        conn.close()

next_button = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text="Далее",
            callback_data="next1"
        )
    ]
],
    resize_keyboard=True
)


next_button2 = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text="Далее",
            callback_data="next2"
        )
    ]
],
    resize_keyboard=True
)


next_button3 = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text="Далее",
            callback_data="next3"
        )
    ]
],
    resize_keyboard=True
)