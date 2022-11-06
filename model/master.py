import datetime
import logging
import typing
from dataclasses import dataclass

import dataclass_factory
from dataclass_factory import Schema

import data.dictionaries.calendar
from data import dictionaries
from functions.f_formattig import formatting_string_to_time


class BaseModel:
    def dict(self):
        factory = dataclass_factory.Factory(default_schema=Schema(omit_default=True))
        return factory.dump(self, self.__class__.__name__)

    def load(self, data: dict):
        factory = dataclass_factory.Factory(default_schema=Schema(omit_default=True))
        query = factory.load(data, self.__class__)
        return query


@dataclass
class ModelScheduleMaster(BaseModel):
    id: int = 0
    day_of_week: typing.Optional[int] = None
    start_time: typing.Optional[datetime.time] = None
    end_time: typing.Optional[datetime.time] = None
    work: int = 1  # 1 - работает, 0 - не работает
    comment: str = "Время работы"

    def __eq__(self, other: 'ModelScheduleMaster'):
        return [self.start_time, self.end_time,
                self.day_of_week, self.work] == [other.start_time, other.end_time,
                                                 other.day_of_week, other.work]



    def convert(self, __object: 'database.job_barber.JobBarber'):
        self.id = __object.id
        self.day_of_week = __object.day_of_week
        self.end_time = __object.end_time
        self.start_time = __object.start_time
        self.work = __object.work

        return self


@dataclass
class ModelServiceMaster(BaseModel):
    name: typing.Optional[str] = None
    price: typing.Optional[int] = None
    time: typing.Optional[int] = None




@dataclass
class ModelMaster(BaseModel):
    name: str = None
    tg_id: typing.Optional[int] = None
    schedules: typing.List[ModelScheduleMaster] = None
    services: typing.List[ModelServiceMaster] = None
    photo_works: typing.List[str] = None

    def append_schedule(self, schedule: ModelScheduleMaster):
        index = None

        index_list = []
        for _index, _schedule in enumerate(self.schedules, 0):


            if _schedule.day_of_week == schedule.day_of_week:
                if _schedule.id:
                    schedule.id = _schedule.id
                index_list.append(_index)

        print(index_list)
        for index in index_list:
            print("удаление")
            self.schedules.pop(index)
        print(schedule)

        self.schedules.append(schedule)

    def default(self):
        self.name = ""
        self.tg_id = 0
        self.schedules = []
        self.services = []
        self.photo_works = []
        return self

    def load_schedule(self):

        default_day_of_week = {
            index_of_week: ModelScheduleMaster(
                day_of_week=index_of_week,
                work=0,
            )

            for day_of_week, index_of_week in data.dictionaries.calendar.day_of_weeks.items()
        }
        for schedule in self.schedules:
            default_day_of_week.pop(
                schedule.day_of_week
            )

        for _, schedule in default_day_of_week.items():

            self.schedules.append(
                schedule
            )





    def parse_schedule(self, text: str):
        """
пн 9:00-17:00
вт 9:00-17:00
ср 9:00-17:00
чт 9:00-17:00
пт 9:00-17:00
cб -
вс -
        :param text:
        :return:
        """
        max_day_of_week = 7

        day_of_weeks = text.split("\n")
        if len(day_of_weeks) != max_day_of_week:
            return False

        for day_of_week in day_of_weeks:

            status_work_default = 1  # рабочий
            _day_of_week, times = tuple(day_of_week.split())
            if times.strip() == "-":
                status_work_default = 0
                start_time, end_time = (None, None)
            else:
                start_time, end_time = list(map(lambda x: formatting_string_to_time(x.strip()), times.split("-")))

            day_of_week_int = dictionaries.calendar.day_of_weeks.get(_day_of_week.strip())
            if day_of_week_int is None:
                print(_day_of_week)

            self.schedules.append(
                ModelScheduleMaster(
                    day_of_week=day_of_week_int,
                    start_time=start_time,
                    end_time=end_time,
                    work=status_work_default,
                )
            )

        return True

    @staticmethod
    def _work_time(model: ModelScheduleMaster):

        if model.end_time and model.start_time:
            return f"{model.start_time.strftime('%H:%M')}-{model.end_time.strftime('%H:%M')}"

        return "-"



    @property
    def to_string_schedules(self):
        day_of_week_reverse = {
            value: key for key, value in dictionaries.calendar.day_of_weeks.items()
        }
        return "\n".join(
            [
                f"{day_of_week_reverse.get(model.day_of_week)} {self._work_time(model)}" for model in self.schedules
            ]
        )

    @property
    def to_string_service(self):

        return "\n".join(
            [
                f"{model.name}, {model.price} KZT ({model.time} минут)" for model in self.services
            ]
        )
