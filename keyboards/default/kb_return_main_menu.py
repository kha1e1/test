from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

return_main_markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
main_menu = KeyboardButton('Главное меню')
return_main_markup.add(main_menu)

return_nazad_markup=ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
return_nazad_markup.add(KeyboardButton("⬅️ Вернуться назад"))
return_nazad_markup.add(main_menu)


def get_back():
    return KeyboardButton(text="⬅️ Назад")