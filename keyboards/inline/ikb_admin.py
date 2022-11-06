import datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from data import dictionaries
from functions.f_reserv import get_times
from keyboards import generate_markup

ikb_week_of_day_cb = CallbackData('week', 'd')
ikb_time_cb = CallbackData('time', 'h', 'm')
ikb_delay_cb = CallbackData('delay', 'm')


def get_week_days_btn():
    markup = InlineKeyboardMarkup(row_width=3)
    btns = [
        InlineKeyboardButton(text=text, callback_data=ikb_week_of_day_cb.new(d=day)) for text, day in
        dictionaries.calendar.day_of_weeks.items()
    ]
    for btn in btns:
        markup.insert(btn)

    return markup


def get_not_working_day():
    return InlineKeyboardButton("❌ Не рабочий день", callback_data='not_working_day')


def get_times_btn() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=3)
    btns = [
        InlineKeyboardButton(
            text=f"{time.get('hour')}:{time.get('minute'):02d}",
            callback_data=ikb_time_cb.new(h=time.get("hour"), m=time.get('minute'))
        ) for time in get_times(9, 23, minutes=[0, 30])

    ]

    return markup.add(*btns)


def get_next_btn(text: str):
    return InlineKeyboardButton(text=text, callback_data='next')


def get_delay_service_btn():
    btns = {
        "30 минут": ikb_delay_cb.new(m=30),
        "60 минут": ikb_delay_cb.new(m=60)
    }

    return generate_markup.GenerateMarkupButtons(
        laylout=2,
        markup=InlineKeyboardMarkup(),
        keyboards=[
            InlineKeyboardButton(text=t, callback_data=c) for t, c in btns.items()
        ]
    ).get()


def get_confirmation_btn():
    btns = {
        "Да": 'yes',
        "Нет": 'no'
    }

    return generate_markup.GenerateMarkupButtons(
        laylout=1,
        markup=InlineKeyboardMarkup(),
        keyboards=[
            InlineKeyboardButton(text=t, callback_data=c)
            for t, c in btns.items()
        ]
    ).get()


def get_add_btn():
    btns = {
        "Добавить": "added",
        "Отменить": "cancel_added"
    }

    markup = InlineKeyboardMarkup()

    for name, callback in btns.items():
        markup.add(InlineKeyboardButton(text=name, callback_data=callback))
    return markup
