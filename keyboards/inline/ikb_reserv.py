import datetime, os
import math
import typing

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
import calendar

from sqlalchemy import select, func, Date
from sqlalchemy.ext.asyncio import AsyncSession

from data import dictionaries
from functions.f_massive import separation_massive
from functions.f_reserv import check_master, f_get_busy_dates, f_get_month_and_year, f_get_free_dates, f_time_filling
from model import database
from model.database.master_barber import MasterBarber
from model.database.schedule_barber import ScheduleBarber

ikb_calendar_cb = CallbackData('post', 'id', 'action')
ikb_reserv_cb = CallbackData("res", "ma", )  # m - master, r - свободных записей
ikb_reserv_time_cb = CallbackData("t", "m", "y", 'M', 'D', 'H')


def make_ikb_calendar(month_num: int, busy_days_of_week: typing.List[int]):
    year_num, month = f_get_month_and_year(month_num)

    ikb_calendar = InlineKeyboardMarkup(7)
    date_now = datetime.datetime.now()
    ignore_callback = "x"
    busy_callback = "busy"
    ignore_text = "x"
    prev_month = InlineKeyboardButton(text="<<",
                                      callback_data=ikb_calendar_cb.new(id=f"month_prev,{month_num - 1}",
                                                                        action='reserv'))
    next_month = InlineKeyboardButton(text=">>",
                                      callback_data=ikb_calendar_cb.new(id=f"month_next,{month_num + 1}",
                                                                        action='reserv'))

    if date_now.month == month and date_now.year == year_num:
        prev_month.callback_data = ignore_callback
        prev_month.text = ignore_text

    month_name = InlineKeyboardButton(text=f"{dictionaries.calendar.months_name.get(month)} {year_num}",
                                      callback_data=ikb_calendar_cb.new(id='month', action="x"))
    ikb_calendar.row(*[
        prev_month, month_name, next_month
    ])
    ikb_calendar.row()

    for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]:
        ikb_calendar.insert(
            InlineKeyboardButton(day, callback_data=ignore_callback)
        )

    month_calendar = calendar.monthcalendar(year=year_num, month=month)
    for week in month_calendar:
        ikb_calendar.row()
        for index, day in enumerate(week, 0):

            if day == 0:
                ikb_calendar.insert(InlineKeyboardButton(" ", callback_data="x"))
                continue

            if index in busy_days_of_week:
                ikb_calendar.insert(InlineKeyboardButton("❌", callback_data="x"))
                continue

            if date_now.year == year_num and date_now.month == month and date_now.day > day:
                ikb_calendar.insert(
                    InlineKeyboardButton("❌", callback_data=busy_callback)
                )
                continue



            callback_id = f"date,{str(year_num)},{str(month).zfill(2)},{str(day).zfill(2)}"
            ikb_calendar.insert(
                InlineKeyboardButton(str(day),
                                     callback_data=ikb_calendar_cb.new(
                                         id=callback_id,
                                         action='mast')
                                     )

            )

    return ikb_calendar


async def make_ikb_masters(
        masters: list,
):
    ikb_masters = InlineKeyboardMarkup(row_width=3)

    for master in masters:
        button = InlineKeyboardButton(text=master, callback_data=ikb_reserv_cb.new(ma=master))
        ikb_masters.add(button)
    ikb_masters.add(
        InlineKeyboardButton(text="Отменить", callback_data=ikb_calendar_cb.new(id="cancel", action='reserv')))
    return ikb_masters

    # path = os.getcwd()
    # try:
    #    file = path + "/Config.xlsx"
    # except OSError:
    #    file = path + "\Config.xlsx"
    # wb_obj = load_workbook(filename=file)
    # wsheet = wb_obj['Masters']
    # for num, name in wsheet.iter_rows(values_only=True):
    #    if num == "#":
    #        continue
    #    masters.append(name)
    # for mas in masters:
    #    if await check_master(date, mas) != "All reserved":
    #        ikb_masters.add(InlineKeyboardButton(text=mas,
    #                                             callback_data=ikb_calendar_cb.new(id='master,' + mas + "," + date, action='reserv')))
    # ikb_masters.add(InlineKeyboardButton(text="Отменить",
    #                                     callback_data=ikb_calendar_cb.new(id="cancel", action='reserv')))


async def make_ikb_time(
        session: AsyncSession,
        master_id: int,
        date_user: datetime.datetime,
        job_master: database.job_barber.JobBarber,
        total_times: int
):
    ikb_time = InlineKeyboardMarkup(row_width=3)

    stmt = select(ScheduleBarber.width.label("width"),
                  ScheduleBarber.too.label("too")
                  ).where(
        func.cast(ScheduleBarber.width, Date) == date_user.date(),
        ScheduleBarber.master_id == master_id,
        ScheduleBarber.cancel_status == 0
    )  # достаем список зарезервированных дат

    if not job_master.work:
        return None

    dates_free = f_get_free_dates(job_master,
                                  year=date_user.year,
                                  month=date_user.month,
                                  day=date_user.day)  # список записей допустимых на один день (с 9 до 17)
    response = await session.execute(stmt)
    dates_reserv = response.mappings().all()
    reserv_dates = []

    for date_reserv in dates_reserv:
        from_date = date_reserv.get('width')
        to_date = date_reserv.get("too")
        reserv_dates += f_time_filling(from_date, to_date)

    date_now = datetime.datetime.now()

    dates = [_date for _date in dates_free if _date not in reserv_dates and _date >= date_now]  # список свободных слотов

    if not dates:
        return []

    records = round(total_times / 30)

    dates = dates[:-records]



    for date in dates:
        ikb_time.insert(InlineKeyboardButton(text=date.strftime("%H:%M"),
                                             callback_data=ikb_reserv_time_cb.new(
                                                 m=date.month,
                                                 y=date.year,
                                                 M=date.minute,
                                                 H=date.hour,
                                                 D=date.day)))

    ikb_time.add(InlineKeyboardButton(text="Отменить",
                                      callback_data=ikb_calendar_cb.new(id="cancel", action='reserv')))

    return ikb_time


def make_ikb_payment():
    inline_payment_services = InlineKeyboardMarkup(row_width=2)
    inline_payment_bankcard_button = InlineKeyboardButton("Картой💳", url="https://kaspi.kz")
    inline_payment_cash = InlineKeyboardButton("В барбершопе 🏢", callback_data="cashpayment")
    inline_payment_services.add(inline_payment_bankcard_button, inline_payment_cash)
    return inline_payment_services
