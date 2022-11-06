import typing

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession

import classes.message_delete
from keyboards.default import kb_return_main_menu
from keyboards.inline import ikb_edit_master
from keyboards.inline.ikb_admin import get_delay_service_btn, get_confirmation_btn, ikb_delay_cb
from loader import dp
from misc import state_add_master
from model import database
from model.master import ModelServiceMaster, ModelMaster


async def set_state(
        state: FSMContext,
        default_state
):
    state_name = await state.get_state()
    state_objects = {
        state_add_master.StateEditMaster.choice_action_service.state: state_add_master.StateEditMaster.service_name,
        state_add_master.StateEditMaster.service_confirmation.state: state_add_master.StateEditMaster.service_name,
        state_add_master.StateEditMaster.service_name.state: state_add_master.StateEditMaster.service_price,
        state_add_master.StateEditMaster.service_price.state: state_add_master.StateEditMaster.service_time,
        state_add_master.StateEditMaster.service_time.state: state_add_master.StateEditMaster.service_confirmation
    }

    state_object = state_objects.get(state_name)
    if state_object is None:
        await default_state.set()

    if state_object:
        await state_object.set()


def get_state_root(state_name):
    return state_name.split(":")[0]


@dp.message_handler(text='⬅️ Назад', state=[
    state_add_master.StateAddMaster.service_price,
    state_add_master.StateAddMaster.service_time,
    state_add_master.StateEditMaster.service_name,
    state_add_master.StateEditMaster.service_time,
    state_add_master.StateAddMaster.service_confirmation
])
async def service_master_back_handler(m: Message, state: FSMContext):
    state_name = await state.get_state()
    state_data = await state.get_data()
    state_name_key = state_name.split(":")[-1]

    handlers = {
        'service_price': {
            'handler': service_master_handler,
            'arguments': dict(c=m, state=state)
        },
        'service_time': {
            'handler': input_service_name_master_handler,
            'arguments': dict(m=m, state=state, return_status=True),
            'message_collection': classes.message_delete.MessageCollection(m.from_user.id, m.bot)
        },
        'service_confirmation': {
            'handler': input_service_price_master_handler,
            'arguments': dict(m=m, state=state, return_status=True),
            'message_collection': classes.message_delete.MessageCollection(m.from_user.id, m.bot)
        }
    }
    handler = handlers.get(state_name_key)
    await handler.get('handler')(**handler.get('arguments'))

    if message_collection := handler.get('message_collection'):
        message_collection.message_ids = state_data.get('message_ids')
        await message_collection.delete()


@dp.message_handler(Text("Добавить услугу"), state=state_add_master.StateEditMaster.choice_action_service)
@dp.callback_query_handler(Text(equals=['next', 'yes']),
                           state=[state_add_master.StateAddMaster.schedule_start,
                                  state_add_master.StateAddMaster.service_confirmation,
                                  state_add_master.StateEditMaster.service_confirmation])
async def service_master_handler(c: typing.Union[CallbackQuery, Message], state: FSMContext,

                                 ):
    state_name = await state.get_state()

    if state_add_master.StateEditMaster.service_confirmation.state in state_name:
        await state.update_data(edit_service=True)

    text = "Напишите название услуги."
    if isinstance(c, Message):
        markup = ReplyKeyboardMarkup(resize_keyboard=True).add(kb_return_main_menu.get_back())
        await c.answer(text, reply_markup=markup)

    if isinstance(c, CallbackQuery):
        await c.message.edit_text("Напишите название услуги.")

    await set_state(state, state_add_master.StateAddMaster.service_name)


@dp.message_handler(state=[state_add_master.StateAddMaster.service_name, state_add_master.StateEditMaster.service_name])
async def input_service_name_master_handler(m: Message, state: FSMContext, return_status=False):
    if not return_status:
        model_service = ModelServiceMaster(name=m.text)
        await state.update_data(
            model_service=model_service.dict()
        )

    await m.answer("Введите цену")
    await set_state(state, state_add_master.StateAddMaster.service_price)


@dp.message_handler(
    state=[state_add_master.StateAddMaster.service_price, state_add_master.StateEditMaster.service_price])
async def input_service_price_master_handler(m: Message, state: FSMContext, return_status: bool = False):
    if not return_status:
        if not m.text.isdigit():
            return await m.answer("Это не похоже не цену.")

        data = await state.get_data()
        model_service: ModelServiceMaster = ModelServiceMaster().load(data.get('model_service'))
        model_service.price = int(m.text)
        await state.update_data(model_service=model_service.dict())

    msg = await m.answer("Укажите продолжительность услуги", reply_markup=get_delay_service_btn())
    await state.update_data(message_ids=[msg.message_id])
    await set_state(state, state_add_master.StateAddMaster.service_time)


@dp.callback_query_handler(ikb_delay_cb.filter(), state=[state_add_master.StateAddMaster.service_time,
                                                         state_add_master.StateEditMaster.service_time])
async def input_delay_service_master_handler(c: CallbackQuery,
                                             callback_data: dict,
                                             state: FSMContext):
    data = await state.get_data()
    model_service: ModelServiceMaster = ModelServiceMaster().load(data.get('model_service'))
    delay_service = int(callback_data.get('m'))  # время в минутах
    model_service.time = delay_service

    model_master = ModelMaster().load(data.get('model'))
    model_master.services.append(model_service)
    await state.update_data(model=model_master.dict())

    msg = await c.message.edit_text(
        text="Вы хотите добавить еще услугу?",
        reply_markup=get_confirmation_btn()
    )
    await state.update_data(message_ids=[msg.message_id])
    await set_state(state, state_add_master.StateAddMaster.service_confirmation)


@dp.callback_query_handler(ikb_edit_master.ikb_edit_master_cb.filter(action='d'),
                           state=state_add_master.StateEditMaster.service_delete)
async def delete_service_master_handler(c: CallbackQuery,
                                        callback_data: dict,
                                        state: FSMContext,
                                        session: AsyncSession):
    service_id = callback_data.get('id')
    data = await state.get_data()
    services: dict = data.get("services")

    if len(services) == 1:
        return await c.answer("Вы больше не можете удалить услугу. Минимум нужна 1 услуга мастера",
                              show_alert=True)

    service = services.get(service_id)
    services.pop(service_id)
    await state.update_data(services=services)

    await database.service_barber.ServiceBarber(**service).delete(session)
    await c.message.edit_text(
        text=f"Услуга мастера успешно удалена.",
        reply_markup=ikb_edit_master.get_service_for_delete_btn([
            database.service_barber.ServiceBarber(**_service)
            for _service in services.values()
        ])
    )
