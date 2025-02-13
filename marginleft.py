# левый блоки игрового поля
from py.button import *
from block import Block
import configparser
from py.amulet import AmuletPassive


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
        dY = OFFSET_HEIGHT_MARGIN
        dH = 10

        font = pygame.font.SysFont('Comic Sans MS', 24)
        text = font.render(f'Дополнительная', True, (0, 0, 0))
        self.surface.blit(text, ((self.width - text.get_width()) / 2, dY))
        dY += text.get_height()

        text = font.render(f'защита', True, (0, 0, 0))
        self.surface.blit(text, ((self.width - text.get_width()) / 2, dY))
        dY += text.get_height() + dH

        # амулеты
        font = pygame.font.SysFont('Comic Sans MS', 16)

        last_offset_y = 0
        for i, b in enumerate(self.amulet_button):
            b.render()
            # корректируем положение один раз
            if self.first_render:
                b.offset = b.offset[0], b.offset[1] + dY

            self.surface.blit(b.surface, b.offset)
            write_text = f'{self.amulet_handles[i].name}'


            if self.amulet_handles[i].price_now <= 0:
                text_color = (100, 100, 100)
                price = self.amulet_handles[i].price_max
            else:
                text_color = (0, 0, 0)
                price = self.amulet_handles[i].price_now

            text1 = font.render(write_text, True, text_color)
            text2 = font.render(f'{price} монстров', True, text_color)

            dH = (b.surface.get_height() - text1.get_height() - text2.get_height()) // 3

            dX = 10
            self.surface.blit(text1, (b.offset[0] + b.surface.get_width() + dX, b.offset[1] + dH))
            self.surface.blit(text2,
                              (b.offset[0] + b.surface.get_width() + dX,
                               b.offset[1] + dH + text1.get_height() + dH))
            last_offset_y = b.offset[1] + b.surface.get_height() + 3 * dH

        dY = last_offset_y

        # if self.button_acheter is None:
        #     pos_button = (self.width - 120) // 2, dY
        #     self.button_acheter = ImagePushButton('acheter', 'images/system/button_120x40', 'Забрать', self, pos_button)
        #     self.button_acheter.setEnable(False)
        #
        # self.button_acheter.render()
        # self.surface.blit(self.button_acheter.surface, self.button_acheter.offset)

        if self.first_render:
            self.first_render = False

    # загрузка описания амулетов
    def loadAmulets(self):

        self.amulet_handles = []
        AmuletPassive.load_amulets(self.amulet_handles)

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
            self.amulet_button.append(button)

        dispatcher.game.amulet_handles = self.amulet_handles

    def onClick(self, pos):
        return False
        # if not super().isInBlock(pos):
        #     return False
        # x, y = pos
        # for i, b in enumerate(self.amulet_button):
        #     b.onClick((x - b.offset[0], y - b.offset[1]))
        #
        # if self.button_acheter is not None:
        #     e = pygame.event
        #     e.type = pygame.MOUSEBUTTONDOWN
        #     e.pos = pos
        #     self.button_acheter.on_click_extend(e)
        # return True

    def onPressedButton(self, button_id, checked):
        need_update = False
        print(f'{self.__class__.__name__} pressed buttonID={button_id} bChecked={checked}')

    def on_click_extend(self, event):
        pass
        # if not super().isInBlock(event.pos):
        #     return False
        # if self.button_acheter is not None:
        #     self.button_acheter.on_click_extend(event)

    def onPushedButton(self, button_id):
        need_update = False
        print(f'{self.__class__.__name__} pushed buttonID={button_id}')

    def game_replay(self):
        self.game_over(False)

    # действия связанные с началом игры
    def game_start(self):
        pass

    # закончилась игра
    def game_over(self, flag_success):
        for i, a in enumerate(self.amulet_handles):
            a.price_now = 0
            self.amulet_button[i].setEnable(False)
        self.render()

    def on_message(self, message_id, *params):

        if message_id == MessadgID.DEF_AMULETS_CLEAR:
            self.game_over(False)
            self.render()

        if message_id == MessadgID.DEF_AMULET_BALL:
            id_amulet, balls = params
            for i, a in enumerate(self.amulet_handles):
                if a.id == id_amulet:
                    self.amulet_handles[i].price_now = balls
                    self.amulet_button[i].setEnable(balls > 0)
                    self.amulet_button[i].check(balls > 0)
                    break
            self.render()
