import typing

from sqlalchemy import Column, Integer, String, ForeignKey, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from model.database.base import Base
from model.master import ModelServiceMaster


class ServiceBarber(Base):
    __tablename__ = "service_barber"

    id = Column(Integer, primary_key=True, autoincrement=True)
    master_id = Column(Integer, ForeignKey("master_barber.id", ondelete="CASCADE"))

    name = Column(String(60))
    time = Column(Integer, default=0)
    price = Column(Integer)
    minute = Column(Integer)

    delete_status = Column(Integer, default=0)


    def json(self):
        return {
            'id': self.id,
            'master_id': self.master_id,
            'name': self.name,
            'time': self.time,
            'minute': self.minute,
            'price': self.price,
            'delete_status': self.delete_status
        }

    async def delete(self, session: AsyncSession):
        stmt = update(ServiceBarber).where(
            ServiceBarber.id == self.id
        ).values(
            dict(
                delete_status=1
            )
        )
        await session.execute(stmt)
        await session.commit()

    @staticmethod
    async def first(session: AsyncSession,
                    *clauses):

        stmt = select(ServiceBarber).where(
            *clauses
        )
        response = await session.execute(stmt)
        return response.scalar()

    @staticmethod
    async def all(session: AsyncSession, master_id: int):

        stmt = select(ServiceBarber).where(ServiceBarber.master_id == master_id,
                                           ServiceBarber.delete_status == 0
                                           )
        response = await session.execute(stmt)

        return response.scalars().all()




async def save_services_master(
        session: AsyncSession,
        master_id: int,
        services: typing.List[ModelServiceMaster]
):
    models = []
    print(services)
    for service in services:

        models.append(
            ServiceBarber(
                master_id=master_id,
                name=service.name,
                minute=service.time,
                price=service.price
            )
        )

    session.add_all(models)
    await session.commit()


async def update_service(session: AsyncSession, service_id: int, data):

    stmt = update(ServiceBarber).where(
        ServiceBarber.id == service_id
    ).values(
        data
    )
    await session.execute(stmt)
    await session.commit()