import ssl
from typing import Tuple, List

import aiojobs
from aiogram import Bot
from aiohttp import web
from loguru import logger

import data
import jobs
import web_handlers
from loader import bot, dp, ssl_context, SSL_CERTIFICATE, db, scheduler
from model.database.gallery_barber import load_gallery_barber
from notify_admins import on_startup_notify


async def on_startup(app: web.Application):
    import middlewares
    import handlers
    logger.info('Configure Webhook URL to: {url}', url=data.config.WEBHOOK_URL)
    await dp.bot.set_webhook(data.config.WEBHOOK_URL, certificate=SSL_CERTIFICATE)

    pool = await db.create_pool(data.config.PATH_URI_DB)
    dp.bot['pool'] = pool

    await load_gallery_barber(pool(), data.config.GALLERY_BARBER_PATH)
    scheduler.add_jobstore('redis', jobs_key='reserv.jobs', run_times_key='reserv.run_times',
                           host=data.config.REDIS_HOST)

    scheduler.add_job(jobs.notification.notification_one_day_before_client_job, trigger='interval', hours=1)
    scheduler.start()
    await on_startup_notify(dp)


async def on_shutdown(app: web.Application):
    app_bot: Bot = app['bot']
    await app_bot.close()


async def init(**kwargs) -> web.Application:
    scheduler = await aiojobs.create_scheduler()
    app = web.Application()
    subapps: List[Tuple[str, web.Application]] = [
        ('/tg/webhooks/', web_handlers.tg_updates.tg_updates_app),
    ]
    for prefix, subapp in subapps:
        subapp['bot'] = bot
        subapp['dp'] = dp
        subapp['scheduler'] = scheduler
        app.add_subapp(prefix, subapp)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    return app


if __name__ == "__main__":
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    SSL_CERTIFICATE = open(data.config.WEBHOOK_SSL_CERT, "rb").read()
    ssl_context.load_cert_chain(data.config.WEBHOOK_SSL_CERT, data.config.WEBHOOK_SSL_PRIV)

    web.run_app(init(), host=data.config.WEBHOOK_HOST,
                port=data.config.WEBAPP_PORT, ssl_context=ssl_context)
