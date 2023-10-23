from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

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