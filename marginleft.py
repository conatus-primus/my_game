# левый блоки игрового поля
import pygame
from vars import *
from block import Block


class MarginLeft(Block):
    def __init__(self):
        super().__init__(WIDTH_MARGIN, HEIGHT_MAP)

    def render(self):
        pygame.draw.rect(self.surface, pygame.Color('coral'), (0, 0, self.width, self.height))