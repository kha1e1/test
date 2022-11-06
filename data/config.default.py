
BOT_TOKEN = "5505855519:AAG70"
WEBHOOK_HOST = 'https://s'
WEBAPP_PORT = 5004
IP = "localhost"
timer_for_feedback = 3600
ADMINS = ['']

SYSTEM = 'LINUX'  # 'WINDOWS' для форматирования путей
MAX_RESERVATION = 5

PATH_URI_DB = "mysql+asyncmy://user:pass@localhost/reserv_bot?charset=utf8mb4"
GALLERY_BARBER_PATH = [
    f".//Photogallerybot//{n}.jpeg"
    for n in range(1, 7)
]