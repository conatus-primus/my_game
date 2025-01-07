# подвал игрового поля
import pygame
from vars import *
from block import Block


class Footer(Block):
    def __init__(self):
        super().__init__(WIDTH_GAME, HEIGHT_FOOTER)

    def render(self):
        pygame.draw.rect(self.surface, pygame.Color('green'), (0, 0, self.width, self.height))