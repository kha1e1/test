from aiogram.dispatcher.filters import Text

from loader import dp
from aiogram import types


@dp.message_handler(Text(equals="Фото салона"))
async def process_command_1(message: types.Message):
    with open ("holl.jpeg","rb") as photo:
        await message.reply_photo(photo,caption="Холл",reply_markup=kb.inline_gallery)