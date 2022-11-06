from data.config import ADMINS


async def check_admin(user_id):

    if user_id in ADMINS:
        return True
    return False
