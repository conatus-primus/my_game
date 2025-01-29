# подвал игрового поля
import pygame
from vars import *
from block import Block


class Footer(Block):
    def __init__(self, game, state):
        super().__init__(game, WIDTH_GAME, HEIGHT_FOOTER)
        self.state = state
        self.offset_y = 0

    def load(self, map_number):
        for id, dscr in Machine.buttons.items():
            path, _, _ = dscr
            fullpath = 'images/system/states/' + path
            image = Dispatcher.load_image(fullpath)
            if image is None:
                LOG.write('Нижняя панель: ошибка загрузки {fullpath}')
                exit()
            Machine.buttons[id] = path, image, None
            # загрузка - самое начало
        self.set_state(self.state)

    def set_state(self, state):
        self.state = state
        # пересчитать положение кнопок
        if self.state not in Machine.states.keys():
            self.state = GameState.GAME_NO
            return

        if self.state == GameState.GAME_NO:
            return

        self.offset_y = 0
        width = 0
        for button_id in Machine.states[self.state]:
            dscr_button = Machine.buttons[button_id]
            path, image, _ = dscr_button
            if image is None:
                LOG.write('Нижняя панель: ошибка разбора {path}')
                exit()
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
        pygame.draw.rect(self.surface, FON_COLOR_DARK, (0, 0, self.width, self.height))
        for button_id in Machine.states[self.state]:
            dscr_button = Machine.buttons[button_id]
            _, image, offset_x = dscr_button
            self.surface.blit(image, (offset_x, self.offset_y))

    def onClick(self, pos):
        x, y = pos

        for button_id in Machine.states[self.state]:
            dscr_button = Machine.buttons[button_id]
            path, image, offset_x = dscr_button
            if offset_x <= x <= image.get_width() + offset_x and self.offset_y <= y <= image.get_height() + self.offset_y:
                LOG.write(f'Нажато {button_id} {path}')
                # сообщить об изменении состояния игры
                dispatcher.game.notify_about_change_state(self.state, button_id)
                return True
        return False

    # GameState
    def on_changed_state(self, old_state, new_state):
        self.set_state(new_state)
