# окно с сообщением
import pygame
from vars import *

class Message:
    def __init__(self, text):
        self.image = pygame.image.load(CURRENT_DIRECTORY + '/images/message.png')
        self.surface = pygame.Surface((self.image.get_width(), self.image.get_height()))

    def render(self, surface):
        self.surface.blit(self.image, (0, 0))
        scale = pygame.transform.scale(
            self.surface, (self.surface.get_width() // 3 * 2, self.surface.get_height() // 3 * 2))
        scale_rect = scale.get_rect(center=(WIDTH_GAME // 2, HEIGHT_GAME // 2))
        surface.blit(scale, scale_rect)
