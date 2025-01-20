import pygame
from vars import *


class EditText:
    DEFAULT_LEN = 12

    def __init__(self, x, y,  # верх лево
                 text_height: int,  # размер шрифта в пунктах
                 max_len_text: int,  # максимальная длина текста (0 - по умолчанию)
                 color_text,  # цвет текста
                 color_fon,  # цвет фона
                 do_upper: bool,  # отображать в верхнем регистре
                 event_object
                 ):
        if max_len_text == 0:
            self.max_len_text = EditText.DEFAULT_LEN
        else:
            self.max_len_text = max_len_text
        self.need_input = False
        self.input_tick = 30
        self.color_text = color_text
        self.color_fon = color_fon
        self.do_upper = do_upper

        self.font = pygame.font.Font(None, text_height)
        self.set_pos(x, y)
        self.text_edit = ''
        self.event_object = event_object

    def set_text(self, text):
        self.prev_text_edit = self.text_edit = text
        if self.do_upper:
            self.prev_text_edit = self.prev_text_edit.upper()
            self.text_edit = self.text_edit.upper()
        if self.event_object is not None:
            self.event_object.updated(self.text_edit)

    def get_width(self):
        return self.input_rect.width

    def get_height(self):
        return self.input_rect.height

    def set_focus(self, focus):
        self.focus = focus

    def __permitted(self,letter):
        abc = '+=-;_#@$&][()! '
        return letter in list(abc) or letter.isdigit() or letter.isalpha()

    def render(self, screen):
        dispatcher.game.start = False
        pygame.draw.rect(screen, self.color_fon, self.input_rect)
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        if not self.input_rect.collidepoint(mouse[0], mouse[1]) and click[0]:
            # перестаем редактировать
            if self.need_input:
                self.need_input = False
                self.text_edit = self.text_edit.replace('|', '')
                #
                if self.event_object is not None:
                    self.event_object.updated(self.text_edit)
                    ret = self.event_object.onClick((mouse[0], mouse[1]))
                    if self.event_object.onClick((mouse[0], mouse[1])) == True:
                        dispatcher.game.start = True
                        print(dispatcher.game.start)

        if self.input_rect.collidepoint(mouse[0], mouse[1]) and click[0]:
            # начинаем редактировать
            if not self.need_input:
                self.need_input = True
                self.text_edit += '|'
                self.input_tick = 30

        if self.need_input:
            for event in pygame.event.get():
                if self.need_input and event.type == pygame.KEYDOWN:
                    self.text_edit = self.text_edit.replace('|', '')
                    self.input_tick = 30

                    if event.key == pygame.K_RETURN:
                        self.need_input = False
                        self.text_edit = self.text_edit.replace('|', '')
                        #
                        if self.event_object is not None:
                            self.event_object.updated(self.text_edit)

                    elif event.key == pygame.K_BACKSPACE:
                        self.text_edit = self.text_edit[:-1]
                        if self.event_object is not None:
                            self.event_object.updated(self.text_edit)
                    else:
                        # print(self.text_edit, len(self.text_edit), self.max_len_text)
                        if len(self.text_edit) < self.max_len_text and self.__permitted(event.unicode):
                            self.text_edit += event.unicode
                            if self.do_upper:
                                self.text_edit = self.text_edit.upper()
                            if self.event_object is not None:
                                self.event_object.updated(self.text_edit)

                    if self.need_input:
                        if len(self.text_edit):
                            if self.text_edit[-1] != '|':
                                self.text_edit += '|'
                        else:
                            self.text_edit += '|'

        if len(self.text_edit):
            self.__print_text(screen)

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

    def __print_text(self, screen):
        surf_text = self.font.render(self.text_edit, True, self.color_text)
        screen.blit(surf_text, self.offset)

    def set_pos(self, x, y):
        self.offset = x, y
        surf_text = self.font.render('W' * self.max_len_text, True, (0, 0, 0))
        self.input_rect = pygame.Rect(x, y, surf_text.get_width(), surf_text.get_height())
