import asyncio
import typing

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession

import classes.message_delete
from data import workdirs
from functions.f_formattig import formatting_input_schedule_master
from handlers.admin import confirmation
from keyboards.default import kb_return_main_menu
from keyboards.default.kb_mainkeyboard import main_menu
from keyboards.inline.ikb_admin import get_add_btn, get_week_days_btn
from loader import dp
from misc import state_add_master
from model import database
from model.database.contact_barber import ContactBarber
from model.master import ModelMaster


@dp.message_handler(text="⬅️ Назад", state=[state_add_master.StateAddMaster.tg_id,
                                            state_add_master.StateAddMaster.schedule_start,
                                            state_add_master.StateAddMaster.service_name,
                                            state_add_master.StateAddMaster.photo
                                            ])
async def add_master_back_handler(query: typing.Union[CallbackQuery, Message], state: FSMContext):
    state_name = await state.get_state()
    state_data = await state.get_data()

    base_arguments = dict(m=query, state=state, return_status=True)
    handlers = {
        state_add_master.StateAddMaster.tg_id.state: {
            'handler': preparation_add_master_handler,
            'arguments': base_arguments
        },
        state_add_master.StateAddMaster.schedule_start.state: {
            'handler': get_name_master_handler,
            'arguments': base_arguments,
            'message_collection': classes.message_delete.MessageCollection(query.from_user.id, query.bot)
        },
        state_add_master.StateAddMaster.service_name.state: {
            'handler': get_tg_id_master_handler,
            'arguments': base_arguments
        },
        state_add_master.StateAddMaster.photo.state: {
            'handler': service_master_handler,
            'arguments': dict(c=query, state=state, return_status=True)
        },


    }

    handler: dict = handlers.get(state_name)
    await handler.get('handler')(**handler.get('arguments'))

    if message_collection := handler.get('message_collection'):
        message_collection.message_ids = state_data.get('message_ids')
        await message_collection.delete()


@dp.message_handler(text="Добавить мастера")
async def preparation_add_master_handler(m: Message, state: FSMContext, **kwargs):
    """Для добавления мастера, нужно узнать от него: имя, tg_id, график работы, услуги и цены (это все вместе)"""

    await state.update_data(model=ModelMaster().default().dict())
    await m.answer(
        text="Введите имя мастера",
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(kb_return_main_menu.get_back())
    )
    await state_add_master.StateAddMaster.name.set()


@dp.message_handler(state=state_add_master.StateAddMaster.name)
async def get_name_master_handler(m: Message, state: FSMContext, return_status: bool = False):
    data = await state.get_data()
    if not return_status:
        model: ModelMaster = ModelMaster().load(data.get("model"))
        model.name = m.text

        await state.update_data(
            model=model.dict()
        )

    await m.answer(
        text="Введите номер телефона мастера без +"
    )

    await state_add_master.StateAddMaster.tg_id.set()


@dp.message_handler(state=state_add_master.StateAddMaster.tg_id)
async def get_tg_id_master_handler(m: Message,
                                   session: AsyncSession,
                                   state: FSMContext, return_status=False):
    failed_message = "Это не похоже на номер"
    failed_message_not_found = "Бот не знает пользователя с таким номером"
    data = await state.get_data()
    model: ModelMaster = ModelMaster().load(data.get("model"))

    if not return_status:
        if not m.text.isdigit():
            return await m.answer(failed_message)

        user_object: ContactBarber = await ContactBarber.get_by_user_phone_number(session=session, phone_number=int(m.text))
        if user_object is None:
            return await m.answer(failed_message_not_found)
        model.tg_id = user_object.user_id

        await state.update_data(
            model=model.dict()
        )

    msg = await m.answer(formatting_input_schedule_master(model.schedules), reply_markup=get_week_days_btn())
    await state.update_data(message_ids=[msg.message_id])
    await state_add_master.StateAddMaster.schedule_start.set()  # функции в файле schedule_master.py


@dp.callback_query_handler(Text(equals=['next', 'yes']),
                           state=[state_add_master.StateAddMaster.schedule_start,
                                  state_add_master.StateAddMaster.service_confirmation])
