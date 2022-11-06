from aiogram import types
from aiogram.dispatcher.filters import Text

from keyboards.inline.ikb_servces import inline_payment_services
from loader import dp


@dp.message_handler(Text(equals='💸 Перейти к оплате'))
async def information_f(message: types.Message):
    await message.answer("Оплатите удобным для вас способом", reply_markup=inline_payment_services)


@dp.callback_query_handler(lambda c: c.data == "cashpayment")
async def process_callback_button(c: types.CallbackQuery):
    await c.bot.answer_callback_query(c.id)
    await c.bot.send_message(c.from_user.id, 'Благодарим за бронь!😊 '
                                             'Мы вам напомним о вашей брони за день. '
                                             'Наши контакты находятся в разделе: ☎️ Контакты. '
                                             'До встречи! 😄 ')
