import typing

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, InputFile, CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from data import workdirs
from data.strings import s_gallery
from functions.f_media import edit_media
from keyboards.default import kb_gallery
from keyboards.default.kb_work_of_masters import get_work_of_masters_btn
from keyboards.inline import ikb_gallery
from keyboards.inline.ikb_gallery import get_paginate_for_gallery, ikb_gallery_cb
from loader import dp, bot
from misc import state_gallery
from model import database


@dp.message_handler(Text(equals='📷 Галерея'), state='*')
async def gallery(message: types.Message, state: FSMContext):
    await state.reset_state()

    await message.answer(s_gallery.gallerystart, reply_markup=kb_gallery.gallery)


@dp.message_handler(Text(equals='Фото работ мастеров'))
async def process_photo_work_of_masters(message: types.Message,
                                        state: FSMContext,
                                        session: AsyncSession):
    await state.finish()
    masters: typing.List[database.master_barber.MasterBarber] = await database.master_barber.MasterBarber.all(session)

    if not masters:
        return await message.answer("Нет мастеров")
    await message.answer("Чьи работы вас интересуют?", reply_markup=get_work_of_masters_btn(masters))

    await state_gallery.StateGallery.master_works.set()


@dp.message_handler(state=state_gallery.StateGallery.master_works)
@dp.callback_query_handler(ikb_gallery_cb.filter(), state=state_gallery.StateGallery.master_works)
async def view_photo_work_of_master(q: CallbackQuery, state: FSMContext,
                                    session: AsyncSession,
                                    callback_data: dict = {}

                                    ):
    data = await state.get_data()
    master_works = data.get("master_works")

    if isinstance(q, Message):
        master_name = q.text.replace("works", "").strip()
        stmt = select(
            database.master_works_barber.MasterWorksBarber.photo_path
        ).select_from(database.master_barber.MasterBarber).join(
            database.master_works_barber.MasterWorksBarber,
            database.master_works_barber.MasterWorksBarber.master_id == database.master_barber.MasterBarber.id
        ).where(
            database.master_barber.MasterBarber.master == master_name
        )
        response = await session.execute(stmt)
        master_works = response.scalars().all()

    await state.update_data(
        master_works=master_works
    )

    page = callback_data.get("page")
    if page is None:
        page = 0

    page = int(page)
    master_work = master_works[page]

    await edit_media(
        q,
        photo=InputFile(path_or_bytesio=workdirs.WORK_DIRECTORY_PHOTO_MASTER_WORKS / master_work),
        reply_markup=get_paginate_for_gallery(master_works, page, limit=1)
    )


@dp.message_handler(Text(equals='Фото салона'))
@dp.callback_query_handler(ikb_gallery_cb.filter())
async def process_photo_salon(query: typing.Union[types.CallbackQuery, types.Message],
                              session: AsyncSession, callback_data: dict = {}):
    gallery_list: typing.List[
        database.gallery_barber.GallerybBarber] = await database.gallery_barber.GallerybBarber.all(session)
    page = callback_data.get("page")
    if page is None:
        page = 0

    page = int(page)
    photo: database.gallery_barber.GallerybBarber = gallery_list[page]

    await edit_media(query, photo=InputFile(photo.path),
                     reply_markup=get_paginate_for_gallery(gallery_list, page, limit=1))
