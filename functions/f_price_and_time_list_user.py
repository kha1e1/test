import math

from model import database


def time_user():
    pass
    # time_sum = 0
    # timeservicesuserlist = []
    # userselectedservices = []
    # timeservicesminutes = []
    # minutes_sum = 0
    # for index, elem in enumerate(servicewithpriceslist):
    #     if index in userlist:
    #         userselectedservices.append(elem)
    # for index, nametimeservice in enumerate(timeservices):
    #     if index in userlist:
    #         timeservicesuserlist.append(nametimeservice)
    #         for i in timeservicesuserlist:
    #             time_sum = i + time_sum
    #             timeservicesuserlist.remove(i)
    # for b, minute in enumerate(timeminutes):
    #     if b in userlist:
    #         timeservicesminutes.append(minute)
    #         for i in timeservicesminutes:
    #             minutes_sum = i + minutes_sum
    #             timeservicesminutes.remove(i)
    # if minutes_sum == 60:
    #     time_sum += 1
    #     minutes_sum = 0
    # elif minutes_sum == 90:
    #     time_sum += 1
    #     minutes_sum = 30
    # elif minutes_sum == 120:
    #     time_sum += 2
    #     minutes_sum = 0
    # elif minutes_sum == 150:
    #     time_sum += 2
    #     minutes_sum = 30
    # elif minutes_sum == 180:
    #     time_sum += 3
    #     minutes_sum = 0
    #
    # print(minutes_sum)
    # return int(time_sum), int(minutes_sum)


def price_and_time_list_user(
        service_name: str,
        service_data: dict
):
    price = service_data.get("price")
    text = f"""
{service_name} ? Цена: {price} KZT
    """
    return text


def formatted_time_to_plus(
        time
) -> str:
    if time < 0:
        return 0

    return time


def formatted_time(number: int) -> str:
    if number < 10:
        return f"0{number}"

    return str(number)


def formatted_to_timer(
        seconds: int
):
    seconds = int(seconds)
    hours = formatted_time_to_plus(seconds / 3600)
    hours_round = math.floor(hours)
    minutes = formatted_time_to_plus((seconds - hours_round * 3600) / 60)
    minutes_round = math.floor(minutes)
    second = formatted_time_to_plus(seconds - hours_round * 3600 - minutes_round * 60)

    if not seconds:
        second = seconds

    return f"""{formatted_time(hours_round)}:{formatted_time(minutes_round)}:{formatted_time(math.floor(second))}"""


def price_and_time_list(
        service_name,
        service: database.service_barber.ServiceBarber
):

    total_minutes = service.minute + service.time
    timer = formatted_to_timer(
        total_minutes * 60
    )

    text = f"""
Вы выбрали следующие услуги: {service_name}
💲 Итог: {service.price} KZT.
⏳ Предполагаемое время: {timer}
    """

    return text


def delete_list():
    pass
