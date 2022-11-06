import typing

from sqlalchemy import Column, Integer, ForeignKey, Time, String, select
from sqlalchemy.ext.asyncio import AsyncSession

from model import master
from model.database.base import Base
from model.master import ModelScheduleMaster


class JobBarber(Base):
    __tablename__ = "jobs_barber"

    id = Column(Integer, primary_key=True, autoincrement=True)
    master_id = Column(Integer, ForeignKey("master_barber.id", ondelete="CASCADE"))
    day_of_week = Column(Integer)  # день недели
    start = Column(Time)
    end = Column(Time)
    work = Column(Integer)
    comment = Column(String(100))


    @property
    def start_time(self):
        return self.start

    @property
    def end_time(self):
        return self.end

    @staticmethod
    async def all(session: AsyncSession, master_id: int):
        stmt = select(JobBarber).where(
            JobBarber.master_id == master_id
        )
        response = await session.scalars(stmt)

        return response.all()

    @staticmethod
    async def get(session: AsyncSession,
                  master_id: int,
                  day_of_week: int):
        stmt = select(JobBarber).where(
            JobBarber.day_of_week == day_of_week,
            JobBarber.master_id == master_id
        )
        response = await session.execute(stmt)
        return response.scalar()

    @staticmethod
    async def get_day_of_week_not_working(session: AsyncSession, master_id: int):
        stmt = select(JobBarber.day_of_week).where(
            JobBarber.master_id == master_id,
            JobBarber.work == 0
        )
        response = await session.execute(stmt)

        return response.scalars().all()



    @staticmethod
    async def update(session: AsyncSession,
                     job_id: int, data: master.ModelScheduleMaster):
        if job_id:
            job: JobBarber = await session.get(JobBarber, job_id)
        else:
            job = JobBarber()
        job.end = data.end_time
        job.start = data.start_time
        job.work = data.work
        session.add(job)
        await session.commit()


async def save_jobs_master(
        session: AsyncSession,
        master_id: int,
        schedules: typing.List[ModelScheduleMaster]
):
    models = []
    for schedule in schedules:
        models.append(
            JobBarber(
                master_id=master_id,
                day_of_week=schedule.day_of_week,
                start=schedule.start_time,
                end=schedule.end_time,
                work=schedule.work
            )
        )
    session.add_all(models)
    await session.commit()
