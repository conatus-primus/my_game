# карта игрового поля
import pygame
import copy
from vars import *
from block import Block
from vectormap import VectorMap
from location import Location
from py.amulet import *


class Field(Block):
    def __init__(self, game):
        super().__init__(game, WIDTH_MAP, HEIGHT_MAP)
        self.staticMap = None
        self.vectorMap = None
        self.location = None
        self.amulets = []

    def load(self, map_number):
        # грузим варианты уровней и движения клавиш
        self.location = Location(map_number)
        self.location.load()

        # грузим векторное описание
        self.vectorMap = VectorMap(map_number)
        self.vectorMap.load()

        # обработка статики в карте (фон + дырки + направляющие)
        self.staticMap = StaticMap(map_number, self.game.session)
        self.staticMap.load()

        # установить выбранный уровень
        self.location.setLevelID(self.game.session.currentLevelID)
        # установить текущую дырку
        self.location.setHoleID(self.game.session.currentHoleID)
        # устанавливаем в векторную карту описание текущего уровня
        self.vectorMap.setCurrentLevelContent(self.location.currentLevelContent())

        # пользовательский амулет
        self.amuletUser = AmuletUser(self)
        # задаем все дырки
        self.amuletUser.load(self.vectorMap.holes)
        # связываем амулет с локатором - изменится локатор - изменим и амулеты
        self.amuletUser.setLocation(self.location)
        self.amulets.append(self.amuletUser)

        amuletPassive = AmuletPassive(self, 'ruby.png', ['path2', 'path3'], [2, 0.1])
        # self.amuletPassive = AmuletPassive(self, 'ruby.png', ['path5'], [2, 0.1])
        amuletPassive.load(self.vectorMap.holes)
        amuletPassive.start()
        self.amulets.append(amuletPassive)

        amuletPassive = AmuletPassive(self, 'sapphire.png', ['path5', 'path4'], [2, 0.1])
        amuletPassive.load(self.vectorMap.holes)
        amuletPassive.start()
        self.amulets.append(amuletPassive)

        #
        dispatcher.needUpdate(self)

    def render(self):
        pygame.draw.rect(self.surface, pygame.Color('blue'), (0, 0, self.width, self.height))
        self.staticMap.render(self.surface)
        self.vectorMap.render(self.surface)

        for a in self.amulets:
            a.render(self.surface)

    # вход - нажатые клавиши pygame.key.get_pressed()
    def onPressedKey(self, pressed_keys):
        # пересчитать положение амулетов
        if any([a.onPressedKey(pressed_keys) for a in self.amulets]):
            self.recalcAmuletRelativePosition()
            dispatcher.needUpdate(self)
            return True
        return False

    def update(self, sender):
        self.staticMap.setBrightness(self.game.session.brightness)
        for a in self.amulets:
            a.update()

    def onClick(self, pos):
        # пересчитать положение амулетов
        if any([a.onClick(pos) for a in self.amulets]):
            self.recalcAmuletRelativePosition()
            dispatcher.needUpdate(self)
            return True
        return False

    def onTimer(self, currentTime):
        # пересчитать положение амулетов
        if any([a.onTimer(currentTime) for a in self.amulets]):
            self.recalcAmuletRelativePosition()
            dispatcher.needUpdate(self)
            return True
        return False

    # пересчитать положение амулетов
    def recalcAmuletRelativePosition(self):
        # есть хотя бы один амулет гарантировано
        holePosition = []
        for a in self.amulets:
            res = a.currentHole()
            if res is not None and res[0] != '':
                holePosition.append(res)

        # activeHoleID, startSecs, self
        # слепляем ключ для сортировки время, сдвинутое на 100 плюс номер дырки (номер точно меньше 100)
        holePosition = sorted(holePosition, key=lambda x: -(int(x[0].replace('path', '')) * 100 + x[1]))
        state = AmuletState.MONTRER_EN_ENTIER

        pos = dict()
        for i, item in enumerate(holePosition):
            activeHoleID, _, amulet = item
            state = pos.get(activeHoleID)
            if state is None:
                amulet.setMontrerState(AmuletState.MONTRER_EN_ENTIER)
                pos[activeHoleID] = AmuletState.MONTRER_UNE_PARTIE
            else:
                amulet.setMontrerState(state)
                if state == AmuletState.MONTRER_UNE_PARTIE:
                    pos[activeHoleID] = AmuletState.NE_MONTRER_PAS


class StaticMap:
    def __init__(self, map_number, session):
        # грузим фон
        self.path = CURRENT_DIRECTORY + '/maps/' + str(map_number) + '.png'
        # базовый фон
        self.image = pygame.image.load(self.path)
        # фон с яркостью
        self.brightenImage = pygame.image.load(self.path)
        # ставим яркость по умолчанию
        self.brightness = session.brightness
        self.setBrightness(self.brightness)
        self.image_test = pygame.image.load(CURRENT_DIRECTORY + '/images/nuage.png')

    def load(self):
        pass

    def setBrightness(self, brightness):
        self.brightness = brightness
        if self.brightness >= len(BRIGHTEN):
            self.brightness = 0
        brightColor = (BRIGHTEN[self.brightness], BRIGHTEN[self.brightness], BRIGHTEN[self.brightness])
        self.brightenImage = pygame.image.load(self.path)
        self.brightenImage.fill(brightColor, special_flags=pygame.BLEND_RGB_SUB)

    def render(self, surface):
        # рисуем фон
        surface.blit(self.brightenImage, (0, 0))
        surface.blit(self.image_test, (100, 350))
