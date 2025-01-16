# разнообразные реализации примитивных кнопок
import pygame

from vars import *


class CheckButton:
    def __init__(self, buttonID, parent):
        self.imagePressed = None
        self.imagePressedOut = None
        self.buttonID = buttonID
        self.parent = parent
        self.image = None
        self.surface = None
        self.checked = False

    def render(self):
        self.surface.fill(FON_COLOR)
        if self.checked:
            self.surface.blit(self.imagePressed, (0, 0))
        else:
            self.surface.blit(self.imagePressedOut, (0, 0))

    def check(self, bCheck):
        self.checked = bCheck

    def isChecked(self):
        return self.checked

    # клик мыши
    def onClick(self, pos):
        x, y = pos
        if 0 <= x < self.imagePressed.get_width() and 0 <= y < self.imagePressed.get_height():
            # меняем состояние
            self.check(not self.isChecked())
            #  сообщаем всем что было нажатие
            self.parent.onPressedButton(self.buttonID, self.isChecked())


# полностью нарисованная кнопка
class DrawnCheckButton(CheckButton):
    def __init__(self, buttonID, name, parent, offset):
        super().__init__(buttonID, parent)
        self.offset = offset
        self.imagePressed = pygame.image.load('images/system/' + name + '_on.png')
        self.imagePressedOut = pygame.image.load('images/system/' + name + '_off.png')
        self.surface = pygame.Surface(
            (max(self.imagePressed.get_width(), self.imagePressedOut.get_width()),
             max(self.imagePressed.get_height(), self.imagePressedOut.get_height())))


# нарисованная кнопка с наложением картинки
# button : (path, name без _on.png/_off.png)
# image : (pathActive pathDisable)
class ImageDrawnCheckButton(CheckButton):
    def __init__(self, buttonID, buttonPath, imagePath, parent, offset):
        super().__init__(buttonID, parent)
        self.offset = offset

        self.imagePressed = pygame.image.load(buttonPath + '_on.png')
        self.imagePressedOut = pygame.image.load(buttonPath + '_off.png')

        self.image = pygame.image.load(imagePath)
        self.disableImage = pygame.image.load(imagePath.replace('.png', '_gray.png'))

        self.surface = pygame.Surface(
            (max(self.imagePressed.get_width(), self.imagePressedOut.get_width()),
             max(self.imagePressed.get_height(), self.imagePressedOut.get_height())))
        self.imageOffset = (self.surface.get_width() - self.image.get_width()) // 2, (
                self.surface.get_height() - self.image.get_height()) // 2

        # начальная инициализаци
        super().check(False)
        self.enabled = False

    def render(self):
        super().render()
        if self.enabled:
            self.surface.blit(self.image, self.imageOffset)
        else:
            self.surface.blit(self.disableImage, self.imageOffset)

    def setEnable(self, bEnable):
        self.enabled = bEnable

    # клик мыши
    def onClick(self, pos):
        if not self.enabled:
            return
        super().onClick(pos)


# нарисованная кнопка с наложением картинки
# button : (path, name без _on.png/_off.png)
# image : (pathActive pathDisable)
class ImagePushButton:
    def __init__(self, buttonID, buttonPath, text, parent, offset):

        self.imageUp = None
        self.imagePush = None
        self.imageDisable = None
        self.buttonID = buttonID
        self.parent = parent
        self.surface = None
        self.enabled = True
        self.pushed = False
        self.offset = offset
        self.text = text

        self.imageUp = pygame.image.load(buttonPath + '.png')
        self.imagePush = pygame.image.load(buttonPath + '_push.png')
        self.imageDisable = pygame.image.load(buttonPath + '_gray.png')

        self.surface = pygame.Surface((self.imageUp.get_width(), self.imageUp.get_height()))

    def render(self):
        font = pygame.font.Font(None, 26)
        self.surface.fill(FON_COLOR)

        if self.enabled:
            if self.pushed:
                self.surface.blit(self.imagePush, (0, 0))
            else:
                self.surface.blit(self.imageUp, (0, 0))
            self.buttonText = font.render(self.text, True, (0, 0, 0))
        else:
            self.surface.blit(self.imageUp, (0, 0))
            self.buttonText = font.render(self.text, True, pygame.Color(128, 128, 128))

        offsetText = (self.imagePush.get_width() - self.buttonText.get_width()) // 2, (
                    self.imagePush.get_height() - self.buttonText.get_height()) // 2
        self.surface.blit(self.buttonText, offsetText)

    def setEnable(self, bEnable):
        self.enabled = bEnable

    # клик мыши
    def onClickExtend(self, event):
        if not self.enabled:
            return

        relativePos = event.pos[0] - self.offset[0], event.pos[1] - self.offset[1]
        rect = self.surface.get_rect()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.surface.get_rect().collidepoint(relativePos[0], relativePos[1]):
                self.pushed = True
            else:
                self.pushed = False
            dispatcher.needUpdate(self)


        if event.type == pygame.MOUSEBUTTONUP:
            if self.surface.get_rect().collidepoint(relativePos[0], relativePos[1]):
                if self.pushed:
                    self.pushed = False
                    dispatcher.needUpdate(self)
                    self.parent.onPushedButton(self.buttonID)

            self.pushed = False

    def onClick(self, pos):
        print(f'{pos}')
