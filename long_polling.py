from aiogram import executor, Dispatcher
import jobs
from data.strings import s_main
from data.config import PATH_URI_DB, GALLERY_BARBER_PATH, REDIS_HOST
from keyboards.default import kb_startkeyboard
from keyboards.default.kb_mainkeyboard import main_menu
from loader import dp, scheduler, db
import middlewares, handlers
from model.database.gallery_barber import load_gallery_barber
from notify_admins import on_startup_notify


async def on_startup(dispatcher: Dispatcher):
    # Уведомляет про запуск
    pool = await db.create_pool(PATH_URI_DB)
    dispatcher.bot['pool'] = pool
    await load_gallery_barber(pool(), GALLERY_BARBER_PATH)
    scheduler.add_jobstore('redis', jobs_key='reserv.jobs', run_times_key='reserv.run_times',
                           host=REDIS_HOST)

    scheduler.add_job(jobs.notification.notification_one_day_before_client_job, trigger='interval', hours=1)
    scheduler.start()
    await on_startup_notify(dispatcher)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
