import random
import typing

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.generate_markup import GenerateMarkupButtons
from model import database





def get_reserv_btn() -> InlineKeyboardButton:

    return InlineKeyboardButton(text="🕖 Оформить бронь", callback_data="reserv_service")


def get_master_btn(masters: typing.List[database.master_barber.MasterBarber]):
    markup = InlineKeyboardMarkup()


    btns = []
    for master in masters:
        btns.append(
            InlineKeyboardButton(text=master.master, callback_data=f"master_{master.id}")
        )

    return GenerateMarkupButtons(
        laylout=2,
        markup=markup,
        keyboards=btns
    ).get()
