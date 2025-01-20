import pygame
from vars import *


class Login3:
    DEFAULT_LEN = 10

    def __init__(self, x, y, text_height, max_len_text, color_text, color_fon):
        if max_len_text == 0:
            self.max_len_text = Login3.DEFAULT_LEN
        else:
            self.max_len_text = max_len_text
        self.offset = x, y
        self.need_input = False
        self.input_tick = 30
        self.color_text = color_text
        self.color_fon = color_fon

        self.font = pygame.font.Font(None, text_height)
        surf_text = self.font.render('V' * self.max_len_text, True, (0, 0, 0))
        self.input_rect = pygame.Rect(x, y, surf_text.get_width(), surf_text.get_height())
        self.text_edit = dispatcher.session.user

    def get_width(self):
        return self.input_rect.width

    def get_height(self):
        return self.input_rect.height

    def render(self, screen):
        pygame.draw.rect(screen, self.color_fon, self.input_rect)
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        if not self.input_rect.collidepoint(mouse[0], mouse[1]) and click[0]:
            self.need_input = False
            dispatcher.session.user = self.text_edit = self.text_edit.replace('|', '')

        if self.input_rect.collidepoint(mouse[0], mouse[1]) and click[0]:
            if not self.need_input:
                self.need_input = True
                self.text_edit = dispatcher.session.user + '|'
                self.input_tick = 30

        if self.need_input:
            for event in pygame.event.get():
                if self.need_input and event.type == pygame.KEYDOWN:
                    self.text_edit = self.text_edit.replace('|', '')
                    self.input_tick = 30

                    if event.key == pygame.K_RETURN:
                        self.need_input = False
                        dispatcher.session.user = self.text_edit = self.text_edit.replace('|', '')

                    elif event.key == pygame.K_BACKSPACE:
                        self.text_edit = self.text_edit[:-1]
                    else:
                        print(self.text_edit, len(self.text_edit), self.max_len_text)
                        if len(self.text_edit) < self.max_len_text:
                            self.text_edit += event.unicode
                            print(self.text_edit)

                    if self.need_input:
                        if len(self.text_edit):
                            if self.text_edit[-1] != '|':
                                self.text_edit += '|'
                        else:
                            self.text_edit += '|'

        if len(self.text_edit):
            self.print_text(screen)

        if self.need_input:
            self.input_tick -= 1
            if self.input_tick == 0:
                self.text_edit = self.text_edit[:-1]
            if self.input_tick == -30:

                if len(self.text_edit):
                    if self.text_edit[-1] != '|':
                        self.text_edit += '|'
                else:
                    self.text_edit += '|'

                self.input_tick = 30

    def print_text(self, screen):
        surf_text = self.font.render(self.text_edit, True, self.color_text)
        screen.blit(surf_text, self.offset)


class Login2:
    len_max = 10

    def __init__(self):
        self.input_rect = pygame.Rect(20, 400, 250, 70)
        self.text = dispatcher.session.user + '|'
        self.need_input = False
        self.input_tick = 30

    def render(self, screen):
        pygame.draw.rect(screen, pygame.Color('white'), self.input_rect)
        mouse = pygame.mouse.get_pos()
        print(mouse)
        click = pygame.mouse.get_pressed()
        if self.input_rect.collidepoint(mouse[0], mouse[1]) and click[0]:
            self.need_input = True
            print(click)

        if self.need_input:
            for event in pygame.event.get():
                if self.need_input and event.type == pygame.KEYDOWN:
                    self.text = self.text.replace('|', '')
                    self.input_tick = 30

                    if event.key == pygame.K_RETURN:
                        self.need_input = False
                        self.text = ''
                    elif event.key == pygame.K_BACKSPACE:
                        self.text = self.text[:-1]
                    else:
                        if len(self.text) < Login2.len_max:
                            self.text += event.unicode
                    self.text += '|'

        if len(self.text):
            self.print_text(screen)

        self.input_tick -= 1
        if self.input_tick == 0:
            self.text = self.text[:-1]
        if self.input_tick == -30:
            self.text += '|'
            self.input_tick = 30

    def print_text(self, screen):
        font = pygame.font.Font(None, 26)
        surf_text = font.render(self.text, True, (0, 0, 0))
        screen.blit(surf_text, (20, 400))
        pass