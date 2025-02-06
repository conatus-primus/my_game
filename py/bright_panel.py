from py.button import *


class BrightPanel:
    def __init__(self, block, width):
        self.block = block
        self.w = width // (len(BRIGHTEN) + 2)
        self.h = 26
        self.surface = pygame.Surface((len(BRIGHTEN) * self.w, self.h))

    # нарисовать панель яркости с выделенным квадратом текущей яркости
    def render(self):
        baseColor = pygame.Color(FON_COLOR_DARK)

        for i in range(len(BRIGHTEN)):
            imageSquare = pygame.Surface([self.w, self.h])
            imageSquare.fill(baseColor)
            brightColor = (BRIGHTEN[i], BRIGHTEN[i], BRIGHTEN[i])
            imageSquare.fill(brightColor, special_flags=pygame.BLEND_RGB_SUB)
            self.surface.blit(imageSquare, (i * self.w, 0))

        if dispatcher.session.brightness < len(BRIGHTEN):
            D = 2
            brightRect = (dispatcher.session.brightness * self.w + D, D, self.w - 2 * D, self.h - 2 * D)
            pygame.draw.rect(self.surface, pygame.Color('white'), brightRect, 1)

    # клик мыши
    def onClick(self, pos):
        x, y = pos
        if 0 <= x < len(BRIGHTEN) * self.w and 0 <= y < self.h:
            # поменяли атрибут в сессии
            dispatcher.session.brightness = int(x // self.w)
            #  сообщаем всем что было изменение
            dispatcher.needUpdate(self)
