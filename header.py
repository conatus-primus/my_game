# чердак игрового поля
import pygame
from vars import *
from block import Block


class Header(Block):
    def __init__(self, game):
        super().__init__(game, WIDTH_GAME, HEIGHT_HEADER)
        self.font = pygame.font.Font(None, HEIGHT_HEADER - 20)

    def render(self, ):
        pygame.draw.rect(self.surface, pygame.Color('red'), (0, 0, self.width, self.height))

        d = 10
        surf_text = self.font.render(dispatcher.session.user, True, (0, 0, 0))
        offset = d, (HEIGHT_HEADER - surf_text.get_height()) // 2
        self.surface.blit(surf_text, offset)
