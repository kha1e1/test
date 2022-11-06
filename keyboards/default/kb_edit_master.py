import array
import typing

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from keyboards import generate_markup
from model import database


def get_master_btn(
        masters: typing.List[database.master_barber.MasterBarber]
):
    btns = [
        KeyboardButton(
            text=master.master
        ) for master in masters
    ]

    return generate_markup.GenerateMarkupButtons(
        laylout=2,
        markup=ReplyKeyboardMarkup(resize_keyboard=True),
        keyboards=btns
    ).get()


def get_edit_action_btn():
    btns = {"Фотографии": 'photo',
            "Услуги": 'service',
            "График работы": 'job'}

    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    return generate_markup.GenerateMarkupButtons(
        laylout=1,
        markup=markup,
        keyboards=[KeyboardButton(
            text=t,
        ) for t, _ in btns.items()]
    ).get()


def get_action_edit_service(service=None):
    btns = [
        "Добавить услугу",
        "Удалить услугу",
        "Редактировать услугу"
    ]
    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    if service is not None:
        btns.pop(0)

    return generate_markup.GenerateMarkupButtons(
        laylout=1,
        markup=markup,
        keyboards=btns
    ).get()



