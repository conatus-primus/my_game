# подвал игрового поля
import pygame
from vars import *
from block import Block
from py.button import *


class ButtonID(enum.Enum):
    # переключение звуков
    ID_BUTTON_SOUND = 1005
    # переключение фоновой музыки
    ID_BUTTON_CHANSON = 1006


class Footer(Block):
    def __init__(self, game):
        super().__init__(game, WIDTH_GAME, HEIGHT_FOOTER)
        self.state = GameState.GAME_NO
        self.offset_y = 0
        self.image_sortir = Dispatcher.load_image('images/system/sortir.png')
        self.offset_sortir = WIDTH_GAME - self.image_sortir.get_width(), (
                self.height - self.image_sortir.get_height()) // 2

        # ужас просто ужас напроектировала...
        temp = DrawnCheckButton(ButtonID.ID_BUTTON_SOUND, 'sound', self, (0, 0))

        self.buttonSound = DrawnCheckButton(ButtonID.ID_BUTTON_SOUND, 'sound', self,
                                            (HEIGHT_FOOTER // 4, (HEIGHT_FOOTER - temp.get_height()) // 2), FON_COLOR_MID)
        self.buttonChanson = DrawnCheckButton(ButtonID.ID_BUTTON_CHANSON, 'chanson', self,
                                              (HEIGHT_FOOTER // 2 + temp.get_width(),
                                               (HEIGHT_FOOTER - temp.get_height()) // 2), FON_COLOR_MID)
        del temp

    def load(self, map_number):
        self.buttonSound.check(dispatcher.session.soundsActive)
        self.buttonChanson.check(dispatcher.session.chansonActive)

        for id, dscr in Machine.buttons.items():
            path, _, _ = dscr
            fullpath = 'images/system/states/' + path
            image = Dispatcher.load_image(fullpath)
            if image is None:
                LOG.write(f'Нижняя панель: ошибка загрузки {fullpath}')
                exit()
            Machine.buttons[id] = path, image, None
            # загрузка - самое начало
        self.set_state(self.state)

    def set_state(self, state):
        LOG.write(f'Новое состояние игры {state}')
        # пересчитать положение кнопок
        if state not in Machine.states.keys():
            self.state = GameState.GAME_NO
            return

        self.state = state

        if self.state == GameState.GAME_NO:
            return

        self.offset_y = 0
        width = 0
        for button_id in Machine.states[self.state]:
            dscr_button = Machine.buttons[button_id]
            path, image, _ = dscr_button
            if image is None:
                LOG.write(f'Нижняя панель: ошибка разбора {path}')
                exit()
            LOG.write(f'Загружаем в нижнюю панель: {path}')
            width += image.get_width()
            self.offset_y = (self.height - image.get_height()) // 2
        margin = (WIDTH_MAP - width) // (len(Machine.states[self.state]) + 1)

        offset = WIDTH_MARGIN + margin
        self.offset = {}
        for button_id in Machine.states[self.state]:
            dscr_button = Machine.buttons[button_id]
            path, image, _ = dscr_button
            Machine.buttons[button_id] = path, image, offset
            offset += image.get_width() + margin

    def render(self):
        pygame.draw.rect(self.surface, FON_COLOR_MID, (0, 0, self.width, self.height))

        for button_id in Machine.states[self.state]:
            dscr_button = Machine.buttons[button_id]
            _, image, offset_x = dscr_button
            self.surface.blit(image, (offset_x, self.offset_y))

        self.surface.blit(self.image_sortir, self.offset_sortir)

        self.buttonSound.render()
        self.surface.blit(self.buttonSound.surface, self.buttonSound.offset)
        self.buttonChanson.render()
        self.surface.blit(self.buttonChanson.surface, self.buttonChanson.offset)

    def onClick(self, pos):
        x, y = pos

        self.buttonSound.onClick((x - self.buttonSound.offset[0], y - self.buttonSound.offset[1]))
        self.buttonChanson.onClick((x - self.buttonChanson.offset[0], y - self.buttonChanson.offset[1]))

        for button_id in Machine.states[self.state]:
            dscr_button = Machine.buttons[button_id]
            _, image, offset_x = dscr_button
            if offset_x <= x <= image.get_width() + offset_x and self.offset_y <= y <= image.get_height() + self.offset_y:
                LOG.write(f'Нажато {button_id}')
                # сообщить об изменении состояния игры
                dispatcher.game.notify_about_change_state(button_id)
                return True

        off_x, off_y = self.offset_sortir
        if off_x <= x <= off_x + self.image_sortir.get_width() and off_y <= y <= off_y + self.image_sortir.get_height():
            dispatcher.flag_finish = True

        return False

    # GameState
    def on_changed_state(self, old_state, new_state):
        self.set_state(new_state)

    def onPressedButton(self, buttonID, bChecked):
        bNeedUpdate = False
        if buttonID == ButtonID.ID_BUTTON_SOUND:
            bNeedUpdate = True
            dispatcher.session.soundsActive = bChecked
            v = dispatcher.session.volumeLevel - 0.1
            if v <= 0:
                v = 1
            pygame.mixer.music.set_volume(v)
            dispatcher.session.volumeLevel = v

        if buttonID == ButtonID.ID_BUTTON_CHANSON:
            bNeedUpdate = True
            dispatcher.session.chansonActive = bChecked

        print(f'button {buttonID} : check={bChecked}')
        if bNeedUpdate:
            dispatcher.need_update(self)
