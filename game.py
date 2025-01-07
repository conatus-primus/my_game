# игровое поле
import pygame
from header import Header
from footer import Footer
from marginleft import MarginLeft
from marginright import MarginRight
from map import Map
from vars import *


class Game:
    def __init__(self):
        # игровой блок и смещение блока относительно всего игрового поля
        self.block = [(Map(), (WIDTH_MARGIN, HEIGHT_HEADER)),
                      (Header(), (0, 0)),
                      (Footer(), (0, HEIGHT_HEADER + HEIGHT_MAP)),
                      (MarginLeft(), (0, HEIGHT_HEADER)),
                      (MarginRight(), (WIDTH_MARGIN + WIDTH_MAP, HEIGHT_HEADER)),
                      ]

    def load(self, map_number):
        for item in self.block:
            obj, _ = item
            obj.load(map_number)

    def render(self, screen):
        screen.fill(pygame.Color('white'))

        for item in self.block:
            obj, offset = item
            # отрисовали на своей поверхности
            obj.render()
            # копируем на общую поверхность
            screen.blit(obj.surface, offset)
