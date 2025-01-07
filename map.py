# карта игрового поля
import pygame
from vars import *
from block import Block


class Map(Block):
    def __init__(self):
        super().__init__(WIDTH_MAP, HEIGHT_MAP)
        self.staticMap = StaticMap()

    def render(self):
        pygame.draw.rect(self.surface, pygame.Color('blue'), (0, 0, self.width, self.height))
        self.staticMap.render(self.surface)

    def load(self, map_number):
        super().load(map_number)
        self.staticMap.load(None, map_number)


class StaticMap:
    def __init__(self):
        pass

    def load(self, mapObject, map_number):
        self.image = pygame.image.load(CURRENT_DIRECTORY + '/maps/' + str(map_number) + '.png')
        self.mapObject = mapObject

    def render(self, surface):
        surface.blit(self.image, (0, 0))
