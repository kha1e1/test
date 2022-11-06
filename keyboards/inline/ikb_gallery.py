import typing

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

ikb_gallery_cb = CallbackData("gallery", "page")


def get_paginate_for_gallery(
        galleries: typing.List[str],
        page: int = 0,
        limit: int = 0
):
    btns = []
    if page > 0:
        btns.append(
            InlineKeyboardButton(
                text="Назад",
                callback_data=ikb_gallery_cb.new(page=page-1)
            )
        )

    if page + 1 < len(galleries) / limit:
        btns.append(
            InlineKeyboardButton(
                text="Вперед",
                callback_data=ikb_gallery_cb.new(page=page+1)
        ))

    markup = InlineKeyboardMarkup()

    return markup.add(
        *btns
    )


