from sqlalchemy import Column, Integer, ForeignKey, String, select, func, BigInteger
from sqlalchemy.ext.asyncio import AsyncSession

from model.database.base import Base


class StatusPresences:
    no_turnout = "no_turnout"
    appeared = "appeared"


class PresenceClient(Base):
    __tablename__ = "presences_client"

    status_presences = StatusPresences

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(60), ForeignKey("contacts_barber.user_id", ondelete='CASCADE'))
    master_id = Column(Integer, ForeignKey("master_barber.id", ondelete='CASCADE'))
    status = Column(String(10), default=status_presences.appeared)

    async def save(self, session: AsyncSession):
        session.add(self)
        await session.commit()


    @staticmethod
    async def get_statistic(session: AsyncSession, client_id: int) -> dict:

        stmt = select(
            PresenceClient.status.label('status'),
            func.count(PresenceClient.id).label('count')
        ).where(
            PresenceClient.user_id == client_id
        ).group_by(PresenceClient.status)

        response = await session.execute(stmt)
        statistics = response.mappings().all()

        data = {PresenceClient.status_presences.no_turnout: 0,
                PresenceClient.status_presences.appeared: 0}

        for _statistic in statistics:
            status = _statistic.get('status')
            count = _statistic.get('count')
            data[status] = count


        return data







