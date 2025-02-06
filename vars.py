# общие переменные для всех классов
import os
import time
import pygame
import configparser
import enum

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
BRIGHTEN = [0, 40, 55, 66, 77, 88, 99, 110, 115, 130, 150, 170]

# цвет заливки всех полей игры
FON_COLOR = pygame.Color(198, 210, 159)
FON_COLOR_MID = pygame.Color(159, 168, 127)
FON_COLOR_DARK = pygame.Color(183, 194, 147)

# лог на сессию
LOG = logger()

# событие таймера
TIMER_EVENT_ONE_SEC = pygame.USEREVENT + 1
TIMER_EVENT_GAME = pygame.USEREVENT + 2

# время показа пассивного амулета в одной дырке
SHOW_TIME_IN_HOLE_SEC = 2

# максимальное количество уровней
MAX_LEVEL_COUNT = 6


# расстояние между двумя точками
def dist2(p1, p2):
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2


# найти точку в контуре, ближайшую к заданной точке
def find_closed_point(angle_point, coords):
    min_point = coords[0][0], coords[0][1], dist2(angle_point, coords[0])
    for x, y in coords:
        d = dist2(angle_point, (x, y))
        if d < min_point[2]:
            min_point = x, y, d
    return min_point


# получить огибающий прямоугольник
# на входе список кортежей (x, y)
# на входе кортеж лево, верх, ширина, высота
def OVERALL_RECT(coords):
    if coords is None or len(coords) == 0:
        return None

    left = r = coords[0][0]
    t = b = coords[0][1]
    for x, y in coords:
        left = min(x, left)
        r = max(x, r)
        t = min(y, t)
        b = max(y, b)
    return pygame.Rect(left, t, r - left, b - t)


# построить огибающий контур для замкнутого контура прямоугольного вида
def OVERALL_CONTOUR(coords, h):
    rect = OVERALL_RECT(coords)

    ret = [find_closed_point(rect.topleft, coords), find_closed_point(rect.topright, coords),
           find_closed_point(rect.bottomright, coords), find_closed_point(rect.bottomleft, coords)]

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
        # описание карты MapDecr
        self.selected_map = None
        # список дырок выбранного уровня
        self.level_content = []

        self.logica = None

    def read(self):
        section = 'start'

        # считываем текущего пользователя
        config = configparser.ConfigParser()
        config.read(self.path, 'utf-8')
        if section in config:
            if 'user' in config[section]:
                self.user = config[section]['user'].strip().lower()
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

        if self.user == '':
            self.user = 'ГОСТЬ'
        self.user = self.user.upper()

    def write(self):
        section = 'start'

        # записываем имя текущего пользователя
        with open(self.path, 'w', encoding='utf-8') as f:
            config = configparser.ConfigParser()
            if section not in config:
                config[section] = {}
            config[section]['user'] = '' if self.user.lower() in ['гость'] else self.user
            config[section]['brightness'] = str(self.brightness)
            config[section]['soundsActive'] = '1' if self.soundsActive is True else '0'
            config[section]['chansonActive'] = '1' if self.chansonActive is True else '0'
            config[section]['volumeLevel'] = str(self.volumeLevel)
            config.write(f)


class Dispatcher:
    def __init__(self):
        self.game = None
        self.session = Session()
        self.user = None
        # размер текущего тика
        self.tick = 0
        self.flag_finish = False
        self.finish_screen = None

    def on_stop(self):
        if self.game is not None:
            self.game.on_stop()

        self.session.write()

        if self.user is not None:
            self.user.save()

    def load(self, game):
        self.game = game
        self.session.read()
        # запускаем общий таймер для на 1 сек постоянно
        pygame.time.set_timer(TIMER_EVENT_ONE_SEC, 500)

    def needUpdate(self, sender):
        self.game.needUpdate(sender)
        # print(f'{sender.__class__.__name__}.needUpdate : sender={sender}')

    def on_timer(self):
        tt = time.time()
        if self.game is not None:
            self.game.on_timer(tt)
        if self.finish_screen is not None:
            self.finish_screen.on_timer(tt)

    @staticmethod
    def load_image(fullname):
        if not os.path.isfile(fullname):
            LOG.write(f'Файл с изображением {fullname} не найден')
            return None
        image = pygame.image.load(fullname)
        LOG.write(f'Загружен файл с изображением {fullname}')
        return image


dispatcher = Dispatcher()


class ButtonState(enum.Enum):
    # начать игру
    PLAY_ID = 3000
    # пауза
    PAUSE_ID = 3001
    # начать игру заново
    REPLAY_ID = 3002
    # продолжить после паузы
    CONTINUE_ID = 3003
    # вернуться к выбору дома
    HOUSE_ID = 3004


class GameState(enum.Enum):
    # игры нет
    GAME_NO = 4005
    # начать игру
    GAME_WAIT = 4000
    # идет игра
    GAME_PLAY = 4001
    # пауза
    GAME_PAUSE = 4002
    # раунд игры закончился успешно
    GAME_SUCCESS = 4003
    # раунд игры закончился неудачно
    GAME_FAIL = 4004

class Machine:
    # 2 параметра картинка, 3 параметр смещение по горизонтали от левого края
    buttons = {ButtonState.PLAY_ID: ('play.png', None, None),
               ButtonState.PAUSE_ID: ('pause.png', None, None),
               ButtonState.REPLAY_ID: ('replay.png', None, None),
               ButtonState.CONTINUE_ID: ('continue.png', None, None),
               ButtonState.HOUSE_ID: ('house.png', None, None)
               }

    states = {GameState.GAME_WAIT: [ButtonState.PLAY_ID, ButtonState.HOUSE_ID],
              GameState.GAME_PLAY: [ButtonState.PAUSE_ID],
              GameState.GAME_PAUSE: [ButtonState.CONTINUE_ID, ButtonState.REPLAY_ID, ButtonState.HOUSE_ID],
              GameState.GAME_SUCCESS: [ButtonState.PLAY_ID, ButtonState.HOUSE_ID],
              GameState.GAME_FAIL: [ButtonState.REPLAY_ID, ButtonState.HOUSE_ID],
              GameState.GAME_NO: []
              }
