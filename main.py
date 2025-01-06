import pygame
import random
import configparser

import os
from svgparser import RawHoleObject
from screensaver import ScreenSaver
from vars import *


class Board:
    # создание поля
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[-1] * width for _ in range(height)]
        # значения по умолчанию
        self.left = 10
        self.top = 10
        self.cell_size = 50

    def set_color(self, cell):
        if cell is None:
            return
        row, col = cell
        self.board[row][col] = 1

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    # координаты клетки в виде кортежа по переданным координатам мыши
    # должен вернуть None если координаты мыши оказались вне поля
    def get_cell(self, mouse_pos):
        x, y = mouse_pos
        dCol = (x - self.left) // self.cell_size
        dRow = (y - self.top) // self.cell_size
        if (dCol < 0 or dRow < 0) or (dCol >= self.width) or (dRow >= self.height):
            return None
        else:
            return (dRow, dCol)

    # рисуем
    def render(self, screen):

        font = pygame.font.Font(None, self.cell_size)

        for row in range(self.height):
            for col in range(self.width):
                # пишем число
                if 0 <= self.board[row][col] <= 9:
                    text = font.render(f'{self.board[row][col]}', True, (0, 255, 0))
                    pos_text_w = self.left + (self.cell_size - text.get_width()) // 2
                    pos_text_h = self.top + (self.cell_size - text.get_height()) // 2
                    screen.blit(text, (col * self.cell_size + pos_text_w, row * self.cell_size + pos_text_h))
                # красим клетку
                elif self.board[row][col] == 10:
                    pygame.draw.rect(screen, pygame.Color('red'),
                                     (self.left + col * self.cell_size, self.top + row * self.cell_size,
                                      self.cell_size, self.cell_size), 0)

        # пустим по верху сеточку
        for row in range(self.height):
            for col in range(self.width):
                pygame.draw.rect(screen, pygame.Color('white'),
                                 (self.left + col * self.cell_size, self.top + row * self.cell_size,
                                  self.cell_size, self.cell_size), 1)


# сюда вынесены расчетные алгоритмы
class Minesweeper(Board):
    def __init__(self, params):
        width, height, mines_count = params
        super().__init__(width, height)

        mines_coords = []
        while len(mines_coords) != mines_count:
            row, col = random.randrange(height - 1), random.randrange(width - 1)
            if (row, col) in mines_coords:
                continue
            else:
                mines_coords.append((row, col))
                self.board[row][col] = 10

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        self.on_click(cell)

    # изменяет поле опираясь на полученные координаты клетки
    def on_click(self, cell):
        self.open_cell(cell)

    # открываем ячейку если закрыта
    def open_cell(self, cell):
        if cell is None:
            return
        row, col = cell
        if self.board[row][col] != -1:
            return
        mines = 0
        for r in range(row - 1, row + 1 + 1):
            for c in range(col - 1, col + 1 + 1):
                if 0 <= r < self.height and 0 <= c < self.width:
                    if self.board[r][c] == 10:
                        mines += 1
        self.board[row][col] = mines


def get_values():
    s = input().split(' ')
    if len(s) != 3:
        raise ValueError

    w = int(s[0])
    h = int(s[1])
    mines = int(s[2])
    if mines >= w * h:
        raise ValueError

    return w, h, mines


if __name__ == '__main__':

    #CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

    config = configparser.ConfigParser()
    config.read(CURRENT_DIRECTORY + '/data/system.ini')

    if 'start' in config and 'map' in config['start']:
        map_number = int(config['start']['map'])
    else:
        map_number = 1

    data = RawHoleObject(map_number)
    data.load()

    # стартовая заставка
    startScreen = ScreenSaver(pygame)

    try:
        # params = get_values()
        params = 10, 10, 10
    except ValueError:
        print('Неправильный формат ввода (ширина поля, высота поля и количество мин через пробел')
        exit()

    pygame.mixer.pre_init(44100, -16, 1, 512)  # важно прописать до pygame.init()

    # board = Minesweeper(params)

    pygame.init()

    pygame.mixer.init()
    pygame.mixer.music.load("sounds/fon.mp3")
    # pygame.mixer.music.play(-1)

    s_glass = pygame.mixer.Sound('sounds/glass1.ogg')

    pygame.display.set_caption('Защита окон от монстров')





    #size = width, height = board.width * board.cell_size + 2 * board.left, \
    #                       board.height * board.cell_size + 2 * board.top
    screen = pygame.display.set_mode(SIZE_GAME)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if startScreen is not None:
                    if startScreen.is_click_start(event.pos):
                        startScreen = None
                    else:
                        s_glass.play()
                #board.get_click(event.pos)

        if startScreen is not None:
            startScreen.render(screen)
        else:
            screen.fill((240, 155, 89))

        pygame.display.flip()

pygame.quit()

