# карта игрового поля
import pygame
from vars import *
from block import Block
from mapparser import LevelMap


class Map(Block):
    def __init__(self):
        super().__init__(WIDTH_MAP, HEIGHT_MAP)
        self.staticMap = None
        self.rawMapObject = None
        # дырки и направляющие, которые отображаются (зависит от уровня)
        self.visible_holes = None

    def render(self):
        pygame.draw.rect(self.surface, pygame.Color('blue'), (0, 0, self.width, self.height))
        self.staticMap.render(self.surface)

    def load(self, map_number):
        # грузим векторное описание
        self.levelMap = LevelMap(map_number)
        self.levelMap.load()

        # обработка статики в карте
        self.staticMap = StaticMap(self.levelMap)
        self.staticMap.load()

    # настройки карты в зависимости от уровня игры
    def setLevelData(self, visible_holes=None):
        self.levelMap.setLevelData(visible_holes)


class StaticMap:
    def __init__(self, mapObject):
        self.mapObject = mapObject
        self.visible_holes = None

    def load(self):
        # грузим фон
        self.image = pygame.image.load(CURRENT_DIRECTORY + '/maps/' + str(self.mapObject.map_number) + '.png')

    def render(self, surface):
        # рисуем фон
        surface.blit(self.image, (0, 0))
        # рисуем дырки

        pens = [
            (pygame.Color(40, 40, 40), 11),
            (pygame.Color(80, 80, 80), 9),
            (pygame.Color(120, 120, 120), 7),
            (pygame.Color(160, 160, 160), 5),
            (pygame.Color(200, 200, 200), 3),
            (pygame.Color(240, 240, 240), 1)
        ]

        for pen in pens:
            color, h = pen
            for n_hole, one_hole in enumerate(self.mapObject.holes):
                # круги в точках перегиба дырки, чтобы сгладить широкую линию
                for point in one_hole.coords_hole:
                    pygame.draw.circle(surface, color, point, h // 2, h // 2)
                # дырка
                pygame.draw.lines(surface, color, True, one_hole.coords_hole, h)
                # направляющие дырки
                for n_line, line in enumerate(one_hole.lines):
                    id, coords = line
                    # закругление внешнего конца для красоты
                    pygame.draw.circle(surface, color, coords[0], h // 2, h // 2)
                    # сама направляющая
                    pygame.draw.lines(surface, color, False, coords, h)
