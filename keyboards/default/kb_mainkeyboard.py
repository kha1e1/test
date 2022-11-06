from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from functions.f_check_admin import check_admin


async def main_menu(user_id):
    kb_main_menu = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn0 = KeyboardButton('***Админ***')
    btn1 = KeyboardButton('Записаться')
    btn4 = KeyboardButton("Мои брони")
    btn2 = KeyboardButton('☎️ Контакты')
    btn3 = KeyboardButton('📷 Галерея')
    kb_main_menu.add(btn1)
    kb_main_menu.add(btn4)
    kb_main_menu.add(btn2, btn3)


    if await check_admin(user_id):
        kb_main_menu.add(btn0)
    return kb_main_menu
