from aiogram import types
from aiogram.dispatcher.handler import ctx_data, CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

import handlers
from model.database.contact_barber import ContactBarber


class IsRegister(BaseMiddleware):

    def __init__(self):
        super().__init__()

    async def on_process_message(self, obj: Message, data):
        session: AsyncSession = data.get('session')

        user = await ContactBarber.get_by_user_id(session, obj.from_user.id)
        content_type = obj.content_type
        if content_type in types.ContentType.CONTACT:
            return

        if user is None:
            await handlers.start.h_start.bot_start(obj, **data)
            raise CancelHandler()


