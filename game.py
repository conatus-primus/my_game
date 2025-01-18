# игровое поле
import pygame
from header import Header
from footer import Footer
from marginleft import MarginLeft
from marginright import MarginRight
from field import Field
import configparser
from vars import *


class Session:
    def __init__(self):
        self.brightness = 0
        self.map_number = 1
        self.currentHoleID = 'path1'
        self.currentLevelID = 'level1_var1'
        self.path = CURRENT_DIRECTORY + '/data/system.ini'
        self.soundsActive = False
        self.chansonActive = False
        self.volumeLevel = 0.1
        self.money = 80
        self.user = ''

    def read(self):
        config = configparser.ConfigParser()
        config.read(self.path)
        if 'start' in config:
            if 'map' in config['start']:
                self.map_number = int(config['start']['map'])
            if 'level' in config['start']:
                self.currentLevelID = config['start']['level']
            if 'brightness' in config['start']:
                self.brightness = int(config['start']['brightness'])
                if self.brightness >= len(BRIGHTEN):
                    self.brightness = len(BRIGHTEN) - 1
            if 'soundsActive' in config['start']:
                self.soundsActive = True if config['start']['soundsActive'] == '1' else False
            if 'chansonActive' in config['start']:
                self.chansonActive = True if config['start']['chansonActive'] == '1' else False
            if 'volumeLevel' in config['start']:
                self.volumeLevel = float(config['start']['volumeLevel'])
            if 'money' in config['start']:
                self.money = int(config['start']['money'])
            if 'user' in config['start']:
                self.user = config['start']['user']

    def write(self):
        config = configparser.ConfigParser()
        config['start'] = {}
        config['start']['map'] = str(self.map_number)
        config['start']['level'] = self.currentLevelID
        config['start']['brightness'] = str(self.brightness)
        config['start']['soundsActive'] = '1' if self.soundsActive == True else '0'
        config['start']['chansonActive'] = '1' if self.chansonActive == True else '0'
        config['start']['volumeLevel'] = str(self.volumeLevel)
        config['start']['money'] = str(self.money)
        config['start']['user'] = str(self.user)
        with open(self.path, 'w') as configfile:
            config.write(configfile)


class Game:
    def __init__(self):
        self.session = Session()
        self.field = Field(self)
        # игровой блок и смещение блока относительно всего игрового поля
        self.block = [(self.field, (WIDTH_MARGIN, HEIGHT_HEADER)),
                      (Header(self), (0, 0)),
                      (Footer(self), (0, HEIGHT_HEADER + HEIGHT_MAP)),
                      (MarginLeft(self), (0, HEIGHT_HEADER)),
                      (MarginRight(self), (WIDTH_MARGIN + WIDTH_MAP, HEIGHT_HEADER)),
                      ]

    def load(self, session):
        self.session = session
        for item in self.block:
            obj, _ = item
            obj.load(session.map_number)

        # self.map.setLevelData(['path1', 'path11', 'path3', 'path32'])

        # фоновая музыка
        pygame.mixer.music.play(-1)
        if not self.session.chansonActive:
            pygame.mixer.music.pause()

        # громкость
        pygame.mixer.music.set_volume(self.session.volumeLevel)

    def render(self, screen):
        screen.fill(pygame.Color('white'))

        for item in self.block:
            obj, offset = item
            # отрисовали на своей поверхности
            obj.render()
            # копируем на общую поверхность
            screen.blit(obj.surface, offset)

    def isSession(self):
        return True

    # sender - кто инициировал обновление
    def needUpdate(self, sender):
        # переключаем звук и музыку
        if self.session.chansonActive:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()
        # print(f'volume={pygame.mixer.music.get_volume()}')

        for item in self.block:
            obj, offset = item
            obj.update(sender)

    # вход - нажатые клавиши pygame.key.get_pressed()
    def onPressedKey(self, pressed_keys):
        for item in self.block:
            obj, offset = item
            obj.onPressedKey(pressed_keys)

    def onClick(self, pos):
        x, y = pos
        for item in self.block:
            obj, offset = item
            blockPos = x - offset[0], y - offset[1]
            obj.onClick(blockPos)

    def onTimer(self, currentTime):
        for item in self.block:
            obj, offset = item
            obj.onTimer(currentTime)

    def onClickExtend(self, event):
        e = event
        x, y = e.pos

        for item in self.block:
            obj, offset = item
            e.pos = x - offset[0], y - offset[1]
            obj.onClickExtend(e)
