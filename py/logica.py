import time
import pygame
from vars import *


class Logica:
    # длительность одного уровня
    interval_sec = 1 * 10

    def __init__(self, parent):
        self.parent = parent
        pygame.time.set_timer(TIMER_EVENT_GAME, Logica.interval_sec * 1000)


    def on_timer(self):
        LOG.write(f'Закончился уровень')
        dispatcher.game.game_over()