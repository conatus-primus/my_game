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
        return False

    # запрос на обновление
    def needUpdate(self, sender):
        self.game.needUpdate(sender)

    def onTimer(self, currentTime):
        return False

    def onPressedKey(self, pressed_keys):
        return False

    def onClickExtend(self, event):
        pass
