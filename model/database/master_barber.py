import json

from sqlalchemy import Column, Integer, String, func, select, insert, BigInteger
from sqlalchemy.ext.asyncio import AsyncSession

from model.database.base import Base


class MasterBarber(Base):
    __tablename__ = "master_barber"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, default=None)
    master = Column(String(60))
    delete_status = Column(Integer, default=0)

    @staticmethod
    async def get_by_name(session: AsyncSession, master_name: str):
        stmt = select(MasterBarber).where(
            MasterBarber.master == master_name,
            MasterBarber.delete_status == 0
        )
        return await session.scalar(stmt)

    @staticmethod
    async def get(session: AsyncSession, master_id: int):
        stmt = select(MasterBarber).where(
            MasterBarber.id == master_id,
            MasterBarber.delete_status == 0
        )
        response = await session.execute(stmt)
        return response.scalar()

    @staticmethod
    async def all(session: AsyncSession):
        stmt = select(MasterBarber).where(
            MasterBarber.delete_status == 0
        )
        response = await session.execute(stmt)
        return response.scalars().all()

    async def count_by_name(self, session: AsyncSession):

        stmt = select(func.count(MasterBarber.id)).where(
            MasterBarber.master == self.master,
            MasterBarber.delete_status == 0

        )
        response = await session.execute(stmt)
        return response.scalar()


    async def save(self, session: AsyncSession):

        count_name = await self.count_by_name(session)
        if count_name:
            self.master = self.master + f" №{count_name+1}"


        session.add(self)

        await session.commit()

        return self









