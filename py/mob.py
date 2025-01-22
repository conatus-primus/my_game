# универсальный моб движется из начальной точки в конечную точку с заданной скорость
# по дороге моб через заданное количество тиков меняет свой вид
# моб доходит до заданной точки и там останавливается, если по пути его не убили
import sys

import pygame

from vars import *


class Mob(pygame.sprite.Sprite):
    def __init__(self, parent, velocity, pos_start, pos_stop, mob_path):
        pygame.sprite.Sprite.__init__(self)
        self.parent = parent
        self.pos_start = pos_start
        self.pos_stop = pos_stop
        self.image = self.load_image(mob_path)
        self.rect = self.image.get_rect()
        self.vx, self.vy = self.__get_components(velocity, pos_start, pos_stop)
        self.start = False
        self.tick = 0

        x, y = pos_start
        self.rect.left = x - self.rect.width // 2
        self.rect.top = y - self.rect.height // 2

    def __get_components(self, velocity, pos_start, pos_stop):
        dX, dy = pos_stop[0] - pos_start[0], pos_stop[1] - pos_start[1]
        dist = dist2(pos_start, pos_stop) ** 0.5
        if dist == 0:
            return 0, 0
        else:
            return velocity * dX / dist, velocity * dy / dist

    def load_image(self, fullname):
        if not os.path.isfile(fullname):
            print(f'Файл с изображением {fullname} не найден')
            sys.exit()
        image = pygame.image.load(fullname)
        return image

    def set_start(self):
        self.start = True

    def update(self):
        if not self.start:
            return

        x_center, y_center = self.rect.left + self.rect.width // 2, self.rect.top + self.rect.height // 2

        new_x, new_y = x_center + self.vx * dispatcher.tick / 1000, y_center + self.vy * dispatcher.tick / 1000
        d = 3
        temp_rect = pygame.Rect(new_x - d, new_y, 2 * d, 2 * d)
        if temp_rect.collidepoint(self.pos_stop):
            # приплыли
            self.start = False
            # четко фиксируем моба в крайней точке
            x, y = self.pos_stop
            self.rect.left = x - self.rect.width // 2
            self.rect.top = y - self.rect.height // 2
        else:
            # еще плывем
            self.rect = self.rect.move((self.vx * dispatcher.tick / 1000, self.vy * dispatcher.tick / 1000))

    def render(self, screen):
        self.update()
        screen.blit(self.image, (self.rect.left, self.rect.top))


class ChangedMob(Mob):
    count_tick = 60

    def __init__(self, parent, velocity, pos_start, pos_stop, mob_path):
        super().__init__(parent, velocity, pos_start, pos_stop, mob_path + '1')
        self.image_next = self.load_image(mob_path + '2')
        self.tick_change = ChangedMob.count_tick

    def set_start(self):
        super().set_start()

    def render(self, screen):
        self.tick_change -= 1

        if self.tick_change == 0:
            # обновляем изображение
            self.image_next, self.image = self.image, self.image_next
            self.tick_change = ChangedMob.count_tick
