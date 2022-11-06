from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from keyboards.default.kb_return_main_menu import main_menu

kb_reserv = ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
btn1 = KeyboardButton('График мастеров')
btn2 = KeyboardButton('Записаться на прием')
kb_reserv.add(btn1, btn2)
kb_reserv.add(main_menu)