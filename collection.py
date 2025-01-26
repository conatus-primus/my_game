# коллекция всех карт
import pygame
from vars import *
from block import Block
from py.biblio import *


class Collection(Block):
    def __init__(self, game):
        super().__init__(game, WIDTH_MAP, HEIGHT_MAP)
        self.font = pygame.font.Font(None, HEIGHT_HEADER - 20)
        self.biblio = None
        self.user = game.user

    def render(self):
        pygame.draw.rect(self.surface, FON_COLOR_DARK, (0, 0, self.width, self.height))
        if self.biblio is not None:
            self.biblio.render(self.surface)

    def load(self, map_number):
        self.biblio = Biblio(self)
        self.biblio.load(self.user)

    def onClick(self, pos):
        if not super().isInBlock(pos):
            return False
        x, y = pos
        if self.biblio is not None:
            self.biblio.on_click(pos)

    def on_double_click(self, event):
        if not super().isInBlock(event.pos):
            return False
        if self.biblio is not None:
            self.biblio.on_double_click(event)
