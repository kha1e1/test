import logging
import ssl

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from data.config import WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV, REDIS_HOST, BOT_TOKEN
from model.database.base import Database

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)

logging_scheduler = logging.getLogger('apscheduler')
logging_scheduler.setLevel(level=logging.ERROR)

bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = RedisStorage2(REDIS_HOST)
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())
scheduler = AsyncIOScheduler()
db = Database()



async def on_shutdown(dispatcher: Dispatcher):
    print('shoo')
