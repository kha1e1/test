import asyncio
from dataclasses import dataclass

from aiogram import Bot


class MessageCollection:
    def __init__(self,
                 chat_id: int,
                 bot: Bot):
        self.message_ids = []
        self.bot = bot
        self.chat_id = chat_id
        self.timeout = 0.5

    async def delete(self):
        if self.message_ids is None:
            return

        for message_id in self.message_ids:
            await self.bot.delete_message(chat_id=self.chat_id, message_id=message_id)
            await asyncio.sleep(self.timeout)

    def pop(self, message_id: int):
        _index = self.message_ids.index(message_id)
        self.message_ids.pop(_index)




