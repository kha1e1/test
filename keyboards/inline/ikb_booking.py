import typing

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

ikb_booking_callback = CallbackData("booking", "id")


def cancel_booking_btn(
        booking: dict
):
    markup = InlineKeyboardMarkup(1)
    btns = [
        InlineKeyboardButton(
            text=f"Отменить: {booking.get('width').strftime('%Y-%m-%d %H:%M')} ({booking.get('master_name')})",
            callback_data=ikb_booking_callback.new(id=booking.get("id"))
        )
    ]
    markup.add(*btns)

    return markup
