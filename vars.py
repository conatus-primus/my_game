# общие переменные для всех классов
import os
import time
import pygame

from logger import logger

# размер карты
WIDTH_MAP = 900
HEIGHT_MAP = 900
# ширина колонок по бокам
WIDTH_MARGIN = 250
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

# массив яркостей, чтобы регулировать яркость фона
BRIGHTEN = [0, 40, 55, 66, 77, 88, 99, 110, 121, 135]

# цвет заливки всех полей игры
FON_COLOR = pygame.Color(198, 210, 159)

# лог на сессию
LOG = logger()

# событие таймера
TIMER_EVENT_ONE_SEC = pygame.USEREVENT + 1


# расстояние между двумя точками
def dist2(p1, p2):
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2


# найти точку в контуре, ближайшую к заданной точке
def findeClosedPoint(anglePoint, coords):
    minPoint = coords[0][0], coords[0][1], dist2(anglePoint, coords[0])
    for x, y in coords:
        d = dist2(anglePoint, (x, y))
        if d < minPoint[2]:
            minPoint = x, y, d
    return minPoint


# получить огибающий прямоугольник
# на входе список кортежей (x, y)
# на входе кортеж лево, верх, ширина, высота
def OVERALL_RECT(coords):
    if coords is None or len(coords) == 0:
        return None

    l = r = coords[0][0]
    t = b = coords[0][1]
    for x, y in coords:
        l = min(x, l)
        r = max(x, r)
        t = min(y, t)
        b = max(y, b)
    return pygame.Rect(l, t, r - l, b - t)


# построить огибающий контур для замкнутого контура прямоугольного вида
def OVERALL_CONTOUR(coords, h):
    rect = OVERALL_RECT(coords)

    ret = [findeClosedPoint(rect.topleft, coords), findeClosedPoint(rect.topright, coords),
           findeClosedPoint(rect.bottomright, coords), findeClosedPoint(rect.bottomleft, coords)]

    w = (2 * h ** 2) ** 0.5 * 0.55

    ret2 = [
        (ret[0][0] - h, ret[0][1]),
        (ret[0][0] - w, ret[0][1] - w),
        (ret[0][0], ret[0][1] - h),

        (ret[1][0], ret[1][1] - h),
        (ret[1][0] + w, ret[1][1] - w),
        (ret[1][0] + h, ret[1][1]),

        (ret[2][0] + h, ret[2][1]),
        (ret[2][0] + w, ret[2][1] + w),
        (ret[2][0], ret[2][1] + h),

        (ret[3][0], ret[3][1] + h),
        (ret[3][0] - w, ret[3][1] + w),
        (ret[3][0] - h, ret[3][1]),

        (ret[0][0] - h, ret[0][1])
    ]

    return ret2


class Dispatcher:
    def __init__(self):
        self.game = None

    def load(self):
        # запускаем общий таймер для на 1 сек постоянно
        pygame.time.set_timer(TIMER_EVENT_ONE_SEC, 500)

    def needUpdate(self, sender):
        self.game.needUpdate(sender)
        print(f'{sender.__class__.__name__}.needUpdate : sender={sender}')

    def onTimer(self):
        self.game.onTimer(time.time())


dispatcher = Dispatcher()


class AmuletHandler:
    def __init__(self):
        self.id = None
        self.fileName = None
        self.name = None
        self.prix = None
        self.life = None
