import typing

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

import classes.message_delete
from data import strings
from keyboards.default import kb_gallery
from loader import dp, bot
from aiogram.dispatcher.filters import Text
from data.strings import s_main
from keyboards.default.kb_mainkeyboard import main_menu
from misc import state_gallery


@dp.callback_query_handler(Text(equals='main_menu'), state='*')
@dp.message_handler(Text(equals=['Главное меню']), state='*')
async def bot_echo(query: typing.Union[types.Message, types.CallbackQuery], state: FSMContext):
    data = await state.get_data()
    message_ids = data.get('message_ids')
    message_collection = classes.message_delete.MessageCollection(query.from_user.id, bot)
    message_collection.message_ids = message_ids
    message_collection.timeout = 0.6

    await state.finish()
    if isinstance(query, CallbackQuery):
        await query.message.delete()
        await query.message.answer(s_main.main_menu, reply_markup=await main_menu(query.from_user.id))

    if isinstance(query, Message):
        await query.answer(s_main.main_menu, reply_markup=await main_menu(query.from_user.id))

    await message_collection.delete()


@dp.message_handler(text="⬅️ Назад", state=state_gallery.StateGallery.master_works)
async def back_gallery_handler(m: types.Message, state: FSMContext):
    await state.finish()

    await m.answer(strings.s_gallery.gallerystart, reply_markup=kb_gallery.gallery)
