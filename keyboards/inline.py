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
            callback_data="back_main_menu"
        )
    ]
],
    resize_keyboard=True
)


back_in_meal_menu = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text="Назад, к питанию",
            callback_data="back_in_meal_menu"
        )
    ]
],
    resize_keyboard=True
)


user_gender_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Мужской", callback_data="male1"),
    ],
    [
        InlineKeyboardButton(text="Женский", callback_data="female1")
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


pay_button: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text="Оплатить 💵", callback_data="want_pay"
        )
    ]
])

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
            callback_data="back_in_meal_menu"
        )
    ],
    [
        InlineKeyboardButton(text="Помощь", callback_data="help")
    ]
])


# async def generate_meal_keyboard():
#     conn = connect()
#     cursor = conn.cursor()
#
#     try:
#         cursor.execute("SELECT meal_name FROM meals;")
#         meals = cursor.fetchall()
#
#         # Собираем все кнопки в список
#         buttons = [InlineKeyboardButton(text=meal[0], callback_data=f"meal:{meal[0]}") for meal in meals]
#         back_button = [InlineKeyboardButton(text="Вернуться в главное меню", callback_data="back_main_menu")]
#
#         # Создаем InlineKeyboardMarkup, передавая кнопки как список списков
#         keyboard_markup = InlineKeyboardMarkup(inline_keyboard=[buttons, back_button])
#
#         return keyboard_markup
#
#     except Exception as e:
#         print(f"Error: {e}")
#         return None
#
#     finally:
#         cursor.close()
#         conn.close()

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
    # [
    #     #InlineKeyboardButton(text="Общение 🗣", url="https://t.me/+TgAj34afQ0lkOTIy"),
    #     #InlineKeyboardButton(text="Вопрос/Ответ 🆘", callback_data="qwestion/answer")
    # ],
    [
        InlineKeyboardButton(text="Получить быстрый ответ ❓", callback_data="quick_answer")
    ],
    [
        InlineKeyboardButton(text="Оплатить 💵", callback_data="want_pay")
    ],
    [
        InlineKeyboardButton(text="Проблема с оплатой 💸", callback_data="problem_pay")
    ],
    [
        InlineKeyboardButton(text="Назад 🔙", callback_data="back_main_menu")
    ]
])


async def get_help_keyboard(user_id):
    buttons = []
    if await is_subscription_active(user_id):
        buttons.append([InlineKeyboardButton(text="Перейти в канал для общения", url="https://t.me/+TgAj34afQ0lkOTIy")])
    buttons.append([InlineKeyboardButton(text="Получить быстрый ответ ❓", callback_data="quick_answer")])
    if await is_subscription_active(user_id):
        buttons.append([InlineKeyboardButton(text="Купить 777 🛒", callback_data="do_you_want_pay")])
    buttons.append([InlineKeyboardButton(text="Проблема с оплатой 💸", callback_data="problem_pay")])
    buttons.append([InlineKeyboardButton(text="Назад 🔙", callback_data="back_main_menu")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def is_subscription_active(user_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE telegram_user_id = %s AND is_subscription_active = TRUE", (user_id,))
    active_user = cursor.fetchone()
    cursor.close()
    conn.close()
    return active_user is not None


@router.callback_query(lambda c: c.data == 'do_you_want_pay')
async def do_you_want_pay(callback: CallbackQuery):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT subscription_days FROM users WHERE telegram_user_id = %s AND is_subscription_active = TRUE", (callback.from_user.id,))
    subscribe_days = cursor.fetchone()
    await callback.message.answer(text=f"У вас действует подписка {subscribe_days} дней. \n"
                                       f"Хотите продлить абонемент?", reply_markup=new_abonement)


new_abonement = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Да', callback_data="pay"),
        InlineKeyboardButton(text="Нет", callback_data="back_main_menu")
    ]
])


question_answer_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Тренировки 🏃", callback_data="training_question")
    ],
    [
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