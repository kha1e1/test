from loader import dp
from .album import AlbumMiddleware
from .db import DbMiddleware
from .is_register import IsRegister
from .throttling import ThrottlingMiddleware


if __name__ == "middlewares":
    # dp.middleware.setup(ThrottlingMiddleware())
    dp.middleware.setup(AlbumMiddleware())
    dp.middleware.setup(DbMiddleware())
    dp.middleware.setup(IsRegister())
