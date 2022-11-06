import asyncio
import calendar
import datetime
import math
import os
import time
import typing

from openpyxl import load_workbook
from sqlalchemy import select, func, Date, DateTime, insert
from sqlalchemy.ext.asyncio import AsyncSession

from functions.f_price_and_time_list_user import time_user
from model import database
from model.database.contact_barber import ContactBarber
from model.database.schedule_barber import ScheduleBarber


def f_time_filling(
        from_date: datetime.datetime,
        to_date: datetime.datetime,
        step_minutes=30
):
    dates: typing.List[datetime.datetime] = []
    date: datetime.datetime = from_date

    while True:
        if from_date >= date:
            dates.append(date)
            date += datetime.timedelta(minutes=step_minutes)
            continue
        break

    return dates


def _generate_hours(
        start: int,
        end: int
):
    hour = start
    hours = [start]

    while True:

        hour += 1
        hours.append(hour)

        if hour >= end:
            break


    return hours


def get_times(
        start_hour: int, end_hour: int, minutes: list[int]
) -> typing.List[dict]:

    hours = _generate_hours(start_hour, end_hour)
    times = []

    for hour in hours:
        for minute in minutes:
            times.append(
                dict(hour=hour, minute=minute)
            )
            if max(hours) == hour:
                break
    return times



def f_get_free_dates(
        job_master: database.job_barber.JobBarber,
        year: int, month: int,
        day: int = 0,

):
    if not day:
        days = [
            i for i in range(1, calendar.monthrange(year, month)[1])
        ]
    else:
        days = [day]

    minutes = [0, 30]
    final_time_dict: typing.List[dict] = get_times(job_master.start.hour, job_master.end.hour, minutes)



    dates = [
        datetime.datetime(year=year, month=month, day=_day,
                          hour=time_tuple.get("hour"), minute=time_tuple.get('minute'))
        for time_tuple in final_time_dict for _day in days
    ]

    return dates


async def check_master(session: AsyncSession,
                       master: str,
                       year: int, month: int, day: int):
    dates = list(map(str, f_get_free_dates(year, month, day)))

    query = select(ScheduleBarber.orders_time).where(
        ScheduleBarber.master == master,
        ScheduleBarber.width.not_in(dates)
    )
    response = await session.execute(query)
    result = response.scalars().all()

    print(result)

    return result


async def make_reserv(session: AsyncSession, mas, from_date: datetime.datetime, to_date: datetime.datetime, userID,
                      name, order) -> int:
    sql1 = select(ContactBarber.Number).where(ContactBarber.user_id == userID)
    response = await session.execute(sql1)
    phone: str = response.scalar()
    date_now = datetime.datetime.now()
    schedule_barber = await ScheduleBarber(
        master_id=mas,
        width=from_date,
        too=to_date,
        user_id=userID,
        phone=phone,
        name=name,
        orders=order,
        orders_time=date_now,
        status=database.schedule_barber.ScheduleBarber.typing_status.wait,
        notify=0,
        cancel_status=0,

    ).save(session)

    return schedule_barber.id


async def f_get_busy_dates(
        session: AsyncSession,
        year: int, month: int,
):
    # busy_days = []
    # start_days = 1
    # end_days = calendar.monthrange(year, month)[1]
    # stmt = select(
    #     func.cast(ScheduleBarber.width, DateTime)
    # ).where(
    #     func.cast(ScheduleBarber.width, Date) <= datetime.date(year, month, end_days),
    #     func.cast(ScheduleBarber.too, Date) >= datetime.date(year, month, start_days)
    # )
    # response = await session.execute(stmt)
    # dates: typing.List[datetime.datetime] = response.scalars().all()  # получаем список занятых дат, которые будем анализировать
    #
    # days = {
    #
    # }  # дни которые заняты
    pass




def f_get_month_and_year(
        months: int
) -> tuple:
    """Получаем год и айди месяца"""
    date_now = datetime.datetime.now()
    max_months = 12
    month = months
    year = date_now.year

    if months > max_months:
        month = months % max_months
        if not month:  # если будет ноль
            month = 12
        year_num = math.ceil(months / max_months)
        year += year_num - 1

    return year, month


def f_get_master_records(
        master_list: list,
        schedule_list: list[dict]
):
    schedule_dict = {
        schedule['master']: schedule['reserv_count'] for schedule in
        schedule_list
    }

    master_and_records = {}

    for master in master_list:

        if reserv_count := schedule_dict.get(master):
            master_and_records[master] = reserv_count
            continue

        master_and_records[master] = 0

    return master_and_records


def interaction_service(
        service: str, service_user: str
):
    if service == service_user:
        return None

    return service_user
