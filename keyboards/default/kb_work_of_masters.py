import typing

from aiogram.types import ReplyKeyboardMarkup

from keyboards.default.kb_return_main_menu import main_menu
from model import database



def get_work_of_masters_btn(
        masters: typing.List[database.master_barber.MasterBarber]
) -> ReplyKeyboardMarkup:

    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    for master in masters:
        markup.add(master.master + " works")

    markup.add(
        "⬅️ Назад"
    )

    return markup


