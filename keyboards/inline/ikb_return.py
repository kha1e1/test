from aiogram.types import InlineKeyboardButton

from data.strings import s_btn


def return_to_main_menu_btn():
    return InlineKeyboardButton("В главное меню", callback_data='main_menu')


def back_btn(text=s_btn.back):
    return InlineKeyboardButton(text=text, callback_data='back')
