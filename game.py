# игровое поле
import pygame
from header import Header
from footer import Footer
from marginleft import MarginLeft
from marginright import MarginRight
from field import Field
from vars import *
from py.shared import *
from collection import *
from py.user import *
from footer import *
from py.logica import *
from collection import *


class Game:
    def __init__(self):
        # self.field = None
        # игровой блок и смещение блока относительно всего игрового поля
        self.block = None
        # для выхода из логина
        self.start = False
        self.block_collect = None
        self.block_game = None
        self.user = None
        self.state = None

    def load(self):
        # к этому моменту уже известен пользователь
        # self.field = Field(self)
        self.collection = Collection(self)

        # игровой блок и смещение блока относительно всего игрового поля
        self.block_game = [(Field(self), (WIDTH_MARGIN, HEIGHT_HEADER)),
                           (Header(self), (0, 0)),
                           (Footer(self), (0, HEIGHT_HEADER + HEIGHT_MAP)),
                           (MarginLeft(self), (0, HEIGHT_HEADER)),
                           (MarginRight(self), (WIDTH_MARGIN + WIDTH_MAP, HEIGHT_HEADER)),
                           ]

        self.block_collect = [(self.collection, (WIDTH_MARGIN, HEIGHT_HEADER)),
                              (Header(self), (0, 0)),
                              (Footer(self), (0, HEIGHT_HEADER + HEIGHT_MAP)),
                              (MarginLeft(self), (0, HEIGHT_HEADER)),
                              (MarginRight(self), (WIDTH_MARGIN + WIDTH_MAP, HEIGHT_HEADER)),
                              ]

        # self.block = self.block_game
        self.block = self.block_collect

        for item in self.block:
            obj, _ = item
            obj.load(dispatcher.session.map_number)

        self.game = GameState.GAME_NO
        for item in self.block:
            obj, _ = item
            obj.on_changed_state(None, self.game)

        # фоновая музыка
        pygame.mixer.music.play(-1)
        if not dispatcher.session.chansonActive:
            pygame.mixer.music.pause()

        # громкость
        pygame.mixer.music.set_volume(dispatcher.session.volumeLevel)

    def render(self, screen):
        if self.block is None:
            return

        screen.fill(pygame.Color('white'))

        for item in self.block:
            obj, offset = item
            # отрисовали на своей поверхности
            obj.render()
            # копируем на общую поверхность
            screen.blit(obj.surface, offset)

    def isSession(self):
        return True

    # sender - кто инициировал обновление
    def need_update(self, sender):
        if self.block is None:
            return

        # переключаем звук и музыку
        if dispatcher.session.chansonActive:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()
        # print(f'volume={pygame.mixer.music.get_volume()}')

        for item in self.block:
            obj, offset = item
            obj.update(sender)

    # вход - нажатые клавиши pygame.key.get_pressed()
    def on_pressed_key(self, pressed_keys):
        if self.block is None:
            return

        if self.state == GameState.GAME_WAIT:
            # эмулируем клик на /начать/
            if pressed_keys[pygame.K_RETURN]:
                dispatcher.game.notify_about_change_state(ButtonState.PLAY_ID)

        elif self.state == GameState.GAME_PLAY:
            if pressed_keys[pygame.K_SPACE]:
                dispatcher.game.notify_about_change_state(ButtonState.PAUSE_ID)
            # не выходим мы в состоянии игры  надо еще амулет подвигать

        elif self.state == GameState.GAME_PAUSE:
            # стоим на паузе надо продолжить эмулируем клик на продолжить
            if pressed_keys[pygame.K_SPACE]:
                dispatcher.game.notify_about_change_state(ButtonState.CONTINUE_ID)
            # не выходим мы на паузе пусть приноровится двигать клавишами

        elif self.state == GameState.GAME_OVER:
            if pressed_keys[pygame.K_ESCAPE]:
                dispatcher.game.notify_about_change_state(ButtonState.RETURN_ID)
            # не выходим мы на паузе пусть приноровится двигать клавишами

        for item in self.block:
            obj, offset = item
            obj.onPressedKey(pressed_keys)

    def onClick(self, pos):
        if self.block is None:
            return

        x, y = pos
        for item in self.block:
            obj, offset = item
            blockPos = x - offset[0], y - offset[1]
            obj.onClick(blockPos)

    def on_timer(self, currentTime):
        if self.block is None:
            return

        for item in self.block:
            obj, offset = item
            obj.on_timer(currentTime)

    def on_click_extend(self, event):
        if self.block is None:
            return

        e = event
        x, y = e.pos

        for item in self.block:
            obj, offset = item
            e.pos = x - offset[0], y - offset[1]
            obj.on_click_extend(e)

    # двойной клик на коллекции - выбор новой карты
    def on_double_click(self, event):
        if self.block is None:
            return False
        e = event
        x, y = e.pos

        for item in self.block:
            obj, offset = item
            e.pos = x - offset[0], y - offset[1]

            if obj.on_double_click(e) is True and obj.__class__.__name__ == 'Collection':
                # выходим из коллекции и устанавливаем выбранную карту
                LOG.write(
                    f'Сейчас будет загрузка карта {dispatcher.session.map_number} для {dispatcher.session.user}')

                self.block = self.block_game
                for item in self.block:
                    obj, _ = item
                    obj.load(dispatcher.session.map_number)

                # эмулируем нажатие клавиши играть заново
                self.notify_about_change_state(ButtonState.REPLAY_ID)
                return True

        return False

    # завершаем игру
    def on_stop(self):
        pass

    #
    def __change_state__(self, old_state):
        for item in self.block:
            obj, _ = item
            obj.on_changed_state(old_state, self.state)

    # сообщение об изменении состояния игры
    def notify_about_change_state(self, button_id):
        # вернуться в коллекцию
        if ButtonState.HOUSE_ID == button_id:

            if dispatcher.session.logica:
                del dispatcher.session.logica
                dispatcher.session.logica = None

            self.block = self.block_collect

            del self.block_game
            self.block_game = [(Field(self), (WIDTH_MARGIN, HEIGHT_HEADER)),
                               (Header(self), (0, 0)),
                               (Footer(self), (0, HEIGHT_HEADER + HEIGHT_MAP)),
                               (MarginLeft(self), (0, HEIGHT_HEADER)),
                               (MarginRight(self), (WIDTH_MARGIN + WIDTH_MAP, HEIGHT_HEADER)),
                               ]
            old_state, self.state = self.state, GameState.GAME_NO
            self.__change_state__(old_state)
            return

        # играем
        elif ButtonState.PLAY_ID == button_id:
            old_state, self.state = self.state, GameState.GAME_PLAY
            self.__change_state__(old_state)
            self.game_start()

        # пауза
        elif ButtonState.PAUSE_ID == button_id:
            old_state, self.state = self.state, GameState.GAME_PAUSE
            self.__change_state__(old_state)
            self.game_pause()

        # продолжить игру после паузы
        elif ButtonState.CONTINUE_ID == button_id:
            old_state, self.state = self.state, GameState.GAME_PLAY
            self.__change_state__(old_state)
            self.game_continue()

        # начать играть заново
        elif ButtonState.REPLAY_ID == button_id:
            old_state, self.state = self.state, GameState.GAME_WAIT
            self.__change_state__(old_state)
            self.game_replay()

        # была заставка после окончания раунда надо войти в состояние ожидания начала игры
        elif ButtonState.RETURN_ID == button_id:

            # вот здесь будем обновлять уровень
            dispatcher.session.level_content = dispatcher.session.selected_map.generate_next_level()
            dispatcher.need_update(self)

            old_state, self.state = self.state, GameState.GAME_WAIT
            self.__change_state__(old_state)
            self.game_replay()

    # действия связанные с началом игры
    def game_start(self):
        if dispatcher.session.logica:
            del dispatcher.session.logica
            dispatcher.session.logica = None

        dispatcher.session.logica = Logica(self)
        dispatcher.logicaaa().game_start()
        for item in self.block:
            obj, _ = item
            obj.game_start()

    # встали на паузу
    def game_pause(self):
        if dispatcher.logicaaa() is not None:
            dispatcher.logicaaa().game_pause()

        for item in self.block:
            obj, _ = item
            obj.game_pause()

    # продолжить игру после паузы
    def game_continue(self):
        if dispatcher.logicaaa() is not None:
            dispatcher.logicaaa().game_continue()

        for item in self.block:
            obj, _ = item
            obj.game_continue()

    # начать играть заново
    def game_replay(self):
        if dispatcher.logicaaa():
            del dispatcher.session.logica
            dispatcher.session.logica = None

        for item in self.block:
            obj, _ = item
            obj.game_replay()

    # закончилась игра
    def game_over(self, flag_success):
        old_state, self.state = self.state, GameState.GAME_OVER
        self.__change_state__(old_state)

        for item in self.block:
            obj, _ = item
            obj.game_over(flag_success)
