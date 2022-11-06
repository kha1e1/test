from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from keyboards import generate_markup

ikb_notify_master_cb = CallbackData(
    "r_n", 'act', 's_id'
)  # s_id - service_id, act - action (принять или отказаться)


def get_notify_btn_for_master(
        service_id: int
):
    btns = {
        "Принять": ikb_notify_master_cb.new(act="access", s_id=service_id),
        "Отказаться": ikb_notify_master_cb.new(act='refuse', s_id=service_id)
    }

    return generate_markup.GenerateMarkupButtons(
        laylout=1,
        markup=InlineKeyboardMarkup(),
        keyboards=[
            InlineKeyboardButton(text=text, callback_data=callback)
            for text, callback in btns.items()
        ]
    ).get()


def get_btn_about_turnout(
        schedule_id: int
):

    btns = {
        "Явился": ikb_notify_master_cb.new(act="appeared", s_id=schedule_id),
        "Не явился": ikb_notify_master_cb.new(act="no_turnout", s_id=schedule_id)
    }

    return generate_markup.GenerateMarkupButtons(
        laylout=1,
        markup=InlineKeyboardMarkup(),
        keyboards=[
            InlineKeyboardButton(text=t, callback_data=c)
            for t, c in btns.items()
        ]
    ).get()
