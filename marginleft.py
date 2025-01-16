# левый блоки игрового поля
import pygame
from vars import *
from py.button import *
from block import Block
import configparser


class MarginLeft(Block):
    def __init__(self, game):
        super().__init__(game, WIDTH_MARGIN, HEIGHT_MAP)
        self.amuletHandles = None
        self.amuletButton = None
        self.bFirstRender = True
        self.buttonAcheter = None

    def load(self, map_number):
        self.loadAmulets()

    def render(self):

        pygame.draw.rect(self.surface, FON_COLOR, (0, 0, self.width, self.height))

        # верхняя подпись
        dY = 10
        dH = 10

        font = pygame.font.Font(None, 26)
        text = font.render(f'{dispatcher.game.session.money} кредитов', True, (0, 0, 0))
        self.surface.blit(text, ((self.width - text.get_width()) / 2, dY))
        dY += text.get_height() + dH

        font = pygame.font.Font(None, 36)
        text = font.render(f'АРСЕНАЛ', True, (0, 0, 0))
        self.surface.blit(text, ((self.width - text.get_width()) / 2, dY))
        dY += text.get_height() + dH

        # амулеты
        font = pygame.font.Font(None, 18)

        lastOffsetY = 0
        for i, b in enumerate(self.amuletButton):
            b.render()
            # корректируем положение один раз
            if self.bFirstRender:
                b.offset = b.offset[0], b.offset[1] + dY

            self.surface.blit(b.surface, b.offset)
            writeText = f'{self.amuletHandles[i].name}'
            if self.amuletHandles[i].prix > dispatcher.game.session.money:
                writeText += (' (не доступно)')

            text1 = font.render(writeText, True, (0, 0, 0))
            text2 = font.render(f'{self.amuletHandles[i].prix} кредитов', True, (0, 0, 0))

            dH = (b.surface.get_height() - text1.get_height() - text2.get_height()) // 3

            dX = 15
            self.surface.blit(text1, (b.offset[0] + b.surface.get_width() + dX, b.offset[1] + dH))
            self.surface.blit(text2,
                              (b.offset[0] + b.surface.get_width() + dX,
                               b.offset[1] + dH + text1.get_height() + dH))
            lastOffsetY = b.offset[1] + b.surface.get_height() + 3 * dH

        dY = lastOffsetY

        if self.buttonAcheter is None:
            posButton = (self.width - 120) // 2, dY
            self.buttonAcheter = ImagePushButton('acheter', 'images/system/button_120x40', 'Забрать', self, posButton)
            self.buttonAcheter.setEnable(False)

        self.buttonAcheter.render()
        self.surface.blit(self.buttonAcheter.surface, self.buttonAcheter.offset)

        if self.bFirstRender:
            self.bFirstRender = False

    # загрузка описания амулетов
    def loadAmulets(self):

        amuletNames = ['diamond.png', 'amethyst.png', 'emerald.png', 'ruby.png', 'topaz.png', 'sapphire.png']
        self.amuletHandles = []
        config = configparser.ConfigParser()
        config.read('data/amulets.ini', 'utf-8')
        for amuletName in amuletNames:
            if amuletName in config:
                amulet = AmuletHandler()
                amulet.id, amulet.name, amulet.prix, amulet.life = amuletName, config[amuletName]['name'], int(
                    config[amuletName]['prix']), int(config[amuletName]['life'])
                amulet.fileName = 'images/amulets/' + amuletName
                self.amuletHandles.append(amulet)
        # отсортируем по цене
        self.amuletHandles = sorted(self.amuletHandles, key=lambda x: x.prix)

        # временно подгрузили, чтобы узнать размеры кнопки
        imageButton = pygame.image.load('images/system/amulet_on.png')

        dX, dY = 15, 15

        # создаем кнопки
        self.amuletButton = []
        for i, a in enumerate(self.amuletHandles):
            button = ImageDrawnCheckButton(a.id,
                                           'images/system/amulet',
                                           a.fileName,
                                           self,
                                           (dX, i * (imageButton.get_height() + dY)))
            button.check(False)
            button.setEnable(False)
            if a.prix <= dispatcher.game.session.money:
                button.setEnable(True)
            self.amuletButton.append(button)

    def onClick(self, pos):
        if not super().isInBlock(pos):
            return False
        x, y = pos
        for i, b in enumerate(self.amuletButton):
            b.onClick((x - b.offset[0], y - b.offset[1]))

        if self.buttonAcheter is not None:
            e = pygame.event
            e.type = pygame.MOUSEBUTTONDOWN
            e.pos = pos
            self.buttonAcheter.onClickExtend(e)
        return True

    def onPressedButton(self, buttonID, bChecked):
        bNeedUpdate = False
        print(f'{self.__class__.__name__} pressed buttonID={buttonID} bChecked={bChecked}')

    def onClickExtend(self, event):
        if not super().isInBlock(event.pos):
            return False
        if self.buttonAcheter is not None:
            self.buttonAcheter.onClickExtend(event)

    def onPushedButton(self, buttonID):
        bNeedUpdate = False
        print(f'{self.__class__.__name__} pushed buttonID={buttonID}')