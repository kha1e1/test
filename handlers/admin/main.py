from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup

from data.strings import s_main
from functions.f_add_master import delete_message
from keyboards.default import kb_master
from keyboards.default.kb_mainkeyboard import main_menu
from loader import dp
from misc import state_add_master


@dp.message_handler(text='⬅️ Назад', state=[state_add_master.StateEditMaster.choice_master, state_add_master.StateAddMaster.name,
                                            state_add_master.StateDeleteMaster.start
                                            ])
@dp.message_handler(text="***Админ***", state="*")
async def admin_start(m: Message, state: FSMContext):
    text = "Админ панель"
    await state.reset_state()
    msg = await m.answer(
        text=text,
        reply_markup=kb_master.get_main_admin_btn()
    )



