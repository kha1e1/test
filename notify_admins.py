import logging

from aiogram import Dispatcher

from data.config import ADMINS
from keyboards.default.kb_mainkeyboard import main_menu


async def on_startup_notify(dp: Dispatcher):

    for admin_id in ADMINS:
        try:
            await dp.bot.send_message(admin_id, "Бот Запущен", reply_markup=await main_menu(admin_id))
        except Exception as err:
            logging.exception(err)
