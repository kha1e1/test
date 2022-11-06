import typing

from aiogram.types import CallbackQuery, Message, InputMedia


async def edit_media(
        q: typing.Union[Message, CallbackQuery],
        **params
):


    if isinstance(q, Message):
        await q.answer_photo(
            **params
        )

    elif isinstance(q, CallbackQuery):
        await q.message.edit_media(
            media=InputMedia(
                media=params.get("photo"),
                caption=params.get("caption")
            ),
            reply_markup=params.get("reply_markup")

        )