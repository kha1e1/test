from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def inline_contacts():
    markup = InlineKeyboardMarkup()
    inline_instagram_button = InlineKeyboardButton("Мы в Instagram 📱 ", url='https://www.instagram.com/oldboy_astana/')
    inline_2gis_button = InlineKeyboardButton("Мы в 2 GIS 📍", url='https://2gis.kz/nur_sultan/firm/70000001036483273')
    markup.add(inline_instagram_button, inline_2gis_button)
    return markup
