from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards import generate_markup


def confirm_btn():
    markup = InlineKeyboardMarkup()
    btns = {
        "Подтвердить": "c_success",
        "Отменить": "c_cancel"
    }

    return generate_markup.GenerateMarkupButtons(
        laylout=2,
        markup=markup,
        keyboards=[
            InlineKeyboardButton(
                text=t,
                callback_data=c
            ) for t, c in btns.items()
        ]
    ).get()