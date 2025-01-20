# начальная заставка
import pygame
from vars import *
from svgparser import VectorizerPictures
from py.edit import EditText


class Invite(VectorizerPictures):
    def __init__(self):
        self.rectText = None
        self.offset = None
        self.imageTitle = None
        self.imageClick = None
        super().__init__('vect_images/invite2.svg')
        self.__load()
        self.tickCount = None
        self.angle = 0
        self.sign = 1

    def __load(self):
        try:
            self.imageTitle = pygame.image.load('vect_images/invite1.png')
            self.imageClick = pygame.image.load('vect_images/invite2.png')
            super().load()
            self.rectText = self.overallRectangle('rect1')
            if self.rectText is None:
                raise (f'{self.__class__.__name__}:{__name__}: ошибка загрузки {self.svg_file}')

            self.offset = (SIZE_GAME[0] - self.imageClick.get_width()) // 2, (
                    SIZE_GAME[1] - self.imageClick.get_height()) // 2

        except Exception as e:
            LOG.write(str(e))
            quit()

    def render(self, screen, tick):

        screen.fill(FON_COLOR)
        pygame.draw.rect(screen, FON_COLOR_DARK, (0, 0, WIDTH_GAME, HEIGHT_HEADER))
        pygame.draw.rect(screen, FON_COLOR_DARK, (0, HEIGHT_GAME - HEIGHT_FOOTER, WIDTH_GAME, HEIGHT_FOOTER))
        screen.blit(self.imageClick, self.offset)

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

        surf = pygame.transform.rotate(self.imageTitle, self.angle)
        rotateRect = surf.get_rect()

        _, _, _, h = self.rectText
        __offset = (SIZE_GAME[0] - rotateRect.width) // 2, (SIZE_GAME[1] - rotateRect.height) // 2 - 2 * h
        screen.blit(surf, __offset)

    def onClick(self, pos):
        x, y = pos
        offset_x, offset_y = self.offset
        l, t, w, h = self.rectText
        return l <= x - offset_x <= l + w and t <= y - offset_y <= t + h


class Login(EditText):
    def __init__(self, x, y):
        super().__init__(x, y, 50, 10, pygame.Color(0,0,0), FON_COLOR_DARK)


class Start:
    def __init__(self):
        # super().__init__('vect_images/start.svg')
        self.imageSynopsis = pygame.image.load('images/system/synopsis.png')
        self.imageWindow2 = pygame.image.load('images/system/window2.png')
        self.loginPos = None
        self.login = None

    def load(self):
        self.login = Login(150, 700)

    def render(self, screen, tick):
        screen.fill(FON_COLOR)
        pygame.draw.rect(screen, FON_COLOR_DARK, (0, 0, WIDTH_GAME, HEIGHT_HEADER))
        pygame.draw.rect(screen, FON_COLOR_DARK, (0, HEIGHT_GAME - HEIGHT_FOOTER, WIDTH_GAME, HEIGHT_FOOTER))

        D = HEIGHT_HEADER // 2
        screen.blit(self.imageSynopsis, ((WIDTH_GAME - self.imageSynopsis.get_width()) // 2, HEIGHT_HEADER + D))
        screen.blit(self.imageWindow2, (D, HEIGHT_HEADER + D))
        screen.blit(self.imageWindow2, (WIDTH_GAME - D - self.imageWindow2.get_width(),
                                        HEIGHT_GAME - HEIGHT_FOOTER - D - self.imageWindow2.get_height()))

        self.login.render(screen)

    def onClick(self, pos):
        if pos[0] > 800:
            return True
        else:
            return False