async def service_master_handler(c: CallbackQuery, state: FSMContext, return_status: bool = False):
    data = await state.get_data()
    text = "Напишите название услуги."

    if isinstance(c, CallbackQuery):
        await c.message.edit_text(text)
    if isinstance(c, Message):
        await c.answer(text)

    await state_add_master.StateAddMaster.service_name.set()  # функции в файле service_master.py
    model: ModelMaster = ModelMaster().load(data.get('model'))
    model.load_schedule()
    await state.update_data(model=model.dict())


@dp.callback_query_handler(Text(equals='no'), state=state_add_master.StateAddMaster.service_confirmation)
async def finish_filling_service_handler(c: CallbackQuery):
    await c.message.edit_text("Отправьте работы мастера.")
    await state_add_master.StateAddMaster.photo.set()


@dp.message_handler(state=state_add_master.StateAddMaster.photo,
                    content_types=types.ContentTypes.PHOTO)
async def get_photo_album_master_works_handler(m: typing.Union[Message, CallbackQuery],
                                               state: FSMContext,
                                               album: typing.Optional[typing.List[Message]] = None,
                                               return_status: bool = False
                                               ):
    if album is None:
        album = [m]

    data = await state.get_data()
    model = ModelMaster().load(data.get("model"))
    if isinstance(m, CallbackQuery):
        msg = m.message
    else:
        msg = m

    if not return_status:
        msg = await m.answer("Сохраняем фотографии...")
        for media in album:
            photo = media.photo[-1]
            filename = f"{photo.file_id}.jpg"
            path_photo = workdirs.WORK_DIRECTORY_PHOTO_MASTER_WORKS / filename
            await media.photo[-1].download(destination_file=path_photo)
            await asyncio.sleep(0.1)
            model.photo_works.append(filename)

    text = f"""
Информация о добавляемом мастере:
Имя: {model.name} (ID {model.tg_id})
График работы:
{model.to_string_schedules}
--
Услуги:
{model.to_string_service}
    """

    await state.update_data(
        model=model.dict()
    )

    await msg.edit_text(
        text,
        reply_markup=get_add_btn()
    )


@dp.callback_query_handler(text="added", state=state_add_master.StateAddMaster.photo)
async def add_master_handler(c: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    model: ModelMaster = ModelMaster().load(data.get('model'))

    master_barber = await database.master_barber.MasterBarber(master=model.name,
                                                              telegram_id=model.tg_id
                                                              ).save(session=session)

    await database.job_barber.save_jobs_master(session, master_barber.id, schedules=model.schedules)
    await database.service_barber.save_services_master(session, master_barber.id, services=model.services)
    await database.master_works_barber.MasterWorksBarber.save(
        session, master_barber.id, master_barber.master, photos=model.photo_works
    )
    await c.message.delete()
    await c.message.answer("Мастер успешно добавлен", reply_markup=await main_menu(c.from_user.id))
    await state.finish()


async def cancel_add_master_success(c: CallbackQuery, state):
    await c.message.delete()
    await c.message.answer("Добавление мастера успешно отменено!", reply_markup=await main_menu(c.from_user.id))
    await state.finish()


async def cancel_add_master_failed(c: CallbackQuery, state):
    await get_photo_album_master_works_handler(c, state, return_status=True)
    await state_add_master.StateAddMaster.photo.set()


@dp.callback_query_handler(text=["cancel_added", "c_success", "c_cancel"],
                           state=[state_add_master.StateAddMaster.photo, state_add_master.StateAddMaster.confirm])
async def cancel_add_master_handler(c: CallbackQuery, state: FSMContext):
    c_data = c.data
    handlers = {
        'c_success': cancel_add_master_success,
        'c_cancel': cancel_add_master_failed,
    }

    handler = handlers.get(c_data)

    if handler is None:
        text = """Вы уверены, что хотите отменить?"""
        await confirmation.confirmation_handler(c, state_add_master.StateAddMaster.confirm, text)
        return

    await handler(c, state)
