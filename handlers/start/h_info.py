from aiogram import types
from loader import dp
from data import strings
from keyboards.default import kb_return_main_menu


@dp.message_handler(commands=['Инфо'])
async def information_f(message: types.Message):
      await message.answer(strings.info, reply_markup=kb_return_main_menu.return_main_markup)
