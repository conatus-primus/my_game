# карта игрового поля
import pygame
from vars import *
from block import Block
from vectormap import VectorMap
from location import Location
from py.amulet import AmuletUser


class Map(Block):
    def __init__(self):
        super().__init__(WIDTH_MAP, HEIGHT_MAP)
        self.staticMap = None
        self.vectorMap = None
        self.location = None
        self.currentHoleID = 'path1'
        self.currentLevelID = '1_1'

    def load(self, map_number):
        # грузим варианты уровней и движения клавиш
        self.location = Location(map_number)
        self.location.load()

        # грузим векторное описание
        self.vectorMap = VectorMap(map_number)
        self.vectorMap.load()

        # обработка статики в карте (фон + дырки + направляющие)
        self.staticMap = StaticMap(map_number)
        self.staticMap.load()

        # установить выбранный уровень
        self.location.setLevelID(self.currentLevelID)
        # установить текущую дырку
        self.location.setHoleID(self.currentHoleID)
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


class StaticMap:
    def __init__(self, map_number):
        # грузим фон
        self.image = pygame.image.load(CURRENT_DIRECTORY + '/maps/' + str(map_number) + '.png')
        self.image_test = pygame.image.load(CURRENT_DIRECTORY + '/images/nuage.png')

    def load(self):
        pass

    def render(self, surface):
        # рисуем фон
        surface.blit(self.image, (0, 0))
        surface.blit(self.image_test, (100, 350))
        # рисуем дырки
