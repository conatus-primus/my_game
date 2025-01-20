# общие переменные для всех классов
import os
import time
import pygame
import configparser

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
FON_COLOR_DARK = pygame.Color(159, 168, 127)

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


class AmuletHandler:
    def __init__(self):
        self.id = None
        self.fileName = None
        self.name = None
        self.prix = None
        self.life = None


class Sounds:
    def __init__(self):
        self.sGlass = pygame.mixer.Sound('sounds/glass1.ogg')
        self.sVgux = pygame.mixer.Sound('sounds/bruit_silence.ogg')
        pygame.mixer.music.load("sounds/fon.mp3")


class Session:
    def __init__(self):
        self.path = 'data/system.ini'

        self.brightness = 0
        # TODO задать кривой номер и нормально показать ошибку
        self.map_number = 101
        self.currentHoleID = 'path1'
        self.currentLevelID = 'level1_var1'
        self.soundsActive = False
        self.chansonActive = False
        self.volumeLevel = 0.1
        self.money = 80
        self.user = ''

    def read(self):
        section = 'start'

        # считываем текущего пользователя
        config = configparser.ConfigParser()
        config.read(self.path, 'utf-8')
        if section in config:
            if 'user' in config[section]:
                self.user = config[section]['user'].strip()

        if self.user == '':
            self.user = 'GUEST'

        # пользовательские настройки
        config.read('users/' + self.user + '.ini', 'utf-8')

        if section in config:
            if 'map' in config[section]:
                self.map_number = int(config[section]['map'])
            if 'level' in config[section]:
                self.currentLevelID = config[section]['level']
            if 'brightness' in config[section]:
                self.brightness = int(config[section]['brightness'])
                if self.brightness >= len(BRIGHTEN):
                    self.brightness = len(BRIGHTEN) - 1
            if 'soundsActive' in config[section]:
                self.soundsActive = True if config[section]['soundsActive'] == '1' else False
            if 'chansonActive' in config[section]:
                self.chansonActive = True if config[section]['chansonActive'] == '1' else False
            if 'volumeLevel' in config[section]:
                self.volumeLevel = float(config[section]['volumeLevel'])
            if 'money' in config[section]:
                self.money = int(config[section]['money'])

    def write(self):
        section = 'start'

        # записываем имя текущего пользователя
        with open(self.path, 'w', encoding='utf-8') as f:
            config = configparser.ConfigParser()
            if section not in config:
                config[section] = {}
            config[section]['user'] = '' if self.user.lower() in ['гость'] else self.user
            config.write(f)

        # формируем файл пользовательских настроек
        config = configparser.ConfigParser()
        config[section] = {}
        config[section]['map'] = str(self.map_number)
        config[section]['level'] = self.currentLevelID
        config[section]['brightness'] = str(self.brightness)
        config[section]['soundsActive'] = '1' if self.soundsActive == True else '0'
        config[section]['chansonActive'] = '1' if self.chansonActive == True else '0'
        config[section]['volumeLevel'] = str(self.volumeLevel)
        config[section]['money'] = str(self.money)

        with open('users/' + self.user + '.ini', 'w', encoding='utf-8') as f:
            config.write(f)


class Dispatcher:
    def __init__(self):
        self.game = None
        self.session = Session()

    def load(self, game):
        self.game = game
        self.session.read()
        # запускаем общий таймер для на 1 сек постоянно
        pygame.time.set_timer(TIMER_EVENT_ONE_SEC, 500)

    def needUpdate(self, sender):
        self.game.needUpdate(sender)
        # print(f'{sender.__class__.__name__}.needUpdate : sender={sender}')

    def onTimer(self):
        self.game.onTimer(time.time())


dispatcher = Dispatcher()
