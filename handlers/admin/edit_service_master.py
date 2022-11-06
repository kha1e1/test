import typing

from aiogram import Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import AsyncSession

import classes.message_delete
from keyboards.inline import ikb_admin, ikb_edit_master
from loader import dp
from misc import state_add_master
from model import database


async def view_service(c: typing.Union[CallbackQuery, Message], service_id, session: AsyncSession):
    markup = ikb_edit_master.get_action_edit_for_service(service_id)
    service: database.service_barber.ServiceBarber = await database.service_barber.ServiceBarber.first(session,
                                                                                                       database.service_barber.ServiceBarber.id == service_id
                                                                                                       )
    text = "Выберите, что хотите отредактировать.\n" \
           f"Наименование: {service.name}\n" \
           f"Продолжительность: {service.minute:.2f}\n" \
           f"Цена: {service.price:.2f} KZT"

    if isinstance(c, CallbackQuery):
        return await c.message.edit_text(
            text=text,
            reply_markup=markup
        )
    if isinstance(c, Message):
        return await c.answer(text=text, reply_markup=markup)


@dp.callback_query_handler(ikb_edit_master.ikb_edit_master_cb.filter(action='view'),
                           state=state_add_master.StateEditMaster.service_edit)
async def view_service_handler(c: CallbackQuery,
                               callback_data: dict, session: AsyncSession):
    service_id = int(callback_data.get("id"))

    await view_service(c, service_id, session)
    await state_add_master.StateEditMaster.service_edit.set()


async def edit_service(bot: Bot, text: str, chat_id: int,
                       markup: InlineKeyboardMarkup = None):
    await bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=markup
    )


@dp.callback_query_handler(ikb_edit_master.ikb_edit_master_cb.filter(action=['name', 'price', 'time']),
                           state=state_add_master.StateEditMaster.service_edit
                           )
async def edit_service_handler(c: CallbackQuery, state: FSMContext, callback_data: dict):
    key = callback_data.get("action")
    service_id = int(callback_data.get('id'))
    data = await state.get_data()
    message_ids = data.get('message_ids')
    message_collection = classes.message_delete.MessageCollection(c.from_user.id, c.bot)
    message_collection.message_ids = message_ids
    message_collection.pop(c.message.message_id)
    await c.message.delete()
    handlers = {
        "name": {
            'handler': edit_service,
            'arguments': dict(bot=c.bot, text="Напишите название услуги.", chat_id=c.from_user.id)
        },
        'price': {
            'handler': edit_service,
            'arguments': dict(bot=c.bot, text="Введите цену", chat_id=c.from_user.id)
        },
        'time': {
            'handler': edit_service,
            'arguments': dict(bot=c.bot, text="Укажите продолжительность услуги", chat_id=c.from_user.id,
                              markup=ikb_admin.get_delay_service_btn())
        }
    }
    await state.update_data(
        service={
            'action': key,
            'id': service_id
        }
    )
    handler = handlers.get(key)
    await handler.get('handler')(**handler.get('arguments'))
    await state.update_data(message_ids=message_ids)
    await state_add_master.StateEditMaster.service_edit_start.set()


@dp.message_handler(state=state_add_master.StateEditMaster.service_edit_start)
async def success_edit_service_handler(m: Message,
                                       session: AsyncSession,
                                       state: FSMContext):
    data = await state.get_data()
    service = data.get("service")
    service_key = service.get("action")
    service_id = service.get('id')
    message_ids: list = data.get('message_ids')
    user_answer = m.text


    if service_key in 'price':
        if not m.text.isdigit():
            return await m.answer("Это не похоже на цену")
        user_answer = int(user_answer)

    await database.service_barber.update_service(session=session,
                                                 service_id=service_id,
                                                 data={
                                                     service_key: user_answer
                                                 })

    msg_id = await view_service(m, service_id, session)
    message_ids.append(msg_id.message_id)
    await state.update_data(message_ids=message_ids)
    await state_add_master.StateEditMaster.service_edit.set()


@dp.callback_query_handler(ikb_admin.ikb_delay_cb.filter(), state=state_add_master.StateEditMaster.service_edit_start)
async def success_edit_time_service_handler(c: CallbackQuery,
                                            session: AsyncSession,
                                            callback_data: dict,
                                            state: FSMContext):
    data = await state.get_data()
    service = data.get("service")
    service_id = service.get('id')
    delay = int(callback_data.get('m'))
    message_ids: list = data.get("message_ids")

    await database.service_barber.update_service(session=session,
                                                 service_id=service_id,
                                                 data={
                                                     'minute': delay
                                                 })

    msg = await view_service(c, service_id, session)
    message_ids.append(msg.message_id)
    await state.update_data(
        message_ids=message_ids
    )

    await state_add_master.StateEditMaster.service_edit.set()
