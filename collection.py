# коллекция всех карт
from block import Block
from py.biblio import *


class Collection(Block):
    def __init__(self, game):
        super().__init__(game, WIDTH_MAP, HEIGHT_MAP)
        self.font = pygame.font.Font(None, HEIGHT_HEADER - 20)
        self.biblio = None

    def render(self):
        pygame.draw.rect(self.surface, FON_COLOR_DARK, (0, 0, self.width, self.height))
        if self.biblio is not None:
            self.biblio.render(self.surface)

    def load(self, map_number):
        self.biblio = Biblio(self)
        self.biblio.load()

    def on_click(self, pos):
        if not super().is_in_block(pos):
            return False
        x, y = pos

        if self.biblio is not None:
            ret = self.biblio.on_click(pos)
            if ret is True:
                map = self.biblio.get_clicked_map()
                LOG.write(f'Стоим на карте {map.map_number}')
            return ret
        else:
            return False

    def on_double_click(self, event):
        if not super().is_in_block(event.pos):
            return False
        if self.biblio is not None:
            return self.biblio.on_double_click(event)
        else:
            return False

    def on_pressed_key(self, pressed_keys):
        return self.biblio.on_pressed_key(pressed_keys)