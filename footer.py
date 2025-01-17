# подвал игрового поля
import pygame
from vars import *
from block import Block


class Footer(Block):
    def __init__(self, game):
        super().__init__(game, WIDTH_GAME, HEIGHT_FOOTER)

    def render(self):
        pygame.draw.rect(self.surface, FON_COLOR_DARK, (0, 0, self.width, self.height))
