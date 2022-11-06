import asyncio
import typing

import aiofiles.os
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, ReplyKeyboardMarkup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import classes.message_delete
from data import workdirs
from functions.f_formattig import formatting_input_schedule_master
from keyboards import generate_markup
from keyboards.default import kb_edit_master, kb_return_main_menu
from keyboards.default.kb_edit_master import get_action_edit_service
from keyboards.inline import ikb_edit_master, ikb_return
from keyboards.inline.ikb_admin import get_week_days_btn
from loader import dp
from misc import state_add_master
from model import database
from model.master import ModelMaster, ModelScheduleMaster


@dp.message_handler(Text(equals="Редактировать мастера"))
async def start_edit_master_handler(m: Message, session: AsyncSession):
    masters = await database.master_barber.MasterBarber.all(session)
    markup = kb_edit_master.get_master_btn(masters)
    markup.add(
        kb_return_main_menu.get_back()
    )
    await m.answer(
        text="Выберите мастера",
        reply_markup=markup
    )
    await state_add_master.StateEditMaster.choice_master.set()


@dp.message_handler(Text(equals="⬅️ Назад"), state=state_add_master.StateEditMaster)
async def back_edit_master_handler(m: Message,
                                   session: AsyncSession,
                                   state: FSMContext):
    state_name = await state.get_state()
    state_group = state_name.split(":")[0]
    data = await state.get_data()
    message_ids = data.get("message_ids")

    handlers = {
        state_add_master.StateEditMaster.choice_action.state: {
            'handler': start_edit_master_handler,
            'arguments': [m, session]
        },
        state_add_master.StateEditMaster.schedule_start.state: {
            'handler': choice_edit_master_handler,
            'arguments': [m, session, state, True],
            'message_collection': classes.message_delete.MessageCollection(m.from_user.id, m.bot)
        },
        state_add_master.StateEditMaster.service_edit.state: {
            'handler': edit_service_master_handler,
            'arguments': [m, state],
            'message_collection': classes.message_delete.MessageCollection(m.from_user.id, m.bot)
        },
        state_add_master.StateEditMaster.__name__: {
            'handler': choice_edit_master_handler,
            'arguments': [m, session, state, True]
        },
        state_add_master.StateEditMaster.service_delete.state: {
            'handler': edit_service_master_handler,
            'arguments': [m, state],
            'message_collection': classes.message_delete.MessageCollection(m.from_user.id, m.bot)
        },
    }

    handler = handlers.get(state_name)
    if handler is None:
        handler = handlers.get(state_group)

    handler_func = handler.get('handler')
    handler_arguments: list = handler.get('arguments')
    message_collection: classes.message_delete.MessageCollection = handler.get('message_collection')

    await handler_func(*handler_arguments)

    if message_collection and message_ids:
        message_collection.message_ids = message_ids
        await message_collection.delete()


@dp.message_handler(state=state_add_master.StateEditMaster.choice_master)
async def choice_edit_master_handler(m: Message, session: AsyncSession,
                                     state: FSMContext, back_status: bool = False):
    """Фото, услуги, график работы"""

    data = await state.get_data()
    if not back_status:
        master_barber: database.master_barber.MasterBarber = await database.master_barber.MasterBarber.get_by_name(session, m.text)
        model = ModelMaster().default()
        model.name = master_barber.master
        model.tg_id = master_barber.telegram_id
        data = dict(
            master={
                "id": master_barber.id,
                "name": master_barber.master
            }
        )

        await state.update_data(
            model=model.dict(),
            **data,
        )

    markup = kb_edit_master.get_edit_action_btn()
    markup.add(kb_return_main_menu.get_back())

    await m.answer(
        f"Выберите, что вы хотите отредактировать у мастера - {data.get('master').get('name')} ",
        reply_markup=markup
    )

    await state_add_master.StateEditMaster.choice_action.set()


