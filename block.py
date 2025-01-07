# базовый класс для всех блоков поля игры
import pygame


class Block:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.surface = pygame.Surface((self.width, self.height))

    def load(self, map_number):
        pass