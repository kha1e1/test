from openpyxl import load_workbook
import os
import datetime

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from model import database


async def add_user(
        session: AsyncSession,
        user_id: str, full_name: str, number: int):
    if not await database.contact_barber.ContactBarber.get_by_user_id(session, user_id):
        await database.contact_barber.ContactBarber(
            user_id=user_id,
            Full_name=full_name,
            Number=number,
            Reg_time=datetime.datetime.now()
        ).save(session)

    return True
