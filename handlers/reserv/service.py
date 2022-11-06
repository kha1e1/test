import re
import typing
import datetime
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.filters import OrFilter
from aiogram.types import CallbackQuery, Message, ReplyKeyboardMarkup, KeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

import classes.message_delete
import notifications
from data import config
from data.config import MAX_RESERVATION
from data.strings import s_reserv
from functions import f_parsing
from functions.f_formattig import formatting_service_text
from functions.f_parsing import parsing_service, parsing_service_new
from functions.f_price_and_time_list_user import price_and_time_list, price_and_time_list_user
from functions.f_reserv import interaction_service, make_reserv
from keyboards.default.kb_mainkeyboard import main_menu
from keyboards.default.kb_services import make_kb_services
from keyboards.inline.ikb_reserv import make_ikb_calendar, ikb_calendar_cb, ikb_reserv_cb, make_ikb_time, \
    ikb_reserv_time_cb, make_ikb_payment
from loader import dp
from misc import state_reserv
from model import database


async def update_master(query: CallbackQuery, state: FSMContext,
                        session: AsyncSession):
    if not isinstance(query, CallbackQuery):
        return
    if 'master' not in query.data:
        return
    _, master_id = tuple(query.data.split("_"))
    master: database.master_barber.MasterBarber = await session.get(database.master_barber.MasterBarber, int(master_id))
    updated_data = dict(id=int(master_id), name=master.master)
    await state.update_data(master=updated_data)


async def get_calendar(m: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    master: dict = data.get('master')
    master_id = master.get('id')

    busy_days_of_week = await database.job_barber.JobBarber.get_day_of_week_not_working(session, master_id)

    date_now = datetime.date.today()
    markup = make_ikb_calendar(date_now.month, busy_days_of_week)

    await m.answer(s_reserv.main,
                   reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("⬅️ Назад")))
    msg = await m.answer("Календарь", reply_markup=markup)
    await state.update_data(message_ids=[msg.message_id])

    await state_reserv.StateReserv.reserv.set()


@dp.callback_query_handler(OrFilter(Text(equals="reserv_service"), Text(startswith="master")),
                           state=[state_reserv.StateReserv.start])
@dp.message_handler(lambda x: False if x.text in "Перейти к записи" else True, state=state_reserv.StateReserv.service)
async def view_service_handler(
        query: typing.Union[CallbackQuery, Message],
        state: FSMContext,
        session: AsyncSession,
        back_status: bool = False
):
    await update_master(query, state, session)
    data = await state.get_data()
    master: dict = data.get("master")
    services = await database.service_barber.ServiceBarber.all(session, int(master.get("id")))
    service_from_data = data.get("service")
    service_user = None

    if service_from_data is not None:
        service_user = parsing_service(service_from_data)

    if isinstance(query, Message):
        service_user = parsing_service(query.text)
    print(service_user)

    if back_status:
        service_user = service_from_data

    text = formatting_service_text()
    markup = make_kb_services(services)
    await state.update_data(service=service_user)

    if isinstance(query, Message):
        if not back_status:
            return await get_calendar(query, state, session)

        await query.answer(text=text, reply_markup=markup)

    if isinstance(query, CallbackQuery):
        await query.message.delete()
        await query.message.answer(text=text, reply_markup=markup)

    await state_reserv.StateReserv.service.set()


@dp.message_handler(Text("⬅️ Назад"), state=state_reserv.StateReserv.reserv)
async def back_reserv_handler(m: Message,
                              session: AsyncSession,
                              state: FSMContext):
    state_name = await state.get_state()
    data = await state.get_data()
    handlers = {
        state_reserv.StateReserv.reserv.state: {
            "handler": view_service_handler,
            "arguments": dict(query=m, state=state, session=session, back_status=True),
            "message_collection": classes.message_delete.MessageCollection(m.from_user.id, m.bot)
        }
    }

    handler_object = handlers.get(state_name)
    handler_func = handler_object.get("handler")
    arguments: dict = handler_object.get("arguments")
    message_collection = handler_object.get('message_collection')
    await handler_func(**arguments)

    if message_collection:
        message_collection.message_ids = data.get('message_ids')
        await message_collection.delete()


@dp.message_handler(Text(equals='Перейти к записи'), state=state_reserv.StateReserv.service)
async def start_reserv_handler(m: types.Message, session: AsyncSession, state: FSMContext):
    date_now = datetime.date.today()
    data = await state.get_data()
    master: dict = data.get('master')
    master_id = master.get('id')
    busy_days_of_week = await database.job_barber.JobBarber.get_day_of_week_not_working(session, master_id)

    markup = make_ikb_calendar(date_now.month, busy_days_of_week)

    await m.answer(s_reserv.main,
                   reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("⬅️ Назад")))
    await m.answer("Календарь", reply_markup=markup)

    await state_reserv.StateReserv.reserv.set()


@dp.callback_query_handler(ikb_calendar_cb.filter(action='reserv'),
                           state=state_reserv.StateReserv.reserv)
