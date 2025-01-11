# чердак игрового поля
import pygame
from vars import *
from block import Block


class Header(Block):
    def __init__(self, game):
        super().__init__(game, WIDTH_GAME, HEIGHT_HEADER)

    def render(self):
        pygame.draw.rect(self.surface, pygame.Color('red'), (0, 0, self.width, self.height))
