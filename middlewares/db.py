from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from sqlalchemy.ext.asyncio import AsyncSession



class DbMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]

    async def pre_process(self, obj, data, *args):
        pool = obj.bot.get('pool')
        print(pool)
        session: AsyncSession = pool()
        data['session'] = session


    async def post_process(self, obj, data, *args):
        if session := data.get("session"):
            await session.close()
            data.pop('session')