import typing

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from openpyxl import load_workbook
import os
from keyboards.default.kb_return_main_menu import main_menu
from model import database

kb_bron = ReplyKeyboardMarkup()
kb_pay = ReplyKeyboardMarkup()
kb_bron.add("Да")
kb_bron.add("⬅️ Вернуться назад")
kb_pay.add("💸 Перейти к оплате")
kb_pay.add("⬅️ Вернуться назад")
kb_pay.add("Главное меню")


def get_services(services: typing.List[database.service_barber.ServiceBarber]) -> list:
    result = []
    for service in services:
        result.append(
            f"{service.name} {service.price} KZT (⏱ {service.minute} мин.)"
        )
    return result


def make_kb_services(
        services: typing.List[database.service_barber.ServiceBarber],

):
    kb_services_new = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    # if service:
    #     kb_services_new.add("Перейти к записи")

    services_list = get_services(services)
    for index, elem in enumerate(services_list):

        # if elem == service:
        #     elem = elem + "✅"

        kb_services_new.add(elem)
    kb_services_new.add("⬅️ Назад")
    return kb_services_new
