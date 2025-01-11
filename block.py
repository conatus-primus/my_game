# базовый класс для всех блоков поля игры
import pygame


class Block:
    def __init__(self, game, width, height):
        self.game = game
        self.width = width
        self.height = height
        self.surface = pygame.Surface((self.width, self.height))

    def load(self, map_number):
        pass

    def update(self, sender):
        pass

    # проверить принадлежит ли клик нашему окну
    def isInBlock(self, pos):
        x, y = pos
        return 0 <= x < self.width and 0 <= y < self.height

    def onClick(self, pos):
        pass

    # запрос на обновление
    def queryUpdate(self, sender):
        self.game.queryUpdate(sender)