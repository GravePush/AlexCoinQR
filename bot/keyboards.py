from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main_user_inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Моя статистика", callback_data="mystats")
        ],
        [
            InlineKeyboardButton(text="🆔 Мой Telegram ID", callback_data="myid")
        ]
    ]
)

main_admin_inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Cтатистика", callback_data="stats")
        ],
        [
            InlineKeyboardButton(text="🤖 Новый QR-код", callback_data="newqr")
        ]
    ]
)

back_to_main_inline_btn = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Назад", callback_data="back_to_main")
        ]
    ]
)

welcome_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Начать", callback_data="start_bot")]
    ]
)



