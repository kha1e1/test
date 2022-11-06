from aiogram.dispatcher.filters.state import StatesGroup, State


class StateAddMaster(StatesGroup):
    name = State()
    tg_id = State()

    service_name = State()
    service_price = State()
    service_time = State()
    service_confirmation = State()

    schedule_start = State()
    schedule_end = State()

    photo = State()

    confirm = State()


class StateEditMaster(StatesGroup):
    choice_master = State()
    choice_action = State()
    choice_action_service = State()

    service_delete = State()
    service_edit = State()
    service_edit_start = State()

    service_name = State()
    service_price = State()
    service_time = State()

    service_confirmation = State()

    schedule_start = State()
    schedule_end = State()

    photo = State()


class StateDeleteMaster(StatesGroup):
    start = State()
