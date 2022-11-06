import typing

from sqlalchemy import Column, Integer, String, TEXT, ForeignKey, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from model.database.base import Base


class MasterWorksBarber(Base):
    __tablename__ = "masterWorks_barber"

    id = Column(Integer, primary_key=True,
                autoincrement=True)
    master_id = Column(Integer, ForeignKey("master_barber.id", ondelete="CASCADE"))
    name = Column(String(100))
    photo_path = Column(TEXT)
    system = Column(String(100))

    @staticmethod
    async def all(session: AsyncSession, master_id: int):
        stmt = select(MasterWorksBarber).where(
            MasterWorksBarber.master_id == master_id
        )
        response = await session.execute(stmt)

        return response.scalars().all()

    @staticmethod
    async def delete(session: AsyncSession, master_id: int):

        stmt = delete(MasterWorksBarber).where(
            MasterWorksBarber.master_id == master_id
        )
        await session.execute(stmt)
        await session.commit()




    @staticmethod
    async def save(session: AsyncSession,
                   master_id: int,
                   master_name: str,
                   photos: typing.List[str]):
        models = []
        default_system = "LINUX"
        for photo in photos:
            models.append(
                MasterWorksBarber(
                    master_id=master_id,
                    name=master_name,
                    photo_path=photo,
                    system=default_system
                )
            )
        session.add_all(models)
        await session.commit()


