# игровое поле
import pygame
from header import Header
from footer import Footer
from marginleft import MarginLeft
from marginright import MarginRight
from field import Field
from vars import *
from py.shared import *


class Game:
    def __init__(self):
        self.field = None
        # игровой блок и смещение блока относительно всего игрового поля
        self.block = None

    def load(self):
        self.field = Field(self)
        # игровой блок и смещение блока относительно всего игрового поля
        self.block = [(self.field, (WIDTH_MARGIN, HEIGHT_HEADER)),
                      (Header(self), (0, 0)),
                      (Footer(self), (0, HEIGHT_HEADER + HEIGHT_MAP)),
                      (MarginLeft(self), (0, HEIGHT_HEADER)),
                      (MarginRight(self), (WIDTH_MARGIN + WIDTH_MAP, HEIGHT_HEADER)),
                      ]

        for item in self.block:
            obj, _ = item
            obj.load(dispatcher.session.map_number)

        # self.map.setLevelData(['path1', 'path11', 'path3', 'path32'])

        # фоновая музыка
        pygame.mixer.music.play(-1)
        if not dispatcher.session.chansonActive:
            pygame.mixer.music.pause()

        # громкость
        pygame.mixer.music.set_volume(dispatcher.session.volumeLevel)

    def render(self, screen):
        if self.block is None:
            return

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
        if self.block is None:
            return

        # переключаем звук и музыку
        if dispatcher.session.chansonActive:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()
        # print(f'volume={pygame.mixer.music.get_volume()}')

        for item in self.block:
            obj, offset = item
            obj.update(sender)

    # вход - нажатые клавиши pygame.key.get_pressed()
    def onPressedKey(self, pressed_keys):
        if self.block is None:
            return

        for item in self.block:
            obj, offset = item
            obj.onPressedKey(pressed_keys)

    def onClick(self, pos):
        if self.block is None:
            return

        x, y = pos
        for item in self.block:
            obj, offset = item
            blockPos = x - offset[0], y - offset[1]
            obj.onClick(blockPos)

    def onTimer(self, currentTime):
        if self.block is None:
            return

        for item in self.block:
            obj, offset = item
            obj.onTimer(currentTime)

    def onClickExtend(self, event):
        if self.block is None:
            return

        e = event
        x, y = e.pos

        for item in self.block:
            obj, offset = item
            e.pos = x - offset[0], y - offset[1]
            obj.onClickExtend(e)
