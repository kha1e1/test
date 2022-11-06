from aiogram import types
from aiogram.dispatcher import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from loader import dp
from data.strings import s_main
from aiogram.dispatcher.filters.builtin import CommandStart
from keyboards.default import kb_startkeyboard
from keyboards.default.kb_mainkeyboard import main_menu
from aiogram.types import ContentType
from functions.f_add_user import add_user
from model import database


@dp.message_handler(CommandStart(), state='*')
async def bot_start(message: types.Message, state: FSMContext, session: AsyncSession, **kwargs):
    user = await database.contact_barber.ContactBarber.get_by_user_id(session, message.from_user.id)
    await state.reset_state()

    if user:
        await message.answer(s_main.main_menu, reply_markup=await main_menu(message.from_user.id))
    else:
        await message.answer(s_main.start, reply_markup=kb_startkeyboard.markup)




@dp.message_handler(content_types=ContentType.CONTACT, state="*")
async def main_menu_f(message: types.Message, session: AsyncSession):
    status_user: bool = await add_user(
        session, message.chat.id, message.contact.full_name, message.contact.phone_number
    )

    if status_user:
        await message.answer(s_main.main_menu, reply_markup=await main_menu(message.chat.id))
    else:
        await message.answer(s_main.fail)
