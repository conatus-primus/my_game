# начальная заставка
import pygame
from vars import *


class ScreenSaver:
    def __init__(self):
        self.image = pygame.image.load(CURRENT_DIRECTORY + '/images/screensaver.png')
        dt = 5
        self.rect = (404 - dt, 666 - dt, 923 + dt, 683 + dt)

    def render(self, screen):
        screen.blit(self.image, (0, 0))
        colors = screen.get_at((0, 0))[:3]
        screen.fill(colors)
        screen.blit(self.image,
                    ((SIZE_GAME[0] - self.image.get_width()) // 2, (SIZE_GAME[1] - self.image.get_height()) // 2))

    def is_click_start(self, pos):
        l, t, r, b = self.rect
        x, y = pos
        return l <= x <= r and t <= y <= b