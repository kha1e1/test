"""Подтверждение"""
from aiogram.dispatcher.filters.state import State
from aiogram.types import Message, CallbackQuery

from keyboards.inline import ikb_confirm


async def confirmation_handler(c: CallbackQuery,
                               set_state: State,
                               text: str = '',):

    markup = ikb_confirm.confirm_btn()
    await c.message.edit_text(
        text,
        reply_markup=markup
    )

    await set_state.set()


