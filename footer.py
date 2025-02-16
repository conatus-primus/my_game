# подвал игрового поля
from block import Block
from py.button import *


class ButtonID(enum.Enum):
    # переключение звуков
    ID_BUTTON_SOUND = 1005
    # переключение фоновой музыки
    ID_BUTTON_CHANSON = 1006


class Footer(Block):
    def __init__(self, game, machine):
        super().__init__(game, WIDTH_GAME, HEIGHT_FOOTER)
        self.state = GameState.GAME_NO
        self.offset_y = 0
        self.image_sortir = Dispatcher.load_image('images/system/sortir.png')
        self.offset_sortir = WIDTH_GAME - self.image_sortir.get_width(), (
                self.height - self.image_sortir.get_height()) // 2

        # ужас просто ужас напроектировала...
        temp = DrawnCheckButton(ButtonID.ID_BUTTON_SOUND, 'sound', self, (0, 0))

        self.button_sound = DrawnCheckButton(ButtonID.ID_BUTTON_SOUND, 'sound', self,
                                             (HEIGHT_FOOTER // 4, (HEIGHT_FOOTER - temp.get_height()) // 2), FON_COLOR_MID)
        self.button_chanson = DrawnCheckButton(ButtonID.ID_BUTTON_CHANSON, 'chanson', self,
                                               (HEIGHT_FOOTER // 2 + temp.get_width(),
                                               (HEIGHT_FOOTER - temp.get_height()) // 2), FON_COLOR_MID)
        del temp
        self.machine = machine
        if machine == MachineCollection:
            self.state = GameState.GAME_SELECT

    def load(self, map_number):
        self.button_sound.check(dispatcher.session.sounds_active)
        self.button_chanson.check(dispatcher.session.chanson_active)

        for id, dscr in self.machine.buttons.items():
            path, _, _ = dscr
            fullpath = 'images/system/states/' + path
            image = Dispatcher.load_image(fullpath)
            if image is None:
                LOG.write(f'Нижняя панель: ошибка загрузки {fullpath}')
                exit()
            self.machine.buttons[id] = path, image, None
            # загрузка - самое начало
        self.set_state(self.state)

    def set_state(self, state):
        LOG.write(f'Новое состояние игры {state}')
        # пересчитать положение кнопок
        if state not in self.machine.states.keys():
            self.state = GameState.GAME_NO
            return

        self.state = state

        if self.state == GameState.GAME_NO:
            return

        self.offset_y = 0
        width = 0
        for button_id in self.machine.states[self.state]:
            dscr_button = self.machine.buttons[button_id]
            path, image, _ = dscr_button
            if image is None:
                LOG.write(f'Нижняя панель: ошибка разбора {path}')
                exit()
            LOG.write(f'Загружаем в нижнюю панель: {path}')
            width += image.get_width()
            self.offset_y = (self.height - image.get_height()) // 2
        margin = (WIDTH_MAP - width) // (len(self.machine.states[self.state]) + 1)

        offset = WIDTH_MARGIN + margin
        self.offset = {}
        for button_id in self.machine.states[self.state]:
            dscr_button = self.machine.buttons[button_id]
            path, image, _ = dscr_button
            self.machine.buttons[button_id] = path, image, offset
            offset += image.get_width() + margin

    def render(self):
        if self.machine == MachineCollection:
            if self.state != GameState.GAME_SELECT:
                self.set_state(GameState.GAME_SELECT)

        pygame.draw.rect(self.surface, FON_COLOR_MID, (0, 0, self.width, self.height))

        for button_id in self.machine.states[self.state]:
            dscr_button = self.machine.buttons[button_id]
            _, image, offset_x = dscr_button
            self.surface.blit(image, (offset_x, self.offset_y))

        self.surface.blit(self.image_sortir, self.offset_sortir)

        self.button_sound.render()
        self.surface.blit(self.button_sound.surface, self.button_sound.offset)
        self.button_chanson.render()
        self.surface.blit(self.button_chanson.surface, self.button_chanson.offset)

    def on_click(self, pos):
        x, y = pos

        self.button_sound.on_click((x - self.button_sound.offset[0], y - self.button_sound.offset[1]))
        self.button_chanson.on_click((x - self.button_chanson.offset[0], y - self.button_chanson.offset[1]))

        for button_id in self.machine.states[self.state]:
            dscr_button = self.machine.buttons[button_id]
            _, image, offset_x = dscr_button
            if offset_x <= x <= image.get_width() + offset_x and self.offset_y <= y <= image.get_height() + self.offset_y:
                LOG.write(f'Нажато {button_id}')
                # сообщить об изменении состояния игры
                if button_id == ButtonState.SELECT_ID:
                    dispatcher.game.message(MessadgID.DEF_SELECT_GAME)
                else:
                    dispatcher.game.notify_about_change_state(button_id)
                    return True

        off_x, off_y = self.offset_sortir
        if off_x <= x <= off_x + self.image_sortir.get_width() and off_y <= y <= off_y + self.image_sortir.get_height():
            dispatcher.flag_finish = True

        return False

    # GameState
    def on_changed_state(self, old_state, new_state):
        self.set_state(new_state)

    def on_pressed_button(self, button_id, b_checked):
        b_need_update = False
        if button_id == ButtonID.ID_BUTTON_SOUND:
            b_need_update = True
            dispatcher.session.sounds_active = b_checked
            v = dispatcher.session.volume_level - 0.1
            if v <= 0:
                v = 1
            pygame.mixer.music.set_volume(v)
            dispatcher.session.volume_level = v

        if button_id == ButtonID.ID_BUTTON_CHANSON:
            b_need_update = True
            dispatcher.session.chanson_active = b_checked

        print(f'button {button_id} : check={b_checked}')
        if b_need_update:
            dispatcher.need_update(self)
