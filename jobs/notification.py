import asyncio
import datetime
import typing

from sqlalchemy import select, func, Date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

import notifications.client
from loader import db, bot
from model import database


async def notification_one_day_before_client_job():
    pool: sessionmaker = db.pool
    session: AsyncSession = pool()

    stmt = select(database.schedule_barber.ScheduleBarber).where(
        func.cast(database.schedule_barber.ScheduleBarber.width, Date) == datetime.date.today() - datetime.timedelta(days=1),
        database.schedule_barber.ScheduleBarber.notify == 0,
        database.schedule_barber.ScheduleBarber.status == database.schedule_barber.ScheduleBarber.typing_status.progress
    )

    response = await session.execute(stmt)
    schedules: typing.List[
        database.schedule_barber.ScheduleBarber,
    ] = response.scalars().all()

    if not schedules:
        await session.close()
        return

    timeout = 0.5
    for schedule in schedules:
        await notifications.client.notification_one_day_before_client(schedule)
        await schedule.update(session, notify=1)
        await asyncio.sleep(timeout)

    await session.close()


async def notice_of_attendance_master(
        schedule_id: int
):
    """Уведомления с вопросом о явки клиента"""

    pool: sessionmaker = bot.get('pool')
    session: AsyncSession = pool()

    stmt = select(
        database.master_barber.MasterBarber, database.schedule_barber.ScheduleBarber
    ).select_from(
        database.master_barber.MasterBarber
    ).join(database.schedule_barber.ScheduleBarber,
           database.schedule_barber.ScheduleBarber.master_id == database.master_barber.MasterBarber.id).where(

        database.schedule_barber.ScheduleBarber.id == schedule_id
    )
    response: typing.Tuple[
        database.master_barber.MasterBarber, database.schedule_barber.ScheduleBarber
    ] = (await session.execute(stmt)).all()
    master_barber, schedule_barber = response[0]
    await schedule_barber.update(session, status=database.schedule_barber.ScheduleBarber.typing_status.finish)
    await notifications.master.notify_about_turnout_client(bot, master_barber, schedule_barber)
    await session.close()



