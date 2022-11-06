from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


markup = ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
btn = KeyboardButton('Авторизоваться', request_contact=True)
markup.add(btn)
