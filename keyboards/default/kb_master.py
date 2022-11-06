from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_admin_btn():
    btns = [
        "Добавить мастера",
        "Редактировать мастера",
        "Удалить мастера",
        "Главное меню"
    ]
    markup = ReplyKeyboardMarkup(resize_keyboard=True,row_width=1)

    for btn_text in btns:
        markup.insert(KeyboardButton(text=btn_text))

    return markup

