# завершающее окно
from vars import *
from py.mob import ChangedMob


class Finish:
    def __init__(self):
        self.image = pygame.image.load('images/system/finish_screen.png')
        self.surface = pygame.Surface((self.image.get_width(), self.image.get_height()))
        self.tick = 0
        self.code_ret = True

        self.mob = []

        self.mob.append(ChangedMob(self, 100, (646, 184), (646, 184), 'images/mobs/mob7_'))
        self.mob.append(ChangedMob(self, 100, (251, 500), (251, 500), 'images/mobs/mob9_'))
        self.mob.append(ChangedMob(self, 100, (1086, 494), (1086, 494), 'images/mobs/mob8_'))
        for x in self.mob:
            x.set_start()

    def render(self, surface):
        pygame.draw.rect(surface, FON_COLOR, (0, 0, WIDTH_GAME, HEIGHT_GAME))
        x, y = (WIDTH_GAME - self.image.get_width()) // 2, (HEIGHT_GAME - self.image.get_height()) // 2
        surface.blit(self.image, (x, y))
        for x in self.mob:
            x.render(surface)
        return self.code_ret

    def on_timer(self, currentTime):
        if self.tick == 0:
            self.tick = currentTime
        else:
            if currentTime - self.tick > 5:
                self.code_ret = False
