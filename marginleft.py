# левый блоки игрового поля
from py.button import *
from block import Block
import configparser


class MarginLeft(Block):
    def __init__(self, game):
        super().__init__(game, WIDTH_MARGIN, HEIGHT_MAP)
        self.amulet_handles = None
        self.amulet_button = None
        self.first_render = True
        self.button_acheter = None

    def load(self, map_number):
        self.loadAmulets()

    def render(self):

        pygame.draw.rect(self.surface, FON_COLOR_MID, (0, 0, self.width, self.height))
        pygame.draw.rect(self.surface, FON_COLOR, (0, 0, self.width - 5, self.height))

        # верхняя подпись
        dY = 10
        dH = 10

        font = pygame.font.Font(None, 26)
        text = font.render(f'{dispatcher.session.money} кредитов', True, (0, 0, 0))
        self.surface.blit(text, ((self.width - text.get_width()) / 2, dY))
        dY += text.get_height() + dH

        font = pygame.font.Font(None, 36)
        text = font.render(f'АРСЕНАЛ', True, (0, 0, 0))
        self.surface.blit(text, ((self.width - text.get_width()) / 2, dY))
        dY += text.get_height() + dH

        # амулеты
        font = pygame.font.Font(None, 18)

        last_offset_y = 0
        for i, b in enumerate(self.amulet_button):
            b.render()
            # корректируем положение один раз
            if self.first_render:
                b.offset = b.offset[0], b.offset[1] + dY

            self.surface.blit(b.surface, b.offset)
            write_text = f'{self.amulet_handles[i].name}'
            if self.amulet_handles[i].prix > dispatcher.session.money:
                write_text += (' (не доступно)')

            text1 = font.render(write_text, True, (0, 0, 0))
            text2 = font.render(f'{self.amulet_handles[i].prix} кредитов', True, (0, 0, 0))

            dH = (b.surface.get_height() - text1.get_height() - text2.get_height()) // 3

            dX = 15
            self.surface.blit(text1, (b.offset[0] + b.surface.get_width() + dX, b.offset[1] + dH))
            self.surface.blit(text2,
                              (b.offset[0] + b.surface.get_width() + dX,
                               b.offset[1] + dH + text1.get_height() + dH))
            last_offset_y = b.offset[1] + b.surface.get_height() + 3 * dH

        dY = last_offset_y

        if self.button_acheter is None:
            pos_button = (self.width - 120) // 2, dY
            self.button_acheter = ImagePushButton('acheter', 'images/system/button_120x40', 'Забрать', self, pos_button)
            self.button_acheter.setEnable(False)

        self.button_acheter.render()
        self.surface.blit(self.button_acheter.surface, self.button_acheter.offset)

        if self.first_render:
            self.first_render = False

    # загрузка описания амулетов
    def loadAmulets(self):

        amulet_names = ['diamond.png', 'amethyst.png', 'emerald.png', 'ruby.png', 'topaz.png', 'sapphire.png']
        self.amulet_handles = []
        config = configparser.ConfigParser()
        config.read('data/amulets.ini', 'utf-8')
        for name in amulet_names:
            if name in config:
                amulet = AmuletHandler()
                amulet.id, amulet.name, amulet.prix, amulet.life = name, config[name]['name'], int(
                    config[name]['prix']), int(config[name]['life'])
                amulet.fileName = 'images/amulets/' + name
                self.amulet_handles.append(amulet)
        # отсортируем по цене
        self.amulet_handles = sorted(self.amulet_handles, key=lambda x: x.prix)

        # временно подгрузили, чтобы узнать размеры кнопки
        image_button = pygame.image.load('images/system/amulet_on.png')

        dX, dY = 15, 15

        # создаем кнопки
        self.amulet_button = []
        for i, a in enumerate(self.amulet_handles):
            button = ImageDrawnCheckButton(a.id,
                                           'images/system/amulet',
                                           a.fileName,
                                           self,
                                           (dX, i * (image_button.get_height() + dY)))
            button.check(False)
            button.setEnable(False)
            if a.prix <= dispatcher.session.money:
                button.setEnable(True)
            self.amulet_button.append(button)

    def onClick(self, pos):
        if not super().isInBlock(pos):
            return False
        x, y = pos
        for i, b in enumerate(self.amulet_button):
            b.onClick((x - b.offset[0], y - b.offset[1]))

        if self.button_acheter is not None:
            e = pygame.event
            e.type = pygame.MOUSEBUTTONDOWN
            e.pos = pos
            self.button_acheter.on_click_extend(e)
        return True

    def onPressedButton(self, button_id, checked):
        need_update = False
        print(f'{self.__class__.__name__} pressed buttonID={button_id} bChecked={checked}')

    def on_click_extend(self, event):
        if not super().isInBlock(event.pos):
            return False
        if self.button_acheter is not None:
            self.button_acheter.on_click_extend(event)

    def onPushedButton(self, button_id):
        need_update = False
        print(f'{self.__class__.__name__} pushed buttonID={button_id}')
