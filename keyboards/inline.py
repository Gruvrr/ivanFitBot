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
        InlineKeyboardButton(text="Купить - 777 🛒", callback_data='pay'),
    ],
    [
        InlineKeyboardButton(text="Активировать промокод 🎁", callback_data="promocode")
    ],
    [
        InlineKeyboardButton(text="В главное меню 🔙", callback_data="main_menu")
    ]
]
)

main_menu_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text="Оплатить 💵",
            callback_data="want_pay"
        )
    ],
    [
        InlineKeyboardButton(
            text="О проекте 💪",
            callback_data="about"
        ),
        InlineKeyboardButton(
            text="Помощь ❓",
            callback_data="help"
        )
    ]
])


success_trening_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text="Тренировки 🏃🏻‍♂️",
            callback_data="training"
        ),
        InlineKeyboardButton(
            text="Питание 🍏",
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
            text="Далее ➡️",
            callback_data="next1"
        )
    ]
],
    resize_keyboard=True
)


next_button2 = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text="Далее ➡️",
            callback_data="next2"
        )
    ]
],
    resize_keyboard=True
)


next_button3 = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text="Далее ➡️",
            callback_data="next3"
        )
    ]
],
    resize_keyboard=True
)


help_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Общение 🗣", callback_data="speak"),
        InlineKeyboardButton(text="Вопрос/Ответ 🆘", callback_data="qwestion/answer")
    ],
    [
        InlineKeyboardButton(text="Получить быстрый ответ ❓", callback_data="quick_answer")
    ],
    [
        InlineKeyboardButton(text="Проблема с оплатой 💸", callback_data="problem_pay")
    ],
    [
        InlineKeyboardButton(text="Назад 🔙", callback_data="back_main_menu")
    ]
])


question_answer_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Питание 🍏", callback_data="meal_question"),
        InlineKeyboardButton(text="Тренировки 🏃", callback_data="training_question")
    ],
    [
        InlineKeyboardButton(text="В главное меню ↩️", callback_data="back_main_menu")
    ]
])

meal_question_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Рекомендации 👤", callback_data="recomendation")
    ],
    [
        InlineKeyboardButton(text="Назад 🔙", callback_data="qwestion/answer"),
        InlineKeyboardButton(text="В главное меню ↩️", callback_data="back_main_menu")
    ]
])


training_question_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Рекомендации 👤", callback_data="recomendation_training")
    ],
    [
        InlineKeyboardButton(text="Назад 🔙", callback_data="qwestion/answer"),
        InlineKeyboardButton(text="В главное меню ↩️", callback_data="back_main_menu")
    ]
])


back_or_main_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Назад 🔙", callback_data="meal_question"),
        InlineKeyboardButton(text="В главное меню ↩️", callback_data="back_main_menu")
    ]
])


pay_problem_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Связаться📞", callback_data="problem_pay", url="https://t.me/IF_PROEKT_13"),
        InlineKeyboardButton(text="В главное меню ↩️", callback_data="back_main_menu")
    ]
])