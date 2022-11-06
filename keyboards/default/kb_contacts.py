from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from keyboards.default.kb_return_main_menu import main_menu

contacts = ReplyKeyboardMarkup( resize_keyboard=True)
btn = KeyboardButton('Мы в instagram')
btn1 = KeyboardButton('Мы в 2GIS')
contacts.add(btn,btn1)
contacts.add(main_menu)