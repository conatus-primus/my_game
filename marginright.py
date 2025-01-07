# правый блоки игрового поля
import pygame
from vars import *
from block import Block


class MarginRight(Block):
    def __init__(self):
        super().__init__(WIDTH_MARGIN, HEIGHT_MAP)

    def render(self):
        pygame.draw.rect(self.surface, pygame.Color('gray'), (0, 0, self.width, self.height))