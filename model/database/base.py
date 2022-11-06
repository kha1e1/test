import typing

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class Database:
    def __init__(self):
        self.pool: typing.Optional[sessionmaker] = None
        self.engine: typing.Optional[AsyncEngine] = None

    async def create_pool(self, connection_uri: str = "postgresql+asyncpg://postgres:postgres@localhost/postgres"):
        engine = create_async_engine(url=connection_uri, pool_timeout=60)
        self.engine = engine
        # async with engine.begin() as conn:
        #     await conn.run_sync(Base.metadata.drop_all)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        pool = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)

        self.pool = pool

        return pool
