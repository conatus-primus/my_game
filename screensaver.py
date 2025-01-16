# начальная заставка
import pygame
from vars import *
from svgparser import VectorizerPictures


class ScreenSaver(VectorizerPictures):
    def __init__(self):
        self.base_name = CURRENT_DIRECTORY + '/vect_images/screensaver'
        super().__init__(self.base_name + '.svg')
        self.image = None
        self.rectText = None
        self.offset = None
        self.__load()

        self.image2 = pygame.image.load(self.base_name + '2.png')
        self.image3 = pygame.image.load(self.base_name + '3.png')
        self.tickCount = None
        self.angle = 0
        self.sign = 1

    def __load(self):
        try:
            self.image3 = pygame.image.load(self.base_name + '.png')
            super().load()
            self.rectText = self.overallRectangle('rect1')
            if self.rectText is None:
                raise (f'{self.__class__.__name__}:{__name__}: ошибка загрузки {self.base_name}')

            self.offset = (SIZE_GAME[0] - self.image3.get_width()) // 2, (
                    SIZE_GAME[1] - self.image3.get_height()) // 2

        except Exception as e:
            LOG.write(str(e))
            quit()

    def render(self, screen, tick):

        screen.fill(pygame.Color(0, 148, 255))
        screen.blit(self.image3, self.offset)

        if self.tickCount == None:
            self.tickCount = 0
            self.angle = 0
            self.sign = 1
        else:
            self.tickCount += 1

            if self.tickCount % 10 == 0:
                self.angle += 0.4 * self.sign

                ANGLE = 10
                if self.angle >= ANGLE:
                    self.sign = -self.sign
                elif self.angle < - ANGLE:
                    self.sign = -self.sign

        surf = pygame.transform.rotate(self.image2, self.angle)
        rotateRect = surf.get_rect()

        _, _, _, h = self.rectText
        __offset = (SIZE_GAME[0] - rotateRect.width) // 2, (SIZE_GAME[1] - rotateRect.height) // 2 - 3 * h
        screen.blit(surf, __offset)

    def onClick(self, pos):
        x, y = pos
        offset_x, offset_y = self.offset
        l, t, w, h = self.rectText
        return l <= x - offset_x <= l + w and t <= y - offset_y <= t + h
