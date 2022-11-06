import os

from environs import Env

env = Env()
env.read_env('.env')
BOT_TOKEN = env.str('BOT_TOKEN')
WEBHOOK_IP = env.str('WEBHOOK_IP')

# webhook settings
WEBHOOK_HOST = f"https://localhost"
WEBHOOK_PORT = 8443
WEBHOOK_PATH = f"/bot/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}:{WEBHOOK_PORT}{WEBHOOK_PATH}"

# webserver settings
WEBAPP_HOST = '0.0.0.0'  # or ip
WEBAPP_PORT = os.getenv("WEBAPP_PORT")

WEBHOOK_SSL_CERT = "webhook_cert.pem"
WEBHOOK_SSL_PRIV = "webhook_pkey.pem"

MYSQL_USER = env.str("MYSQL_USER")
MYSQL_PASSWORD = env.str("MYSQL_PASSWORD")
MYSQL_DATABASE = env.str("MYSQL_DATABASE")
MYSQL_HOST = env.str("MYSQL_HOST")

REDIS_HOST = env.str('REDIS_HOST')

ADMINS = [483200140, 1691626230, 564023521]

SYSTEM = 'LINUX'  # 'WINDOWS' для форматирования путей
MAX_RESERVATION = 5

PATH_URI_DB = "mysql+asyncmy://{user}:{pwd}@{host}/{db_name}?charset=utf8mb4".format(
    user=MYSQL_USER,
    pwd=MYSQL_PASSWORD,
    host=MYSQL_HOST,
    db_name=MYSQL_DATABASE
)
print(PATH_URI_DB)
GALLERY_BARBER_PATH = [
    f".//Photogallerybot//{n}.jpeg"
    for n in range(1, 7)
]
