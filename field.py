# карта игрового поля
from block import Block
from vectormap import VectorMap
from location import Location
from py.amulet import *
from py.mob import *


class Field(Block):
    def __init__(self, game):
        super().__init__(game, WIDTH_MAP, HEIGHT_MAP)
        self.staticMap = None
        self.vectorMap = None
        self.location = None
        self.amulets = []
        self.amuletUser = None
        # данные для панелей пассивных амулетов
        self.strips: dict[str, list(Amulet)] = {}
        self.mob = None

    def load(self, map_number):

        self.mob = ChangedMob(self, 100, (0, 0), (900, 900), 'images/mobs/mob9_')
        self.mob.set_start()

        # грузим варианты уровней и движения клавиш
        self.location = Location(map_number)
        self.location.load()

        # грузим векторное описание
        self.vectorMap = VectorMap(map_number)
        self.vectorMap.load()

        # обработка статики в карте (фон + дырки + направляющие)
        self.staticMap = StaticMap(map_number)
        self.staticMap.load()

        # устанавливаем в векторную карту описание текущего уровня
        self.vectorMap.set_current_level_content(dispatcher.session.level_content,
                                                 dispatcher.session.selected_map.max_count_holes)

        # пользовательский амулет
        self.amuletUser = AmuletUser(self)
        # задаем все дырки
        self.amuletUser.load(self.vectorMap.holes + self.vectorMap.disabled_holes)
        # связываем амулет с локатором - изменится локатор - изменим и амулеты
        self.amuletUser.setLocation(self.location)
        self.amulets.append(self.amuletUser)

        amuletPassive = AmuletPassive(self, 'ruby.png', ['path1', 'path2'], SHOW_TIME_IN_HOLE_SEC)
        # self.amuletPassive = AmuletPassive(self, 'ruby.png', ['path5'], [2, 0.1])
        amuletPassive.load(self.vectorMap.holes)
        amuletPassive.start()
        self.amulets.append(amuletPassive)

        amuletPassive = AmuletPassive(self, 'sapphire.png', ['path2', 'path1'], SHOW_TIME_IN_HOLE_SEC)
        amuletPassive.load(self.vectorMap.holes)
        amuletPassive.start()
        self.amulets.append(amuletPassive)

        #
        dispatcher.needUpdate(self)

    def render(self):
        pygame.draw.rect(self.surface, pygame.Color('blue'), (0, 0, self.width, self.height))
        self.staticMap.render(self.surface)
        self.vectorMap.render(self.surface)

        # рисуем все амулеты
        for a in self.amulets:
            a.render(self.surface)

        # рисуем планки если они есть
        self.render_strips()

        # рисуем переходные состояния - они самые последние
        for a in self.amulets:
            a.render_last(self.surface)

        self.mob.render(self.surface)

    # вход - нажатые клавиши pygame.key.get_pressed()
    def onPressedKey(self, pressed_keys):
        # пересчитать положение амулетов
        if any([a.onPressedKey(pressed_keys) for a in self.amulets]):
            self.recalcAmuletRelativePosition()
            dispatcher.needUpdate(self)
            return True
        return False

    def update(self, sender):
        self.staticMap.set_brightness(dispatcher.session.brightness)
        for a in self.amulets:
            a.update()

    def onClick(self, pos):
        # пересчитать положение амулетов
        if any([a.onClick(pos) for a in self.amulets]):
            self.recalcAmuletRelativePosition()
            dispatcher.needUpdate(self)
            return True
        return False

    def onTimer(self, current_time):
        # пересчитать положение амулетов
        if any([a.onTimer(current_time) for a in self.amulets]):
            self.recalcAmuletRelativePosition()
            dispatcher.needUpdate(self)
            return True
        return False

    # пересчитать положение амулетов
    def recalcAmuletRelativePosition(self):
        # есть хотя бы один амулет гарантировано
        hole_position: list[tuple[str, int, Amulet]] = []
        for a in self.amulets:
            res = a.currentHole()
            if res is not None and res[0] != '':
                hole_position.append(res)

        # activeHoleID, startSecs, self
        # слепляем ключ для сортировки время, сдвинутое на 100 плюс номер дырки (номер точно меньше 100)
        hole_position = sorted(hole_position, key=lambda x: -(int(x[0].replace('path', '')) * 100 + x[1]))
        state = AmuletState.MONTRER_EN_ENTIER

        pos = dict()
        self.strips = {}
        for i, item in enumerate(hole_position):
            activeHoleID, _, amulet = item
            state = pos.get(activeHoleID)
            if state is None:
                amulet.setMontrerState(AmuletState.MONTRER_EN_ENTIER)
                pos[activeHoleID] = AmuletState.MONTRER_UNE_PARTIE
            else:
                amulet.setMontrerState(state)
                if state == AmuletState.MONTRER_UNE_PARTIE:
                    pos[activeHoleID] = AmuletState.NE_MONTRER_PAS
            # заполним данные для отрисовки панелей
            if activeHoleID not in self.strips.keys():
                self.strips[activeHoleID] = []
            self.strips[activeHoleID].append(amulet)

    # рисуем планки если они есть
    def render_strips(self):
        for hole_id, list_amulet in self.strips.items():
            if hole_id in self.vectorMap.strips:
                # координаты планки
                coords = self.vectorMap.strips[hole_id]

                if len(coords) <= 1:
                    continue
                if len(list_amulet) <= 1:
                    continue

                pos_start, pos_stop = coords[0], coords[-1]
                if pos_start[1] > pos_stop[1]:
                    pos_start, pos_stop = pos_stop, pos_start
                dx, dy = pos_stop[0] - pos_start[0], pos_stop[1] - pos_start[1]
                dist = (dx ** 2 + dy ** 2) ** 0.5
                if dist == 0:
                    dx, dy = 0, 0
                else:
                    dx, dy = Amulet.strip_max_length * dx / dist, Amulet.strip_max_length * dy / dist

                num = 0
                for i, a in enumerate(list_amulet):
                    point = pos_start[0] + num * dx, pos_start[1] + num * dy
                    a.render_strip(point, self.surface)
                    num += 1


class StaticMap:
    def __init__(self, map_number):
        # грузим фон
        self.path = CURRENT_DIRECTORY + '/maps/' + str(map_number) + '.png'
        # базовый фон
        self.image = pygame.image.load(self.path)
        # фон с яркостью
        self.brightenImage = pygame.image.load(self.path)
        # ставим яркость по умолчанию
        self.brightness = dispatcher.session.brightness
        self.set_brightness(self.brightness)
        self.image_test = pygame.image.load(CURRENT_DIRECTORY + '/images/nuage.png')

    def load(self):
        pass

    def set_brightness(self, brightness):
        self.brightness = brightness
        if self.brightness >= len(BRIGHTEN):
            self.brightness = 0
        bright_color = (BRIGHTEN[self.brightness], BRIGHTEN[self.brightness], BRIGHTEN[self.brightness])
        self.brightenImage = pygame.image.load(self.path)
        self.brightenImage.fill(bright_color, special_flags=pygame.BLEND_RGB_SUB)

    def render(self, surface):
        # рисуем фон
        surface.blit(self.brightenImage, (0, 0))
        surface.blit(self.image_test, (100, 350))
