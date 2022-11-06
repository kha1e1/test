import datetime
import typing


def formatting_path_in_windows_to_linux(
        paths: typing.List[str], system: str = 'LINUX'
) -> typing.List[str]:
    if system in 'LINUX':
        paths = list(map(
            lambda x: x.replace("\\", "/"),
            paths
        ))

    return paths


def formatting_master_text(
        master: typing.Optional[str] = None
):
    master_name_default = 'не выбран'
    if master is not None:
        master_name_default = master

    text = f"""
Выберите мастера из списка ниже.
    """

    return text


def formatting_service_text(
):
    text = """
Выберите услугу из списка ниже."""

    return text


def formatting_string_to_time(string_time: str):
    return datetime.datetime.strptime(string_time, "%H:%M").time()


def formatting_input_schedule_master(schedules_master=None):
    """schedule master union database.job_master.JobBarber ModelScheduleMaster"""

    data = {0: "-", 1: '-', 2: '-', 3: '-', 4: '-', 5: '-', 6: '-'}
    if schedules_master is None:
        schedules_master = []
    for schedule_master in schedules_master:

        if not schedule_master.work:
            continue
        data.update(
            {
                schedule_master.day_of_week:
                    f"{schedule_master.start_time.strftime('%H:%M')}:{schedule_master.end_time.strftime('%H:%M')}"
            }
        )

    week_names = [
        'Понедельник', "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"
    ]
    text = "\n".join(
        f"{week}: {data.get(index)}" for index, week in enumerate(week_names)
    )
    return text
