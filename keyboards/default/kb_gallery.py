from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from keyboards.default.kb_return_main_menu import main_menu
gallery = ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
btn = KeyboardButton('Фото салона')
btn1 = KeyboardButton('Фото работ мастеров')
gallery.add(btn,btn1)
gallery.add(main_menu)
