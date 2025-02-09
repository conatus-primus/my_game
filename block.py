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

    def on_timer(self, currentTime):
        return False

    def onPressedKey(self, pressed_keys):
        return False

    def onClickExtend(self, event):
        pass

    def on_double_click(self, event):
        pass

    # GameState
    def on_changed_state(self, old_state, new_state):
        pass

    # действия связанные с началом игры
    def game_start(self):
        pass

    # встали на паузу
    def game_pause(self):
        pass

    # продолжить игру после паузы
    def game_continue(self):
        pass

    # начать играть заново
    def game_replay(self):
        pass

    # закончилась игра
    def game_over(self, flag_success):
        pass
