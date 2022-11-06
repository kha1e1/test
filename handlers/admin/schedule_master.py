import datetime

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from data import strings
from functions.f_formattig import formatting_input_schedule_master
from keyboards.inline.ikb_admin import get_times_btn, get_week_days_btn, ikb_week_of_day_cb, ikb_time_cb, get_next_btn, \
    get_not_working_day
from loader import dp
from misc import state_add_master
from model.master import ModelScheduleMaster, ModelMaster


@dp.callback_query_handler(ikb_week_of_day_cb.filter(), state=[state_add_master.StateAddMaster.schedule_start,
                                                               state_add_master.StateEditMaster.schedule_start
                                                               ])
async def input_day_of_day_master_handler(c: CallbackQuery,
                                          state: FSMContext,
                                          callback_data: dict):
    """Выбор дня недели"""
    day_of_week = callback_data.get("d")
    model_schedule = ModelScheduleMaster(day_of_week=int(day_of_week))
    state_name = await state.get_state()

    await state.update_data(
        model_schedule=model_schedule.dict()
    )
    markup = get_times_btn()
    if state_add_master.StateEditMaster.schedule_start.state == state_name:
        markup.inline_keyboard.insert(0, [get_not_working_day()])


    await c.message.edit_text(
        text=strings.s_master.input_start_time,
        reply_markup=markup
    )


@dp.callback_query_handler(ikb_time_cb.filter(),
                           state=[
                               state_add_master.StateAddMaster.schedule_start,
                               state_add_master.StateEditMaster.schedule_start]
                           )
async def input_start_time_work_master_handler(c: CallbackQuery, state: FSMContext, callback_data: dict):
    """Выбор времени работы от и до"""
    state_name = await state.get_state()
    states_object = {
        state_add_master.StateAddMaster.schedule_start.state: {
            'state': state_add_master.StateAddMaster.schedule_end
        },
        state_add_master.StateEditMaster.schedule_start.state: {
            'state': state_add_master.StateEditMaster.schedule_end,
        }
    }

    data = await state.get_data()
    hour = callback_data.get("h")
    minute = callback_data.get("m")
    model_schedule: ModelScheduleMaster = ModelScheduleMaster().load(data.get('model_schedule'))
    model_schedule.start_time = datetime.time(hour=int(hour), minute=int(minute))
    await state.update_data(model_schedule=model_schedule.dict())
    state_object = states_object.get(state_name)

    markup: InlineKeyboardMarkup = get_times_btn()
    if state_object.get('btn'):
        markup.inline_keyboard.insert(0, [get_not_working_day()])

    await c.message.edit_text(
        text=strings.s_master.input_end_time,
        reply_markup=markup
    )
    await state_object['state'].set()


@dp.callback_query_handler(ikb_time_cb.filter(), state=[state_add_master.StateAddMaster.schedule_end,
                                                        state_add_master.StateEditMaster.schedule_end
                                                        ])
async def input_end_time_work_master_handler(c: CallbackQuery,
                                             callback_data: dict,
                                             state: FSMContext):
    data = await state.get_data()
    state_name = await state.get_state()

    states = {
        state_add_master.StateAddMaster.schedule_end.state: {
            'state': state_add_master.StateAddMaster.schedule_start,
            'next_btn': get_next_btn("Перейти к заполнению услуг")
        },
        state_add_master.StateEditMaster.schedule_end.state: {
            'state': state_add_master.StateEditMaster.schedule_start,
            'next_btn': get_next_btn("Обновить"),

        }
    }
    state_object = states.get(state_name)

    hour = callback_data.get("h")
    minute = callback_data.get("m")

    model_schedule = ModelScheduleMaster().load(data.get('model_schedule'))
    model_master: ModelMaster = ModelMaster().load(data.get('model'))

    model_schedule.end_time = datetime.time(hour=int(hour), minute=int(minute))

    if model_schedule.start_time > model_schedule.end_time:
        return await c.answer(text="Ошибка. Укажите конечное время больше, чем начальное")

    model_master.append_schedule(model_schedule)
    await state.update_data(model_schedule=model_schedule.dict(),
                            model=model_master.dict())

    markup = get_week_days_btn()

    if model_master.schedules:
        markup.inline_keyboard.insert(0, [state_object.get("next_btn")])

    await c.message.edit_text(
        text=formatting_input_schedule_master(model_master.schedules),
        reply_markup=markup
    )

    await state_object['state'].set()


@dp.callback_query_handler(Text(equals='not_working_day'), state=state_add_master.StateEditMaster.schedule_start)
async def not_working_day_handler(c: CallbackQuery, state: FSMContext):
    states = {
        state_add_master.StateAddMaster.schedule_start.state: {
            'state': state_add_master.StateAddMaster.schedule_start,
            'next_btn': get_next_btn("Перейти к заполнению услуг")
        },
        state_add_master.StateEditMaster.schedule_start.state: {
            'state': state_add_master.StateEditMaster.schedule_start,
            'next_btn': get_next_btn("Обновить"),

        }
    }

    data = await state.get_data()
    state_name = await state.get_state()
    state_object = states.get(state_name)
    markup = get_week_days_btn()


    model_schedule = ModelScheduleMaster().load(data.get("model_schedule"))
    model = ModelMaster().load(data.get('model'))
    model_schedule.work = 0
    model.append_schedule(model_schedule)


    markup.inline_keyboard.insert(0, [state_object.get('next_btn')])

    await state.update_data(
        model=model.dict()
    )
    await c.message.edit_text(
        text=formatting_input_schedule_master(model.schedules),
        reply_markup=markup
    )


