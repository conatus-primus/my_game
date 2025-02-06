# правый блоки игрового поля
import copy

from py.button import *
from py.bright_panel import *
from block import Block
from py.panel import ImagePanel
from py.biblio import MapDscr
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

        self.level_panel = None
        self.current_map = MapDscr('так надо это пустая карта')

    def load(self, session):
        self.buttonSound.check(dispatcher.session.soundsActive)
        self.buttonChanson.check(dispatcher.session.chansonActive)

    def render(self):
        pygame.draw.rect(self.surface, FON_COLOR_MID, (0, 0, self.width, self.height))
        pygame.draw.rect(self.surface, FON_COLOR, (5, 0, self.width, self.height))
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

        if dispatcher.game.state is None or dispatcher.game.state == GameState.GAME_NO:
            # мы в коллекции
            if dispatcher.game is not None and dispatcher.game.collection is not None:
                map = dispatcher.game.collection.biblio.get_clicked_map()

                if map is not None:

                    # ищем карту в профиле пользователя, чтобы отобразить статистику
                    round, points, p_original = dispatcher.user.get_map_data(map.map_number)
                    percents = copy.deepcopy(p_original)
                    level_count_in_map = map.get_level_count()

                    if self.level_panel == None or map.map_number != self.current_map.map_number:
                        self.level_panel = None
                        self.level_panel = ImagePanel(self, FON_COLOR)
                        self.level_panel.load('images/system/level_horz.png', 'images/system/level_horz_disable.png',
                                              (30, 30),
                                              level_count_in_map)
                        self.level_panel.set_enabled_count(level_count_in_map)
                        print(f'всего уровней {level_count_in_map} отработали {len(percents)}')

                    self.current_map = map

                    # TODO сделать по-человечески
                    # да, я знаю, выглядит страшненько, подбор, увы. подбор, потом оптимизируем
                    font = pygame.font.SysFont('Comic Sans MS', 24)

                    offset_y = 200
                    font.set_bold(False)
                    text = font.render(f'Дом № {map.map_number}', True, (0, 0, 0))
                    self.surface.blit(text, ((self.width - text.get_width()) / 2, offset_y))

                    if points != 0:
                        offset_y += text.get_height()
                        font.set_bold(False)
                        text = font.render(f'Очки опыта', True, (0, 0, 0))
                        self.surface.blit(text, ((self.width - text.get_width()) / 2, offset_y))

                        offset_y += text.get_height()
                        font.set_bold(True)
                        text = font.render(f'{points}', True, (0, 0, 0))
                        self.surface.blit(text, ((self.width - text.get_width()) / 2, offset_y))

                    if round != 0:
                        offset_y += text.get_height()
                        font.set_bold(False)
                        text = font.render(f'Проведено игр', True, (0, 0, 0))
                        self.surface.blit(text, ((self.width - text.get_width()) / 2, offset_y))

                        offset_y += text.get_height()
                        font.set_bold(True)
                        text = font.render(f'{round}', True, (0, 0, 0))
                        self.surface.blit(text, ((self.width - text.get_width()) / 2, offset_y))

                    offset_y += 2 * text.get_height()
                    font.set_bold(False)
                    text = font.render(f'Игра сейчас', True, (0, 0, 0))
                    self.surface.blit(text, ((self.width - text.get_width()) / 2, offset_y))

                    font = pygame.font.SysFont('Comic Sans MS', 16)
                    offset_y += text.get_height()
                    if len(percents) < level_count_in_map:
                        percents += [0] * (level_count_in_map - len(percents))
                    warning = False

                    # посчитаем смещение влево берем шаблонную строку
                    text = font.render(f'Щ уровень: не пройден', True, (0, 0, 0))
                    dx = (self.width - text.get_width()) // 2

                    for i, p in enumerate(percents):
                        if p == 0:
                            if warning is not True:
                                font.set_bold(True)
                                text = font.render(f'Вы здесь', True, (0, 0, 0))
                                self.surface.blit(text, ((self.width - text.get_width()) / 2, offset_y))
                                offset_y += text.get_height()
                                warning = True
                                font.set_bold(False)

                            text = font.render(f'{i + 1} уровень не пройден', True, (0, 0, 0))
                        else:
                            text = font.render(f'{i + 1} уровень {p}% монстров', True, (0, 0, 0))
                        self.surface.blit(text, (dx, offset_y))
                        offset_y += text.get_height()

                    offset_y += text.get_height()
                    self.level_panel.render(self.surface, ((self.width - self.level_panel.width) // 2, offset_y))

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
            dispatcher.needUpdate(self)

