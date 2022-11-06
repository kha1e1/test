from aiogram import types
from aiogram.dispatcher import FSMContext

from data import strings
from keyboards.default.kb_mainkeyboard import main_menu
from loader import dp


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
@dp.message_handler(state="*")
async def bot_echo(message: types.Message, state: FSMContext):
    await state.reset_state()
    await message.answer(strings.s_main.main_menu, reply_markup=await main_menu(message.from_user.id))
