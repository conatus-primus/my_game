# правый блоки игрового поля
from vars import *
from py.button import *
from block import Block
import enum


class ButtonID(enum.Enum):
    # переключение звуков
    ID_BUTTON_SOUND = 1000
    # переключение фоновой музыки
    ID_BUTTON_CHANSON = 1001


class MarginRight(Block):
    def __init__(self, game):
        super().__init__(game, WIDTH_MARGIN, HEIGHT_MAP)
        self.brightPanel = BrightPanel(self, WIDTH_MARGIN)
        self.brightOffset = ((self.width - self.brightPanel.surface.get_width()) / 2, self.brightPanel.w)

        self.buttonSound = DrawnCheckButton(ButtonID.ID_BUTTON_SOUND, 'sound', self, (20, 70))
        self.buttonChanson = DrawnCheckButton(ButtonID.ID_BUTTON_CHANSON, 'chanson', self, (100, 70))

    def load(self, session):
        self.buttonSound.check(self.game.session.soundsActive)
        self.buttonChanson.check(self.game.session.chansonActive)

    def render(self):
        pygame.draw.rect(self.surface, FON_COLOR, (0, 0, self.width, self.height))
        self.brightPanel.render()
        self.surface.blit(self.brightPanel.surface, self.brightOffset)

        dX = 20
        dY = 70

        self.buttonSound.render()
        self.surface.blit(self.buttonSound.surface, self.buttonSound.offset)

        self.buttonChanson.render()
        self.surface.blit(self.buttonChanson.surface, self.buttonChanson.offset)

        # image_sound = pygame.image.load(CURRENT_DIRECTORY + '/images/system/sound2.png')
        # self.surface.blit(image_sound, (dX, 60))
        # image_chanson = pygame.image.load(CURRENT_DIRECTORY + '/images/system/chanson3.png')
        # self.surface.blit(image_chanson, (dX + image_sound.get_width() + dX, 60))

    # клик мыши
    def onClick(self, pos):
        if not super().isInBlock(pos):
            return False
        x, y = pos
        self.brightPanel.onClick((x - self.brightOffset[0], y - self.brightOffset[1]))
        self.buttonSound.onClick((x - self.buttonSound.offset[0], y - self.buttonSound.offset[1]))
        self.buttonChanson.onClick((x - self.buttonChanson.offset[0], y - self.buttonChanson.offset[1]))
        return True

    def onPressedButton(self, buttonID, bChecked):
        bNeedUpdate = False
        if buttonID == ButtonID.ID_BUTTON_SOUND:
            bNeedUpdate = True
            self.game.session.soundsActive = bChecked
            v = self.game.session.volumeLevel - 0.1
            if v <= 0:
                v = 1
            pygame.mixer.music.set_volume(v)
            self.game.session.volumeLevel = v

        if buttonID == ButtonID.ID_BUTTON_CHANSON:
            bNeedUpdate = True
            self.game.session.chansonActive = bChecked

        print(f'button {buttonID} : check={bChecked}')
        if bNeedUpdate:
            dispatcher.needUpdate(self)


class BrightPanel:
    def __init__(self, block, width):
        self.block = block
        self.w = width // (len(BRIGHTEN) + 2)
        self.h = 26
        self.surface = pygame.Surface((len(BRIGHTEN) * self.w, self.h))

    # нарисовать панель яркости с выделенным квадратом текущей яркости
    def render(self):
        baseColor = pygame.Color("black")

        for i in range(len(BRIGHTEN)):
            imageSquare = pygame.Surface([self.w, self.h])
            imageSquare.fill(baseColor)
            brightColor = (BRIGHTEN[i], BRIGHTEN[i], BRIGHTEN[i])
            imageSquare.fill(brightColor, special_flags=pygame.BLEND_RGB_ADD)
            self.surface.blit(imageSquare, (i * self.w, 0))

        if self.block.game.session.brightness < len(BRIGHTEN):
            D = 2
            brightRect = (self.block.game.session.brightness * self.w + D, D, self.w - 2 * D, self.h - 2 * D)
            pygame.draw.rect(self.surface, pygame.Color('white'), brightRect, 1)

    # клик мыши
    def onClick(self, pos):
        x, y = pos
        if 0 <= x < len(BRIGHTEN) * self.w and 0 <= y < self.h:
            # поменяли атрибут в сессии
            self.block.game.session.brightness = int(x // self.w)
            #  сообщаем всем что было изменение
            dispatcher.needUpdate(self)