async def query_view(query: types.CallbackQuery,
                     callback_data: typing.Dict[str, str], state: FSMContext,
                     session: AsyncSession
                     ):
    data = await state.get_data()
    master: dict = data.get('master')
    master_id = master.get('id')
    post_id = callback_data['id']
    post_ids = post_id.split(",")
    act = post_ids[0]
    date_now = datetime.datetime.now()
    busy_days_of_week = await database.job_barber.JobBarber.get_day_of_week_not_working(session, master_id)

    if act.endswith(("month_prev", "month_next")):
        month_id = post_ids[1]

        markup = make_ikb_calendar(int(month_id), busy_days_of_week)
        await query.message.edit_text('Календарь', reply_markup=markup)


    elif 'cancel' in post_id:
        markup = make_ikb_calendar(date_now.month, busy_days_of_week)
        await query.message.edit_text('Календарь', reply_markup=markup)


@dp.callback_query_handler(ikb_calendar_cb.filter(action='mast'),
                           state=state_reserv.StateReserv.reserv)
async def get_list_of_free_masters_handler(c: CallbackQuery,
                                           session: AsyncSession,
                                           callback_data: dict,
                                           state: FSMContext,
                                           ):
    """
    Получаем список свободных мастеров
    """

    data = await state.get_data()
    service: str = data.get('service')
    post_ids = callback_data.get("id").split(",")
    year = int(post_ids[1])
    month = int(post_ids[2])
    day = int(post_ids[3])

    date_user = datetime.datetime(year, month, day)
    service_name = parsing_service_new(service)
    print(service_name, "service_name")

    master: dict = data.get("master")

    await state.update_data(
        year=year,
        month=month,
        day=day
    )

    # найти время, когда слоты зарезервированы
    service_object: database.service_barber.ServiceBarber = await database.service_barber.ServiceBarber.first(
        session,
        database.service_barber.ServiceBarber.master_id == master.get("id"),
        database.service_barber.ServiceBarber.name == service_name,
        database.service_barber.ServiceBarber.delete_status == 0
    )

    # график работы мастера
    job_master_object: database.job_barber.JobBarber = await database.job_barber.JobBarber.get(session,
                                                                                               master.get('id'),
                                                                                               day_of_week=date_user.weekday()
                                                                                               )

    total_times = service_object.time + service_object.minute
    markup = await make_ikb_time(session=session,
                                 date_user=datetime.datetime(year=year, month=month, day=day),
                                 master_id=master.get("id"), job_master=job_master_object,
                                 total_times=total_times
                                 )

    if not markup:
        return await c.answer("❌ Мастер занят")

    await c.message.edit_text(
        text="Доступное время:",
        reply_markup=markup
    )


@dp.callback_query_handler(ikb_reserv_time_cb.filter(), state=state_reserv.StateReserv.reserv)
async def reserv_handler(
        c: CallbackQuery,
        state: FSMContext,
        session: AsyncSession,
        callback_data: dict
):
    """Резерв"""
    data = await state.get_data()

    service_name: str = parsing_service_new(data.get('service')).strip()
    master: dict = data.get("master")
    service_object: database.service_barber.ServiceBarber = await database.service_barber.ServiceBarber.first(
        session,
        database.service_barber.ServiceBarber.master_id == master.get("id"),
        database.service_barber.ServiceBarber.name == service_name,
        database.service_barber.ServiceBarber.delete_status == 0
    )

    total_minutes = service_object.minute + service_object.time  # в минутах время

    month = int(callback_data.get("m"))
    year = int(callback_data.get("y"))
    day = int(callback_data.get("D"))
    minute = int(callback_data.get("M"))
    hour = int(callback_data.get("H"))

    text = price_and_time_list(service_name, service_object)
    markup = make_ikb_payment()

    from_date = datetime.datetime(year=year, month=month, day=day, minute=minute, hour=hour)
    to_date = from_date + datetime.timedelta(minutes=total_minutes)

    quantity_reserv = await database.schedule_barber.get_quantity_reserv_by_user_id(session, str(c.from_user.id))

    if quantity_reserv >= MAX_RESERVATION:
        return c.answer("Вы достигли максимального количества действующих брони. ")

    order_text = f"{service_name} {service_object.price} KZT ({service_object.minute} мин)"
    service_id = await make_reserv(session, master.get('id'),
                                   from_date, to_date,
                                   userID=c.from_user.id, name=c.from_user.full_name,
                                   order=order_text)

    master_barber = await database.master_barber.MasterBarber.get(session, master.get("id"))
    client = await database.contact_barber.ContactBarber.get_by_user_id(session, c.from_user.id)

    # user = await database.

    records_statistic_user: dict = await database.client.PresenceClient.get_statistic(session,
                                                                                      c.from_user.id)  # статистика записей

    status_sent = await notifications.master.notify_reserv(c.bot,
                                                           master_barber,
                                                           client,
                                                           service_name,
                                                           from_date,
                                                           service_id,
                                                           records_statistic_user
                                                           )

    await c.message.delete()
    await c.message.answer("Выберите способ оплаты.", reply_markup=await main_menu(c.from_user.id))
    await c.message.answer(text, reply_markup=markup)

    await state.finish()
