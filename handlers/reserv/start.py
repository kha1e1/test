import typing

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession

from functions.f_formattig import formatting_master_text
from keyboards.inline import ikb_master
from keyboards.inline.ikb_return import return_to_main_menu_btn
from loader import dp
from misc import state_reserv
from model import database

@dp.message_handler(Text(equals='Записаться'), state='*')
@dp.message_handler(Text(equals='⬅️ Назад'), state=state_reserv.StateReserv.service)
async def information_f(message: types.Message, state: FSMContext, session: AsyncSession):
    masters_name: typing.List[database.master_barber.MasterBarber] = await database.master_barber.MasterBarber.all(session)

    if not masters_name:
        return await message.answer("Пока нет мастеров.")

    data = await state.get_data()
    master_dict: dict = data.get("master")

    if master_dict is None:
        master_dict = {}
        await state.update_data(master=master_dict)

    if message.text == "⬅️ Назад":
        await message.answer("Вы вернулись назад", reply_markup=ReplyKeyboardRemove())

    markup = ikb_master.get_master_btn(masters_name)
    markup.add(return_to_main_menu_btn())
    await message.answer(formatting_master_text(master_dict.get("name")),
                         reply_markup=markup)

    await state_reserv.StateReserv.start.set()



