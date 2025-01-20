# начальная заставка
import pygame
from vars import *
from svgparser import VectorizerPictures
from py.edit import EditText


class Invite(VectorizerPictures):
    def __init__(self):
        super().__init__('vect_images/invite2.svg')
        self.rectText = None
        self.offset = None
        self.imageTitle = None
        self.imageClick = None
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


class EventObject:
    def updated(self, new_text):
        pass


class Login(EditText, EventObject):
    def __init__(self, rect_overall, start_window):
        self.start_window = start_window
        # расчет высоты шрифта и прочего
        super().__init__(0, 0, 50, 10, pygame.Color(0, 0, 0), FON_COLOR_DARK, True, self)
        # сюда надо вписать контрол (только по вертикали)
        x, y, w, h = rect_overall
        # считаем смещение
        y += (h - super().get_height()) // 2
        super().set_pos(x, y)
        # это для рамки
        d = 5
        self.ramka = pygame.Rect(x - d, y - d, super().get_width() + 2 * d, super().get_height() + 2 * d)
        self.image_warning = pygame.image.load('images/system/warning_login.png')
        self.show_warning = False

    def render(self, screen):
        pygame.draw.rect(screen, (0, 0, 0), self.ramka, 1)
        if self.show_warning == True:
            d = 10
            screen.blit(self.image_warning, (self.ramka.x, self.ramka.bottom + d))
        super().render(screen)

    def updated(self, new_text):
        new_text = new_text.strip()
        self.show_warning = new_text.lower() in ['гость', 'guest', '']
        # выводим предупреждение
        self.start_window.updated(new_text)

    def onClick(self, pos):
        return self.start_window.onClick(pos)


class Start(VectorizerPictures):
    def __init__(self):
        super().__init__('vect_images/login_start.svg')
        self.image_synopsis = pygame.image.load('images/system/synopsis.png')
        self.image_window2 = pygame.image.load('images/system/window_clin.png')
        self.image_login = pygame.image.load('vect_images/login_start.png')
        self.login_image_pos = ((WIDTH_GAME - self.image_login.get_width()) // 2, HEIGHT_GAME - 5 * HEIGHT_FOOTER)
        self.login_control = None
        self.active_start = False

    def load(self):
        # считаем положение окошка логина и клика для начала
        super().load()

        rect_login_control = self.overallRectangle('rect1')
        self.rect_start = self.overallRectangle('rect2')

        if rect_login_control is None or self.rect_start is None:
            raise (f'{self.__class__.__name__}:{__name__}: ошибка загрузки {self.svg_file}')

        # старт
        x, y, w, h = self.rect_start
        d = 10
        self.rect_start = x + self.login_image_pos[0] - d, y + self.login_image_pos[1] - d, w + 2 * d, h + 2 * d
        # логин
        x, y, w, h = rect_login_control
        rect_login_control = x + self.login_image_pos[0], y + self.login_image_pos[1], w, h
        self.login_control = Login(rect_login_control, self)
        self.login_control.set_text(dispatcher.session.user)

    def render(self, screen, tick):
        screen.fill(FON_COLOR)
        pygame.draw.rect(screen, FON_COLOR_DARK, (0, 0, WIDTH_GAME, HEIGHT_HEADER))
        pygame.draw.rect(screen, FON_COLOR_DARK, (0, HEIGHT_GAME - HEIGHT_FOOTER, WIDTH_GAME, HEIGHT_FOOTER))

        # pygame.draw.rect(screen, FON_COLOR_DARK, self.rect_start, 2)
        # pygame.draw.rect(screen, FON_COLOR_DARK, self.rect_login_control, 2)

        d = HEIGHT_HEADER // 2
        screen.blit(self.image_synopsis, ((WIDTH_GAME - self.image_synopsis.get_width()) // 2, HEIGHT_HEADER + d))
        screen.blit(self.image_window2, (d, HEIGHT_HEADER + d))
        screen.blit(self.image_window2, (WIDTH_GAME - d - self.image_window2.get_width(),
                                         HEIGHT_GAME - HEIGHT_FOOTER - d - self.image_window2.get_height()))

        screen.blit(self.image_login, self.login_image_pos)

        if self.login_control is not None:
            self.login_control.render(screen)

    def onClick(self, pos):
        x, y = pos
        l, t, w, h = self.rect_start
        return l <= x <= l + w and t <= y <= t + h

    def updated(self, new_text):
        if new_text == '':
            new_text = 'гость'.upper()
        dispatcher.session.user = new_text
