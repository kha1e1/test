from copy import copy

from aiogram import types
from keyboards.inline import ikb_contacts, ikb_return
from loader import dp
from aiogram.dispatcher.filters import Text


@dp.message_handler(Text(equals='☎️ Контакты'), state='*')
async def contacts(message: types.Message):
    markup = ikb_contacts.inline_contacts()
    markup.add(ikb_return.return_to_main_menu_btn())

    text = f"Контактная информация: +77074344353"

    await message.answer(text, reply_markup=markup)

