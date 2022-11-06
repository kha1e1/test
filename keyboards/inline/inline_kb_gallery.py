from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data import strings

inline_gallery = InlineKeyboardMarkup()
inline_btn = InlineKeyboardButton(strings.next,callback_data="Следующее фото")
inline_btn1 = InlineKeyboardButton(strings.back,callback_data="Предыдущее фото")
inline_gallery.add(inline_btn, inline_btn1)