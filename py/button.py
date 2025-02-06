# разнообразные реализации примитивных кнопок
from vars import *


class CheckButton:
    def __init__(self, buttonID, parent, color_fon):
        self.image_pressed = None
        self.image_pressed_out = None
        self.buttonID = buttonID
        self.parent = parent
        self.image = None
        self.surface = None
        self.checked = False
        self.fon = color_fon

    def render(self):
        self.surface.fill(self.fon)
        if self.checked:
            self.surface.blit(self.image_pressed, (0, 0))
        else:
            self.surface.blit(self.image_pressed_out, (0, 0))

    def check(self, checked):
        self.checked = checked

    def isChecked(self):
        return self.checked

    # клик мыши
    def onClick(self, pos):
        x, y = pos
        if 0 <= x < self.image_pressed.get_width() and 0 <= y < self.image_pressed.get_height():
            # меняем состояние
            self.check(not self.isChecked())
            #  сообщаем всем что было нажатие
            self.parent.onPressedButton(self.buttonID, self.isChecked())


# полностью нарисованная кнопка
class DrawnCheckButton(CheckButton):
    def __init__(self, buttonID, name, parent, offset, color_fon = FON_COLOR):
        super().__init__(buttonID, parent, color_fon)
        self.offset = offset
        self.image_pressed = pygame.image.load('images/system/' + name + '_on.png')
        self.image_pressed_out = pygame.image.load('images/system/' + name + '_off.png')
        self.surface = pygame.Surface(
            (max(self.image_pressed.get_width(), self.image_pressed_out.get_width()),
             max(self.image_pressed.get_height(), self.image_pressed_out.get_height())))

    def get_width(self):
        return self.image_pressed.get_width()

    def get_height(self):
        return self.image_pressed.get_height()


# нарисованная кнопка с наложением картинки
# button : (path, name без _on.png/_off.png)
# image : (pathActive pathDisable)
class ImageDrawnCheckButton(CheckButton):
    def __init__(self, buttonID, buttonPath, image_path, parent, offset, color_fon = FON_COLOR):
        super().__init__(buttonID, parent, color_fon)
        self.offset = offset

        self.image_pressed = pygame.image.load(buttonPath + '_on.png')
        self.image_pressed_out = pygame.image.load(buttonPath + '_off.png')

        self.image = pygame.image.load(image_path)
        self.disableImage = pygame.image.load(image_path.replace('.png', '_gray.png'))

        self.surface = pygame.Surface(
            (max(self.image_pressed.get_width(), self.image_pressed_out.get_width()),
             max(self.image_pressed.get_height(), self.image_pressed_out.get_height())))
        self.image_offset = (self.surface.get_width() - self.image.get_width()) // 2, (
                self.surface.get_height() - self.image.get_height()) // 2

        # начальная инициализация
        super().check(False)
        self.enabled = False

    def render(self):
        super().render()
        if self.enabled:
            self.surface.blit(self.image, self.image_offset)
        else:
            self.surface.blit(self.disableImage, self.image_offset)

    def setEnable(self, enabled):
        self.enabled = enabled

    # клик мыши
    def onClick(self, pos):
        if not self.enabled:
            return
        super().onClick(pos)


# нарисованная кнопка с наложением картинки
# button : (path, name без _on.png/_off.png)
# image : (pathActive pathDisable)
class ImagePushButton:
    def __init__(self, button_id, button_path, text, parent, offset):
        self.image_up = None
        self.image_push = None
        self.image_disable = None
        self.button_id = button_id
        self.parent = parent
        self.surface = None
        self.enabled = True
        self.pushed = False
        self.offset = offset
        self.text = text

        self.image_up = pygame.image.load(button_path + '.png')
        self.image_push = pygame.image.load(button_path + '_push.png')
        self.image_disable = pygame.image.load(button_path + '_gray.png')

        self.surface = pygame.Surface((self.image_up.get_width(), self.image_up.get_height()))

    def render(self):
        font = pygame.font.Font(None, 26)
        self.surface.fill(FON_COLOR)

        if self.enabled:
            if self.pushed:
                self.surface.blit(self.image_push, (0, 0))
            else:
                self.surface.blit(self.image_up, (0, 0))
            self.button_text = font.render(self.text, True, (0, 0, 0))
        else:
            self.surface.blit(self.image_up, (0, 0))
            self.button_text = font.render(self.text, True, pygame.Color(128, 128, 128))

        offset_text = (self.image_push.get_width() - self.button_text.get_width()) // 2, (
                self.image_push.get_height() - self.button_text.get_height()) // 2
        self.surface.blit(self.button_text, offset_text)

    def setEnable(self, bEnable):
        self.enabled = bEnable

    # клик мыши
    def onClickExtend(self, event):
        if not self.enabled:
            return

        relative_pos = event.pos[0] - self.offset[0], event.pos[1] - self.offset[1]
        rect = self.surface.get_rect()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.surface.get_rect().collidepoint(relative_pos[0], relative_pos[1]):
                self.pushed = True
            else:
                self.pushed = False
            dispatcher.needUpdate(self)

        if event.type == pygame.MOUSEBUTTONUP:
            if self.surface.get_rect().collidepoint(relative_pos[0], relative_pos[1]):
                if self.pushed:
                    self.pushed = False
                    dispatcher.needUpdate(self)
                    self.parent.onPushedButton(self.button_id)

            self.pushed = False

    def onClick(self, pos):
        print(f'{pos}')
