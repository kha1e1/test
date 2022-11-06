import logging

from aiogram import Bot


async def delete_message(
        bot: Bot,
        message_id: int,
        chat_id: int
):

    try:
        await bot.delete_message(
            chat_id=chat_id,
            message_id=message_id
        )
    except Exception as e:
        logging.info(e)