import asyncio
import datetime
import typing

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup
from sqlalchemy import select, func, Date, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.default.kb_return_main_menu import return_main_markup
from keyboards.inline.ikb_booking import cancel_booking_btn, ikb_booking_callback
from loader import dp
from model.database.master_barber import MasterBarber
from model.database.schedule_barber import ScheduleBarber


@dp.message_handler(text="Мои брони", state="*")
async def booking_handler(m: Message, session: AsyncSession,
                          state: FSMContext
                          ):
    await state.reset_state()
    stmt = select(ScheduleBarber.id.label("id"),
                  ScheduleBarber.orders.label("orders"),
                  ScheduleBarber.width.label("width"),
                  MasterBarber.master.label("master_name")
                  ).join(
        MasterBarber, MasterBarber.id == ScheduleBarber.master_id
    ).where(
        ScheduleBarber.width >= datetime.datetime.now(),
        ScheduleBarber.user_id == m.from_user.id,
        ScheduleBarber.cancel_status == 0,
        ScheduleBarber.status == ScheduleBarber.typing_status.progress
    )

    response = await session.execute(stmt)
    schedules: typing.List[ScheduleBarber] = response.mappings().all()

    if not schedules:
        return await m.answer("Нет брони", reply_markup=return_main_markup)

    text = """<b>Брони\n</b>"""
    await m.answer(text, reply_markup=return_main_markup)
    message_ids = []
    for schedule in schedules:
        text = f"{schedule.get('width').strftime('%Y.%m.%d %H:%M')} - {schedule.get('orders')}"
        await asyncio.sleep(0.3)
        msg = await m.answer(
            text=text,
            reply_markup=cancel_booking_btn(schedule)
        )
        message_ids.append(msg.message_id)
    print(message_ids)
    await state.update_data(message_ids=message_ids)


@dp.callback_query_handler(ikb_booking_callback.filter())
async def cancel_booking_handler(c: CallbackQuery,
                                 session: AsyncSession,
                                 callback_data: dict):
    booking_id = int(callback_data.get("id"))
    stmt = update(ScheduleBarber).where(ScheduleBarber.id == booking_id).values(
        dict(cancel_status=1)
    )
    await session.execute(stmt)
    await session.commit()

    await c.message.edit_text("Бронь успешно отменена!")