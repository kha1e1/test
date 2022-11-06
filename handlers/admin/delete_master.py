import typing

from aiogram.dispatcher.filters import Text
from aiogram.types import Message
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.default import kb_edit_master, kb_return_main_menu
from loader import dp
from misc import state_add_master
from model import database


@dp.message_handler(Text(equals="Удалить мастера"))
async def start_delete_master_handler(m: Message, session: AsyncSession):
    masters = await database.master_barber.MasterBarber.all(session)
    markup = kb_edit_master.get_master_btn(masters)
    markup.add(
        kb_return_main_menu.get_back()
    )
    await m.answer(
        text="Выберите мастера.\n<i>При нажатии на кнопку - мастер удалится</i>",
        reply_markup=markup
    )
    await state_add_master.StateDeleteMaster.start.set()


@dp.message_handler(state=state_add_master.StateDeleteMaster.start)
async def delete_master_handler(m: Message, session: AsyncSession):
    master_name = m.text

    stmt = select(
        database.master_barber.MasterBarber, database.schedule_barber.ScheduleBarber
    ).join(database.schedule_barber.ScheduleBarber,
           and_(database.schedule_barber.ScheduleBarber.master_id == database.master_barber.MasterBarber.id,
                database.schedule_barber.ScheduleBarber.status == database.schedule_barber.ScheduleBarber.typing_status.progress),
           isouter=True,
           ).where(
        database.master_barber.MasterBarber.master == master_name,
        database.master_barber.MasterBarber.delete_status == 0
    )

    response = await session.execute(stmt)
    master, schedule_master = response.all()[0]



    if schedule_master:
        return await m.answer("Вы не можете удалить мастера! У него есть действующие записи")

    master.delete_status = 1
    session.add(master)
    await session.commit()

    masters = await database.master_barber.MasterBarber.all(session)
    markup = kb_edit_master.get_master_btn(masters)
    markup.add(
        kb_return_main_menu.get_back()
    )
    await m.answer("Мастер успешно удален.", reply_markup=markup)



