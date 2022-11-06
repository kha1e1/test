import typing

from aiogram.types import CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import jobs.notification
import notifications
from keyboards.inline import ikb_notify
from loader import dp, scheduler
from model import database


@dp.callback_query_handler(ikb_notify.ikb_notify_master_cb.filter(act='access'), state="*")
async def processing_access_handler(c: CallbackQuery,
                                    session: AsyncSession,
                                    callback_data: dict):
    schedule_id = int(callback_data.get("s_id"))
    stmt = select(
        database.schedule_barber.ScheduleBarber,
        database.master_barber.MasterBarber
    ).join(
        database.master_barber.MasterBarber,
        database.master_barber.MasterBarber.id == database.schedule_barber.ScheduleBarber.master_id
    ).where(
        database.schedule_barber.ScheduleBarber.id == schedule_id
    )

    response = await session.execute(stmt)
    objects: typing.List[
        typing.Tuple[
            database.schedule_barber.ScheduleBarber,
            database.master_barber.MasterBarber
        ]
    ] = response.all()

    schedule_barber, master_barber = objects[0]
    await notifications.client.notify_acceptance_of_the_reservation(master_barber, schedule_barber)

    await schedule_barber.update(session, status=database.schedule_barber.ScheduleBarber.typing_status.progress)

    scheduler.add_job(
        jobs.notification.notice_of_attendance_master,
        run_date=schedule_barber.too,
        args=(schedule_id,),
        id=str(schedule_id)
    )

    await c.message.edit_text("Запись принята.")


@dp.callback_query_handler(ikb_notify.ikb_notify_master_cb.filter(act='refuse'), state="*")
async def processing_refused_handler(c: CallbackQuery,
                                     session: AsyncSession,
                                     callback_data: dict):
    schedule_id = int(callback_data.get("s_id"))
    stmt = select(
        database.schedule_barber.ScheduleBarber,
        database.master_barber.MasterBarber
    ).join(
        database.master_barber.MasterBarber,
        database.master_barber.MasterBarber.id == database.schedule_barber.ScheduleBarber.master_id
    ).where(
        database.schedule_barber.ScheduleBarber.id == schedule_id
    )

    response = await session.execute(stmt)
    objects: typing.List[
        typing.Tuple[
            database.schedule_barber.ScheduleBarber,
            database.master_barber.MasterBarber
        ]
    ] = response.all()
    print(objects)
    schedule_barber, master_barber = objects[0]

    await notifications.client.notify_entry_canceled(master_barber, schedule_barber)
    await schedule_barber.delete_record(session)

    await c.message.edit_text("Запись отменена")


@dp.callback_query_handler(ikb_notify.ikb_notify_master_cb.filter(act=["appeared", "no_turnout"]), state='*')
async def processing_turnout_handler(c: CallbackQuery,
                                     session: AsyncSession,
                                     callback_data: dict):
    schedule_id = int(callback_data.get("s_id"))
    action = callback_data.get("act")
    print(schedule_id)

    stmt = select(
        database.schedule_barber.ScheduleBarber
    ).where(
        database.schedule_barber.ScheduleBarber.id == schedule_id
    )

    schedule_master: database.schedule_barber.ScheduleBarber = await session.scalar(stmt)

    handlers = {
        "no_turnout": {
            "text": "Клиент не явился.",
            "status": database.client.PresenceClient.status_presences.no_turnout
        },
        "appeared": {
            "text": "Клиент явился.",
            "status": database.client.PresenceClient.status_presences.appeared
        }
    }

    handler = handlers.get(action)

    presence_client = database.client.PresenceClient(
        user_id=schedule_master.user_id,
        master_id=schedule_master.master_id,
        status=handler.get('status')
    )
    await presence_client.save(session)
    await c.message.edit_text(handler.get('text'))
