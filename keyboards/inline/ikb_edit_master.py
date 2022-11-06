import typing

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

from keyboards import generate_markup
from model import database

ikb_edit_master_cb = CallbackData("edit", 'action', 'id')


def get_service_for_delete_btn(
        services: typing.List[
            database.service_barber.ServiceBarber
        ]
):
    """Кнопки для удаления услуг у мастера"""

    btns = [
        InlineKeyboardButton(
            text=f"{service.name} {service.price} KZT",
            callback_data=ikb_edit_master_cb.new(action='d', id=service.id)
        ) for service in services
    ]

    return generate_markup.GenerateMarkupButtons(
        laylout=2,
        markup=InlineKeyboardMarkup(),
        keyboards=btns).get()




def get_service_for_edit_btn(
        services: typing.List[
            database.service_barber.ServiceBarber
        ]
):
    btns = [
        InlineKeyboardButton(
            text=f"{_service.name} {_service.price}",
            callback_data=ikb_edit_master_cb.new(
                action='view',
                id=_service.id
            )

        ) for _service in services
    ]

    return generate_markup.GenerateMarkupButtons(
        laylout=1,
        markup=InlineKeyboardMarkup(),
        keyboards=btns
    ).get()


def get_action_edit_for_service(service_id: int):

    btns = {
        "Имя": ikb_edit_master_cb.new(action='name', id=service_id),
        "Цена": ikb_edit_master_cb.new(action='price', id=service_id),
        "Продолжительность": ikb_edit_master_cb.new(action='time', id=service_id)
    }

    return generate_markup.GenerateMarkupButtons(
        laylout=2,
        markup=InlineKeyboardMarkup(),
        keyboards=[InlineKeyboardButton(
            text=t, callback_data=c
        ) for t, c in btns.items()]
    ).get()