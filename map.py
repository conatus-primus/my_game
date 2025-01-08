# карта игрового поля
import pygame
from vars import *
from block import Block
from mapparser import RawMapObject

class Map(Block):
    def __init__(self):
        super().__init__(WIDTH_MAP, HEIGHT_MAP)
        self.staticMap = None
        self.rawMapObject = None

    def render(self):
        pygame.draw.rect(self.surface, pygame.Color('blue'), (0, 0, self.width, self.height))
        self.staticMap.render(self.surface)

    def load(self, map_number):
        super().load(map_number)

        # грузим векторное описание
        self.rawMapObject = RawMapObject(map_number)
        self.rawMapObject.load()

        # обработка статики в карте
        self.staticMap = StaticMap()
        self.staticMap.load(self.rawMapObject)


class StaticMap:
    def __init__(self):
        pass

    def load(self, mapObject, ):
        # грузим фон
        self.image = pygame.image.load(CURRENT_DIRECTORY + '/maps/' + str(mapObject.map_number) + '.png')
        # векторное описание карты
        self.mapObject = mapObject

    def render(self, surface):
        # рисуем фон
        surface.blit(self.image, (0, 0))
        # рисуем дырки
        color = pygame.Color('red')

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
            for n_hole, hole in enumerate(self.mapObject.holes):
                # круги в точках перегиба дырки чтобы сгладить широкую линию
                for point in hole.coords_hole:
                    pygame.draw.circle(surface, color, point, h // 2, h // 2)
                # дырка
                pygame.draw.lines(surface, color, True, hole.coords_hole, h)
                # направляющие дырки
                for n_line, line in enumerate(hole.coord_lines):
                    # закругление внешнего конца для красоты
                    pygame.draw.circle(surface, color, line[0], h // 2, h // 2)
                    # сама направляющая
                    pygame.draw.lines(surface, color, False, line, h)

