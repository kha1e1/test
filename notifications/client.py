from aiogram import Bot

from functions.f_message import send_message
from loader import bot
from model import database


async def notify_entry_canceled(
        master_barber: database.master_barber.MasterBarber,
        schedule_barber: database.schedule_barber.ScheduleBarber):
    text = f"""
К сожалению, мастер  {master_barber.master} отменил:
Вашу услугу: {schedule_barber.orders.strip()}
    """

    await send_message(
        bot, text=text, chat_id=schedule_barber.user_id
    )


async def notify_acceptance_of_the_reservation(
        master_barber: database.master_barber.MasterBarber,
        schedule_barber: database.schedule_barber.ScheduleBarber
):
    """
    Уведомление о принятии брони
    """

    text = f"""
Мастер {master_barber.master} принял вашу бронь. Просим быть вовремя в {schedule_barber.width.strftime('%d.%m.%Y %H:%M')}.
Услуга: {schedule_barber.orders.strip()}
<i>Мы вам напомним за день до начала записи.</i>
    """
    await bot.send_message(
        chat_id=schedule_barber.user_id,
        text=text
    )


async def notification_one_day_before_client(
        schedule: database.schedule_barber.ScheduleBarber
):
    text = f"""
Уведомляем, что завтра у вас запись {schedule.width.strftime("%d.%m.%Y %H:%M")} на {schedule.orders.strip()}
    """

    await send_message(
        bot=bot,
        text=text,
        chat_id=schedule.user_id
    )
