# начальная заставка
import pygame
from vars import *
from svgparser import VectorizerPictures

class ScreenSaver2:
    def __init__(self):
        self.image = pygame.image.load(CURRENT_DIRECTORY + '/images/screensaver.png')
        dt = 5
        self.rect = (404 - dt, 666 - dt, 923 + dt, 683 + dt)

    def render(self, screen):
        screen.blit(self.image, (0, 0))
        colors = screen.get_at((0, 0))[:3]
        screen.fill(colors)
        screen.blit(self.image,
                    ((SIZE_GAME[0] - self.image.get_width()) // 2, (SIZE_GAME[1] - self.image.get_height()) // 2))

    def onClick(self, pos):
        l, t, r, b = self.rect
        x, y = pos
        return l <= x <= r and t <= y <= b


class ScreenSaver(VectorizerPictures):
    def __init__(self):
        self.base_name = CURRENT_DIRECTORY + '/vect_images/screensaver'
        super().__init__(self.base_name + '.svg')
        self.image = None
        self.rect = None
        self.offset = None
        self.__load()

    def __load(self):
        try:
            self.image = pygame.image.load(self.base_name + '.png')
            super().load()
            self.rect = self.overallRectangle('rect1')
            if self.rect is None:
                raise(f'{self.__class__.__name__}:{__name__}: ошибка загрузки {self.base_name}')

            self.offset = (SIZE_GAME[0] - self.image.get_width()) // 2, (SIZE_GAME[1] - self.image.get_height()) // 2

        except Exception as e:
            LOG.write(str(e))
            quit()

    def render(self, screen):
        screen.blit(self.image, (0, 0))
        colors = screen.get_at((0, 0))[:3]
        screen.fill(colors)
        screen.blit(self.image, self.offset)

    def onClick(self, pos):
        x, y = pos
        offset_x, offset_y = self.offset
        l, t, w, h = self.rect
        return l <= x - offset_x <= l + w and t <= y - offset_y <= t + h