@dp.message_handler(Text(equals="График работы"), state=state_add_master.StateEditMaster.choice_action)
async def edit_schedule_master_handler(m: Message, session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    master: dict = data.get("master")
    model_master = ModelMaster().load(data.get('model'))
    message_collection = classes.message_delete.MessageCollection(m.from_id, m.bot)
    schedules: typing.List[database.job_barber.JobBarber] = await database.job_barber.JobBarber.all(session=session,
                                                                                                    master_id=master.get(
                                                                                                        'id'))
    model_master.schedules = [ModelScheduleMaster().convert(_object) for _object in schedules]
    msg = await m.answer("Вы в разделе <b>График работы</b>",
                         reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(kb_return_main_menu.get_back()))

    message_collection.message_ids.append(msg.message_id)

    await state.update_data(model=model_master.dict(),
                            old_model=model_master.dict()

                            )
    msg = await m.answer(formatting_input_schedule_master(model_master.schedules), reply_markup=get_week_days_btn())
    message_collection.message_ids.append(msg.message_id)

    await state.update_data(
        message_ids=message_collection.message_ids,

    )

    await state_add_master.StateEditMaster.schedule_start.set()  # функции в файле schedule_master.py


@dp.callback_query_handler(text='next', state=state_add_master.StateEditMaster.schedule_start)
async def update_schedule_master_handler(c: CallbackQuery,
                                         session: AsyncSession,
                                         state: FSMContext):
    data = await state.get_data()
    model = ModelMaster().load(data.get('model'))
    old_model = ModelMaster().load(data.get('old_model'))
    message_collection = classes.message_delete.MessageCollection(c.from_user.id, c.bot)
    message_collection.message_ids = data.get("message_ids")

    schedules_old_to_dict = {
        _job.day_of_week: {
            'model': _job
        } for _job in old_model.schedules
    }
    schedules = []

    for _job in model.schedules:
        __job_object: dict = schedules_old_to_dict.get(_job.day_of_week)
        if _job != __job_object['model']:
            schedules.append(_job)

    await c.message.edit_text("Идет обновление...")

    for _schedule in schedules:
        await database.job_barber.JobBarber.update(
            session, job_id=_schedule.id, data=_schedule,
        )

    await message_collection.delete()
    markup = kb_edit_master.get_edit_action_btn()
    markup.add(kb_return_main_menu.get_back())
    await c.message.answer(f"График работы успешно изменен у мастера {model.name}", reply_markup=markup)
    await state_add_master.StateEditMaster.choice_action.set()


@dp.message_handler(Text(equals="Фотографии"), state=state_add_master.StateEditMaster.choice_action)
async def edit_photo_master_handler(m: Message):
    await m.answer("Отправьте фотографии работ мастера.",
                   reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(kb_return_main_menu.get_back()))

    await state_add_master.StateEditMaster.photo.set()


@dp.message_handler(state=state_add_master.StateEditMaster.photo,
                    content_types=types.ContentTypes.PHOTO)
async def get_photo_master_handler(m: Message, state: FSMContext,
                                   session: AsyncSession, album: typing.List[Message] = None
                                   ):
    if album is None:
        album = [m]

    data = await state.get_data()
    model = ModelMaster().load(data.get("model"))
    master_data: dict = data.get('master')
    msg = await m.answer("Заменяем фотографии...")
    photos: typing.List[
        database.master_works_barber.MasterWorksBarber
    ] = await database.master_works_barber.MasterWorksBarber.all(session=session, master_id=master_data.get('id'))
    await database.master_works_barber.MasterWorksBarber.delete(session, master_id=master_data.get('id'))

    for media in album:
        photo = media.photo[-1]
        filename = f"{photo.file_id}.jpg"
        path_photo = workdirs.WORK_DIRECTORY_PHOTO_MASTER_WORKS / filename
        await media.photo[-1].download(destination_file=path_photo)
        await asyncio.sleep(0.1)
        model.photo_works.append(filename)

    await database.master_works_barber.MasterWorksBarber.save(
        session, master_id=master_data.get('id'),
        master_name=master_data.get('name'), photos=model.photo_works
    )

    markup = kb_edit_master.get_edit_action_btn()
    markup.add(kb_return_main_menu.get_back())

    await msg.delete()
    await m.answer(text="Фотографии успешно заменены", reply_markup=markup)
    await state_add_master.StateEditMaster.choice_master.set()

    for photo in photos:
        await aiofiles.os.remove(workdirs.WORK_DIRECTORY_PHOTO_MASTER_WORKS / photo.photo_path)


@dp.message_handler(Text(equals="Услуги"), state=state_add_master.StateEditMaster.choice_action)
async def edit_service_master_handler(m: Message, state: FSMContext):
    text = "Выберите"
    markup = kb_edit_master.get_action_edit_service()
    markup.add(
        kb_return_main_menu.get_back()
    )

    await state.update_data(
        model=ModelMaster().default().dict()
    )
    await m.answer(
        text=text,
        reply_markup=markup
    )
    await state_add_master.StateEditMaster.choice_action_service.set()


@dp.callback_query_handler(Text(equals='no'), state=state_add_master.StateEditMaster.service_confirmation)
async def add_service_master_handler(c: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    master: dict = data.get('master')
    model_master = ModelMaster().load(data.get('model'))

    await database.service_barber.save_services_master(
        session, master.get('id'), model_master.services
    )
    await c.message.delete()
    markup = kb_edit_master.get_action_edit_service()
    markup.add(
        kb_return_main_menu.get_back()
    )

    await c.message.answer(
        text="Услуги успешно добавлены.",
        reply_markup=markup
    )

    await state_add_master.StateEditMaster.choice_action_service.set()


@dp.message_handler(Text(equals="Удалить услугу"), state=state_add_master.StateEditMaster.choice_action_service)
async def delete_service_master_handler(m: Message, state: FSMContext, session: AsyncSession):
    text = "Выберите услугу, которую хотите удалить.\n" \
           "<i>После нажатия на кнопку - услуга удалится</i>"

    message_collection = classes.message_delete.MessageCollection(m.from_user.id, m.bot)
    data = await state.get_data()
    master = data.get('master')
    ms_id = await m.answer(
        text,
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(kb_return_main_menu.get_back())
    )
    message_collection.message_ids.append(ms_id.message_id)

    services: typing.List[
        database.service_barber.ServiceBarber
    ] = await database.service_barber.ServiceBarber.all(session=session, master_id=master.get('id'))

    await state.update_data(
        services={
            __service.get('id'): {
                **__service
            } for __service in [_service.json() for _service in services]
        }
    )

    ms_id = await m.answer(
        text=f"Услуги мастера - {master.get('name')}",
        reply_markup=ikb_edit_master.get_service_for_delete_btn(services)
    )
    message_collection.message_ids.append(ms_id.message_id)

    await state.update_data(
        message_ids=message_collection.message_ids
    )

    await state_add_master.StateEditMaster.service_delete.set()


@dp.message_handler(Text(equals='Редактировать услугу'), state=state_add_master.StateEditMaster.choice_action_service)
async def edit_view_service_master_handler(
        m: Message, state: FSMContext, session: AsyncSession
):
    data = await state.get_data()
    master: dict = data.get('master')

    services: typing.List[
        database.service_barber.ServiceBarber
    ] = await database.service_barber.ServiceBarber.all(session, master.get('id'))

    markup = ikb_edit_master.get_service_for_edit_btn(services)
    msg_id_first = await m.answer("Вы в разделе <b>Редактирование услуг</b>", reply_markup=ReplyKeyboardMarkup(
        resize_keyboard=True
    ).add(kb_return_main_menu.get_back()))

    msg_id_second = await m.answer(
        text="Выберите услугу, которую хотите отредактировать",
        reply_markup=markup
    )
    await state.update_data(
        message_ids=[msg_id_first.message_id, msg_id_second.message_id]
    )
    await state_add_master.StateEditMaster.service_edit.set()
