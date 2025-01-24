# универсальный моб движется из начальной точки в конечную точку с заданной скорость
# по дороге моб через заданное количество тиков меняет свой вид
# моб доходит до заданной точки и там останавливается, если по пути его не убили
import sys
from vars import *


class Mob(pygame.sprite.Sprite):
    def __init__(self, parent, velocity, pos_start, pos_stop, mob_path):
        pygame.sprite.Sprite.__init__(self)
        self.parent = parent
        self.pos_start = pos_start
        self.pos_stop = pos_stop
        self.image = Mob.load_image(mob_path)
        self.rect = self.image.get_rect()
        self.vx, self.vy = Mob.__get_components(velocity, pos_start, pos_stop)
        self.velocity = velocity
        self.start = False

        self.tick = 0

        x, y = pos_start
        self.rect.left = x - self.rect.width // 2
        self.rect.top = y - self.rect.height // 2
        self.dx = self.dy = 0

    @staticmethod
    def __get_components(velocity, pos_start, pos_stop):
        dx, dy = pos_stop[0] - pos_start[0], pos_stop[1] - pos_start[1]
        dist = dist2(pos_start, pos_stop) ** 0.5
        if dist == 0:
            return 0, 0
        else:
            return velocity * dx / dist, velocity * dy / dist

    @staticmethod
    def load_image(fullname):
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
        # смотрим попадание в центр
        new_x, new_y = x_center + self.vx * dispatcher.tick / 1000, y_center + self.vy * dispatcher.tick / 1000

        # смотрим попадание в центр
        d = 3
        temp_rect = pygame.Rect(new_x - d, new_y, 2 * d, 2 * d)
        if temp_rect.collidepoint(self.pos_stop):
            # приплыли
            self.start = False
            # четко фиксируем моб в крайней точке
            x, y = self.pos_stop
            self.rect.left = x - self.rect.width // 2
            self.rect.top = y - self.rect.height // 2

        else:
            # еще плывем
            dx, dy = self.vx * dispatcher.tick / 1000, self.vy * dispatcher.tick / 1000
            new_dx, new_dy = self.dx + dx, self.dy + dy

            # TODO закинуть после отладки в отдельную функцию
            delta = 0.5
            if abs(new_dx) < 1:
                # накапливаем изменение
                self.dx = new_dx
                dx = 0
            else:
                self.dx = new_dx
                dx = int(self.dx + delta)
                self.dx = new_dx - dx

            if abs(new_dy) < 1:
                # накапливаем изменение
                self.dy = new_dy
                dy = 0
            else:
                self.dy = new_dy
                dy = int(self.dy + delta)
                self.dy = new_dy - dy

            # подрулим направление скорости из-за потери точности
            self.rect = self.rect.move((dx, dy))
            self.vx, self.vy = Mob.__get_components(self.velocity, self.rect.center, self.pos_stop)

    def render(self, screen):
        self.update()
        screen.blit(self.image, (self.rect.left, self.rect.top))


class ChangedMob(Mob):
    count_tick = 20

    def __init__(self, parent, velocity, pos_start, pos_stop, mob_path):
        super().__init__(parent, velocity, pos_start, pos_stop, mob_path + '1.png')
        self.image_list = []
        self.image_list.append(self.image)
        for i in range(2, 7):
            self.image_list.append(self.load_image(mob_path + str(i) + '.png'))
        self.tick_change = ChangedMob.count_tick

    def set_start(self):
        super().set_start()

    def render(self, screen):
        self.tick_change -= 1

        if self.tick_change == 0:
            # обновляем изображение
            self.image = self.image_list[0]
            self.image_list.pop(0)
            self.image_list.append(self.image)

            temp_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = temp_center

            self.tick_change = ChangedMob.count_tick

        super().render(screen)
