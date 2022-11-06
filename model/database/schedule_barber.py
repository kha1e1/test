import datetime
import typing

from sqlalchemy import Column, Integer, String, DateTime, TEXT, ForeignKey, delete, update, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from model.database.base import Base


class TypingScheduleStatus:
    wait = "waiting"
    progress = 'in progress'
    finish = 'finish'


class ScheduleBarber(Base):
    __tablename__ = "shedule_barber"

    typing_status = TypingScheduleStatus

    id = Column(Integer, primary_key=True,
                autoincrement=True)
    master_id = Column(Integer, ForeignKey("master_barber.id", ondelete="CASCADE"))
    width = Column(DateTime)
    too = Column(DateTime)
    user_id = Column(String(100))
    phone = Column(String(50))
    name = Column(String(100))
    orders = Column(TEXT)
    orders_time = Column(DateTime)
    status = Column(String(100), default=typing_status.wait)
    cancel_status = Column(Integer)
    notify = Column(Integer, default=0)  # уведомление за день до начала записи

    async def update(self, session: AsyncSession, clauses: typing.Optional[list] = None, **data):
        if not clauses:
            clauses = [ScheduleBarber.id == self.id]

        stmt = update(ScheduleBarber).values(
            **data
        ).where(
            *clauses
        )
        await session.execute(stmt)
        await session.commit()

    async def delete_record(self, session: AsyncSession):
        stmt = update(ScheduleBarber).values(
            cancel_status=1
        ).where(
            ScheduleBarber.id == self.id
        )
        await session.execute(stmt)
        await session.commit()

    async def save(self, session: AsyncSession):
        self.status = self.typing_status.wait
        session.add(self)
        await session.commit()

        return self




async def get_quantity_reserv_by_user_id(
        session: AsyncSession,
        user_id: str
) -> int:
    date_now = datetime.datetime.now()
    stmt = select(func.count(ScheduleBarber.id)).where(
        ScheduleBarber.width >= date_now,
        ScheduleBarber.user_id == user_id
    )

    return await session.scalar(stmt)