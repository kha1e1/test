import typing

from sqlalchemy import Column, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession

from model.database.base import Base


class GallerybBarber(Base):
    __tablename__ = "gallery_barber"

    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column(String(128))
    system = Column(String(128), default='LINUX')

    @staticmethod
    async def all(session: AsyncSession):

        stmt = select(GallerybBarber)
        response = await session.execute(stmt)
        return response.scalars().all()



async def load_gallery_barber(
        session: AsyncSession,
        photos: typing.List[str]
):
    models = []

    for photo_path in photos:
        models.append(
            GallerybBarber(
                path=photo_path,
                system='LINUX'
            )
        )

    session.add_all(models)
    await session.commit()