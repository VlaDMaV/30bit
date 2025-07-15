from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

main = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Оставить отзыв", callback_data="review"),
        InlineKeyboardButton(text="Посмотреть отзывы", callback_data="reviews")
    ],
    [
        InlineKeyboardButton(text="Обратная связь", callback_data="feedback")
    ],
    [
        InlineKeyboardButton(text="О компании", callback_data="about")
    ]
],
    input_field_placeholder="Выберите пункт меню")


aboutus = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="YouTube", url="https://www.youtube.com/@30bit"),
        InlineKeyboardButton(text="WhatsApp", url="https://wa.me/79991234567")  # добавьте ваш номер
    ],
    [
        InlineKeyboardButton(text="Сайт", url="https://ваш-сайт.ru"),  # добавьте вашу ссылку
        InlineKeyboardButton(text="Telegram", url="https://t.me/ваш_канал")  # добавьте ваш канал
    ],
    [
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")
    ]
])


back_to_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_main")]
])


def stars_rating():
    builder = InlineKeyboardBuilder()
    for i in range(1, 6):
        builder.button(text=f"{i}⭐", callback_data=f"rate_{i}")
    builder.adjust(5)
    return builder.as_markup()


def review_management():
    builder = InlineKeyboardBuilder()

    builder.button(text="✏️ Редактировать отзыв", callback_data="edit_review")
    builder.button(text="🔙 На главную", callback_data="back_to_main")
    builder.adjust(1)

    return builder.as_markup()


def reviews_keyboard(page: int = 0, total_pages: int = 1):
    builder = InlineKeyboardBuilder()
    
    if page > 0:
        builder.button(text="⬅️ Назад", callback_data=f"reviews_{page-1}")
    
    if page < total_pages - 1:
        builder.button(text="Вперед ➡️", callback_data=f"reviews_{page+1}")
    
    builder.button(text="🔙 На главную", callback_data="back_to_main")
    
    builder.adjust(2, 1)
    return builder.as_markup()