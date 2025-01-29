# подвал игрового поля
import pygame
from vars import *
from block import Block


class Footer(Block):
    def __init__(self, game):
        super().__init__(game, WIDTH_GAME, HEIGHT_FOOTER)
        self.state = GameState.GAME_NO
        self.offset_y = 0
        self.image_sortir = Dispatcher.load_image('images/system/sortir.png')
        self.offset_sortir = WIDTH_GAME - self.image_sortir.get_width(), (
                    self.height - self.image_sortir.get_height()) // 2

    def load(self, map_number):
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
        pygame.draw.rect(self.surface, FON_COLOR_DARK, (0, 0, self.width, self.height))
        for button_id in Machine.states[self.state]:
            dscr_button = Machine.buttons[button_id]
            _, image, offset_x = dscr_button
            self.surface.blit(image, (offset_x, self.offset_y))

        if self.state != GameState.GAME_NO:
            self.surface.blit(self.image_sortir, self.offset_sortir)

    def onClick(self, pos):
        x, y = pos

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
