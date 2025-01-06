# общие переменные для всех классов
import os
from logger import logger


# размер игрового поля
size_field = 900, 900
# ширина колонок по бокам
width_column = 200
# высота чердака
height_loft = 100
# высота подвала
height_footer = 20
# полные размеры игры
SIZE_GAME = size_field[0] + 2 * width_column, size_field[1] + height_loft + height_footer

# каталог программы
CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

# лог на сессию
LOG = logger()