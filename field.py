# карта игрового поля
import pygame
import copy
from vars import *
from block import Block
from vectormap import VectorMap
from location import Location
from py.amulet import AmuletUser


class Field(Block):
    def __init__(self, game):
        super().__init__(game, WIDTH_MAP, HEIGHT_MAP)
        self.staticMap = None
        self.vectorMap = None
        self.location = None

    def load(self, map_number):
        # грузим варианты уровней и движения клавиш
        self.location = Location(map_number)
        self.location.load()

        # грузим векторное описание
        self.vectorMap = VectorMap(map_number)
        self.vectorMap.load()

        # обработка статики в карте (фон + дырки + направляющие)
        self.staticMap = StaticMap(map_number, self.game.session)
        self.staticMap.load()

        # установить выбранный уровень
        self.location.setLevelID(self.game.session.currentLevelID)
        # установить текущую дырку
        self.location.setHoleID(self.game.session.currentHoleID)
        # устанавливаем в векторную карту описание текущего уровня
        self.vectorMap.setCurrentLevelContent(self.location.currentLevelContent())

        # пользовательский амулет
        self.amuletUser = AmuletUser()
        # задаем все дырки
        self.amuletUser.load(self.vectorMap.holes)

        # связываем амулет с локатором - изменится локатор - изменим и амулеты
        self.amuletUser.setLocation(self.location)
        # и сразу и обновляем первый раз
        self.amuletUser.update()

    def render(self):
        pygame.draw.rect(self.surface, pygame.Color('blue'), (0, 0, self.width, self.height))
        self.staticMap.render(self.surface)
        self.vectorMap.render(self.surface)
        self.amuletUser.render(self.surface)

    # вход - нажатые клавиши pygame.key.get_pressed()
    def onPressed(self, pressed_keys):
        self.location.update(pressed_keys)
        self.amuletUser.update()

    def update(self, sender):
        self.staticMap.setBrightness(self.game.session.brightness)


class StaticMap:
    def __init__(self, map_number, session):
        # грузим фон
        self.path = CURRENT_DIRECTORY + '/maps/' + str(map_number) + '.png'
        # базовый фон
        self.image = pygame.image.load(self.path)
        # фон с яркостью
        self.brightenImage = pygame.image.load(self.path)
        # ставим яркость по умолчанию
        self.brightness = session.brightness
        self.setBrightness(self.brightness)
        self.image_test = pygame.image.load(CURRENT_DIRECTORY + '/images/nuage.png')

    def load(self):
        pass

    def setBrightness(self, brightness):
        self.brightness = brightness
        if self.brightness >= len(BRIGHTEN):
            self.brightness = 0
        brightColor = (BRIGHTEN[self.brightness], BRIGHTEN[self.brightness], BRIGHTEN[self.brightness])
        self.brightenImage = pygame.image.load(self.path)
        self.brightenImage.fill(brightColor, special_flags=pygame.BLEND_RGB_ADD)

    def render(self, surface):
        # рисуем фон
        surface.blit(self.brightenImage, (0, 0))
        surface.blit(self.image_test, (100, 350))
