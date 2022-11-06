from aiogram.dispatcher.filters.state import StatesGroup, State


class StateReserv(StatesGroup):
    start = State()
    service = State()
    reserv = State()