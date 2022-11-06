import datetime

from aiogram import Bot

from functions.f_message import send_message
from keyboards.inline import ikb_notify
from model import database


async def notify_reserv(bot: Bot,
                        master: database.master_barber.MasterBarber,
                        client: database.contact_barber.ContactBarber,
                        service_name: str,
                        width: datetime.datetime,
                        service_id: int,

                        records_client: dict

                        ):
    text = f"""
Уведомление о бронировании.
Номер телефона клиента: {client.Number}
Дата записи: {width.strftime("%d.%m.%Y %H:%M")}
Услуга: {service_name}

<i>Cтатистика</i>
Неявок: <code>{records_client.get("no_turnout")}</code>
Явок: <code>{records_client.get("appeared")}</code>

    """

    sent_status = await send_message(
        bot, text=text, chat_id=master.telegram_id,
        reply_markup=ikb_notify.get_notify_btn_for_master(service_id=service_id)
    )

    return sent_status


async def notify_about_turnout_client(
        bot: Bot,
        master: database.master_barber.MasterBarber,
        schedule: database.schedule_barber.ScheduleBarber
):
    text = f"""
Здравствуйте, клиент <b>{schedule.name}</b> явился на вашу услугу в <b>{schedule.width.strftime("%d.%m.%Y %H:%M")}</b>?
"""

    await send_message(
        bot, text=text, chat_id=master.telegram_id,
        reply_markup=ikb_notify.get_btn_about_turnout(schedule.id)
    )
