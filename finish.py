# завершающее окно
from vars import *
from py.mob import ChangedMob


class Finish:
    def __init__(self):
        self.image = pygame.image.load('images/system/finish_screen.png')
        self.surface = pygame.Surface((self.image.get_width(), self.image.get_height()))
        self.tick = None
        self.tick2 = None
        self.code_ret = True

        self.mob = []

        velocity = 150
        self.mob.append(ChangedMob(self, velocity, (30, 184), (WIDTH_GAME // 2, 184), 'mob7', None, None, 1))
        self.mob.append(ChangedMob(self, velocity, (WIDTH_GAME - 30, 184), (WIDTH_GAME // 3, 184), 'mob7', None, None, 3))

        self.mob.append(ChangedMob(self, velocity, (251, 500), (251, 500), 'mob9', None, None))
        self.mob.append(ChangedMob(self, velocity, (1086, 494), (1086, 494), 'mob6', None, None))
        self.mob.append(ChangedMob(self, velocity, (WIDTH_GAME // 2, 784), (WIDTH_GAME // 2, 784), 'mob8', None, None))
        for x in self.mob:
            x.set_start()

    def render(self, surface):
        pygame.draw.rect(surface, FON_COLOR, (0, 0, WIDTH_GAME, HEIGHT_GAME))
        x, y = (WIDTH_GAME - self.image.get_width()) // 2, (HEIGHT_GAME - self.image.get_height()) // 2
        surface.blit(self.image, (x, y))
        for x in self.mob:
            x.render(surface)

        if self.mob[0].velocity == 0:
            if self.tick2 == 15:
                self.mob.pop(0)
                self.mob.pop(0)
                x = ChangedMob(self, 100, (WIDTH_GAME // 2, 184), (WIDTH_GAME // 2, 184), 'mob7', None, None)
                x.set_start()
                self.mob.append(x)
            else:
                self.tick2 += 1
        else:
            if pygame.Rect.colliderect(self.mob[0].rect, self.mob[1].rect):
                self.mob[0].last_show(True)
                self.mob[1].last_show(False)
                self.tick = 0
                self.tick2 = 0

        return self.code_ret

    def on_timer(self, currentTime):
        if self.tick is None:
            return

        if self.tick == 0:
            self.tick = currentTime
            sounds.finish()
        else:
            if currentTime - self.tick > 3:
                self.code_ret = False
