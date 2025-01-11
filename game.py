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

    def read(self):
        config = configparser.ConfigParser()
        config.read(self.path)
        if 'start' in config:
            if 'map' in config['start']:
                self.map_number = int(config['start']['map'])
            if 'level' in config['start']:
                self.currentLevelID  = config['start']['level']
            if 'brightness' in config['start']:
                self.brightness = int(config['start']['brightness'])

    def write(self):
        config = configparser.ConfigParser()
        config['start'] = {}
        config['start']['map'] = str(self.map_number)
        config['start']['level'] = self.currentLevelID
        config['start']['brightness'] = str(self.brightness)
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

    # вход - нажатые клавиши pygame.key.get_pressed()
    def onPressed(self, pressed_keys):
        self.field.onPressed(pressed_keys)

    # sender - кто инициировал обновление
    def queryUpdate(self, sender):
        for item in self.block:
            obj, offset = item
            obj.update(sender)

    def onClick(self, pos):
        x, y = pos
        for item in self.block:
            obj, offset = item
            blockPos = x - offset[0], y - offset[1]
            obj.onClick(blockPos)
