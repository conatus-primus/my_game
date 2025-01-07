# общие переменные для всех классов
import os
from logger import logger


# размер карты
WIDTH_MAP = 900
HEIGHT_MAP = 900
# ширина колонок по бокам
WIDTH_MARGIN = 200
# высота чердака
HEIGHT_HEADER = 50
# высота подвала
HEIGHT_FOOTER = 50
# полные размеры игрового поля
WIDTH_GAME = WIDTH_MAP + 2 * WIDTH_MARGIN
HEIGHT_GAME = HEIGHT_MAP + HEIGHT_HEADER + HEIGHT_FOOTER
SIZE_GAME = WIDTH_GAME, HEIGHT_GAME
# каталог программы
CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))


# лог на сессию
LOG = logger()