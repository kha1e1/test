from sqlalchemy import Column, Integer, String, select, BigInteger
from sqlalchemy.ext.asyncio import AsyncSession

from model.database.base import Base


class ContactBarber(Base):
    __tablename__ = "contacts_barber"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(60), unique=True)
    Full_name = Column(String(60))
    Number = Column(String(60))
    Reg_time = Column(String(60))

    async def save(self, session: AsyncSession):
        session.add(self)
        await session.commit()

        return self

    @staticmethod
    async def get_by_user_id(session: AsyncSession,
                             user_id: int):
        stmt = select(ContactBarber).where(
            ContactBarber.user_id == user_id
        )

        response = await session.execute(stmt)

        return response.scalar()

    @staticmethod
    async def get_by_user_phone_number(session: AsyncSession,
                                       phone_number: str):
        stmt = select(ContactBarber).where(
            ContactBarber.Number == phone_number
        )
        response = await session.execute(stmt)

        return response.scalar()
