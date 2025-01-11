# правый блоки игрового поля
import pygame
from vars import *
from block import Block


class MarginRight(Block):
    def __init__(self, game):
        super().__init__(game, WIDTH_MARGIN, HEIGHT_MAP)
        self.brightPanel = BrightPanel(self, WIDTH_MARGIN)
        self.brightOffset = (self.brightPanel.w, self.brightPanel.w)

    def render(self):
        pygame.draw.rect(self.surface, pygame.Color('gray'), (0, 0, self.width, self.height))
        self.brightPanel.render()
        self.surface.blit(self.brightPanel.surface, self.brightOffset)


        dX = 20
        image_sound = pygame.image.load(CURRENT_DIRECTORY + '/images/system/sound.png')
        self.surface.blit(image_sound, (dX, 60))
        image_chanson = pygame.image.load(CURRENT_DIRECTORY + '/images/system/chanson.png')
        self.surface.blit(image_chanson, (dX + image_sound.get_width() + dX, 60))



    # клик мыши
    def onClick(self, pos):
        if not super().isInBlock(pos):
            return
        x, y = pos
        self.brightPanel.onClick((x - self.brightOffset[0], y - self.brightOffset[1]))


class BrightPanel:
    def __init__(self, block, width):
        self.block = block
        self.w = width // (len(BRIGHTEN) + 2)
        self.h = self.w
        self.surface = pygame.Surface((len(BRIGHTEN) * self.w, self.h))

    # нарисовать панель яркости с выделенным квадратом текущей яркости
    def render(self):
        baseColor = pygame.Color("blue")

        for i in range(len(BRIGHTEN)):
            imageSquare = pygame.Surface([self.w, self.h])
            imageSquare.fill(baseColor)
            brightColor = (BRIGHTEN[i], BRIGHTEN[i], BRIGHTEN[i])
            imageSquare.fill(brightColor, special_flags=pygame.BLEND_RGB_ADD)
            self.surface.blit(imageSquare, (i * self.w, 0))

        if self.block.game.session.brightness < len(BRIGHTEN):
            D = 2
            brightRect = (self.block.game.session.brightness * self.w + D, D, self.w - 2 * D, self.h - 2 * D)
            pygame.draw.rect(self.surface, pygame.Color('white'), brightRect, 1)

    # клик мыши
    def onClick(self, pos):
        x, y = pos
        if 0 <= x < len(BRIGHTEN) * self.w and 0 <= y < self.h:
            # поменяли атрибут в сессии
            self.block.game.session.brightness = x // self.w
            #  сообщаем всем что было изменение
            self.block.queryUpdate(self.block)
