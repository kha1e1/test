import logging
import typing

from aiogram import Bot


async def send_message(bot: Bot, **params) -> typing.Optional[bool]:

    try:
        await bot.send_message(
            **params
        )
        return True
    except Exception as e:
        logging.info(e)
