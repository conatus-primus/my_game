# универсальная панель отображается активные квадраты и пассивные квадраты
# можно кликать на активные квадраты, по клику выделяется и идет нотификация о выборе
# можно использовать для показа уровней (3 активных из 5), сложности (без клика), медалей
from vars import *
import pygame


class ImagePanel:
    def __init__(self, parent, color_fon):
        self.parent = parent
        self.image_enabled = None
        self.image_disabled = None
        # подсветка текущего индекса
        self.current_index = None
        # размер панели
        self.width = self.height = 0
        self.loaded = False
        self.max_count = 0
        self.enabled_count = 0
        self.color_fon = pygame.Color(color_fon)
        self.surface = None
        self.offset = None
        self.size_cell = None

    # size - размер ячейки
    def load(self, image_path_enabled, image_path_disabled, size_cell, max_count):
        self.image_enabled = Dispatcher.load_image(image_path_enabled)
        self.image_disabled = Dispatcher.load_image(image_path_disabled)
        self.loaded = False
        try:
            if self.image_enabled is None or self.image_disabled is None:
                raise (f'Не загружена панель {image_path_enabled} {image_path_disabled}')

            width_cell, height_cell = size_cell
            # смотрим что с размерами (должно все биться с раземром ячейки и максимальным количеством)
            if self.image_enabled.get_height() < height_cell or self.image_disabled.get_height() < height_cell:
                raise (f'Высота ячейки {size_cell} не согласуется с {image_path_enabled} {image_path_disabled}')

            if self.image_enabled.get_width() // max_count < width_cell or \
                    self.image_disabled.get_width() // max_count < width_cell:
                raise (f'Ширина ячейки {size_cell} не согласуется с {image_path_enabled} {image_path_disabled}')

            self.max_count = max_count
            self.size_cell = size_cell
            self.width, self.height = max_count * width_cell, height_cell
            self.max_count = max_count

            # внтури сразу подготовится панель
            self.set_enabled_count(0)
            self.loaded = True

        except Exception as e:
            LOG.write(str(e))

    def set_enabled_count(self, count):
        if self.loaded is False:
            return
        if count is None:
            self.enabled_count = 0
        elif 0 <= count <= self.max_count:
            self.enabled_count = count
        else:
            self.enabled_count = 0
        # пересчитываем вид панели
        self.update()

    # пересчитываем вид панели
    def update(self):
        image_pos = [(self.image_enabled, self.enabled_count, (0, 0)),
                     (self.image_disabled, self.max_count - self.enabled_count,
                      (self.enabled_count * self.size_cell[0], 0))
                     ]

        w, h = self.size_cell
        self.surface = pygame.Surface((self.width, self.height))
        self.surface = self.surface.convert_alpha()
        self.surface.fill((0, 0, 0, 0))
        pygame.draw.rect(self.surface, self.color_fon, (0, 0, self.width, self.height), 0, 5)

        for x in image_pos:
            image, count, offset = x
            surface = pygame.Surface((w * count, h))
            surface = self.surface.convert_alpha()
            surface.fill((0, 0, 0, 0))
            surface.blit(image, (0, 0))
            self.surface.blit(surface, offset)

    def set_active_index(self, index):
        if self.loaded is False:
            return
        if index is None:
            self.current_index = None
        elif 0 <= index < self.max_count:
            self.current_index = index
        else:
            self.current_index = None

    # нарисовать панель с выделенным квадратом текущей яркости
    def render(self, screen, offset):
        if self.loaded is False:
            return
        screen.blit(self.surface, offset)

    # клик мыши
    def on_click(self, pos):
        x, y = pos
        # if 0 <= x < len(BRIGHTEN) * self.w and 0 <= y < self.h:
        #     # поменяли атрибут в сессии
        #     dispatcher.session.brightness = int(x // self.w)
        #     #  сообщаем всем что было изменение
        #     dispatcher.needUpdate(self)
