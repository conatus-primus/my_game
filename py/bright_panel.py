from py.button import *


class BrightPanel:
    def __init__(self, block, width):
        self.block = block
        self.w = width // (len(BRIGHTEN) + 2)
        self.h = 26
        self.surface = pygame.Surface((len(BRIGHTEN) * self.w, self.h))

    # нарисовать панель яркости с выделенным квадратом текущей яркости
    def render(self):
        base_color = pygame.Color(FON_COLOR_DARK)

        for i in range(len(BRIGHTEN)):
            image_square = pygame.Surface([self.w, self.h])
            image_square.fill(base_color)
            bright_color = (BRIGHTEN[i], BRIGHTEN[i], BRIGHTEN[i])
            image_square.fill(bright_color, special_flags=pygame.BLEND_RGB_SUB)
            self.surface.blit(image_square, (i * self.w, 0))

        if dispatcher.session.brightness < len(BRIGHTEN):
            D = 2
            bright_rect = (dispatcher.session.brightness * self.w + D, D, self.w - 2 * D, self.h - 2 * D)
            pygame.draw.rect(self.surface, pygame.Color('white'), bright_rect, 1)

    # клик мыши
    def on_click(self, pos):
        x, y = pos
        if 0 <= x < len(BRIGHTEN) * self.w and 0 <= y < self.h:
            # поменяли атрибут в сессии
            dispatcher.session.brightness = int(x // self.w)
            #  сообщаем всем что было изменение
            dispatcher.need_update(self)
