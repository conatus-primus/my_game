import pygame
from vars import *
import configparser
import enum


class AmuletState(enum.Enum):
    # показывать полный амулет (амулет + основная рамка)
    MONTRER_EN_ENTIER = 1000
    # показать амулет частично (дополнительная рамка)
    MONTRER_UNE_PARTIE = 1001
    # не показывать амулет
    NE_MONTRER_PAS = 1002


class AmuletSprite(pygame.sprite.Sprite):
    def __init__(self, parent):
        pygame.sprite.Sprite.__init__(self)
        self.parent = parent
        self.active = False
        self.image = None
        self.id = None
        self.coords_hole = None
        self.centre = None
        self.contour = None

    def load(self, image, id, coords_hole, centre_hole, color):
        self.image = image
        self.id = id
        self.coords_hole = coords_hole
        self.centre = centre_hole
        self.color = color
        # ставим большой прямоугольник - нам надо столкновение моба именно с площадным объектом
        self.rect = OVERALL_RECT(coords_hole)
        self.contour = OVERALL_CONTOUR(coords_hole, 10)

        r, g, b = self.color.r, self.color.g, self.color.b

        self.pens = [

            (pygame.Color(r * 3 // 15, g * 3 // 15, b * 3 // 15), 9),
            (pygame.Color(r * 7 // 15, g * 7 // 15, b * 7 // 15), 7),
            (pygame.Color(r * 11 // 15, g * 11 // 15, b * 11 // 15), 5),
            (pygame.Color(r * 15 // 15, g * 15 // 15, b * 15 // 15), 3),
            (pygame.Color(255, 255, 255), 1)
        ]

    def isPointInHole(self, pos):
        return self.rect.collidepoint(pos)

    def update(self, currentHoleID):
        self.active = True if currentHoleID == self.id else False

    def render(self, surface, montrerState):
        if not self.active:
            return

        if montrerState == AmuletState.NE_MONTRER_PAS:
            return

        # сам амулет
        if montrerState == AmuletState.MONTRER_EN_ENTIER:
            surface.blit(self.image,
                         (self.centre[0] - self.image.get_width() // 2, self.centre[1] - self.image.get_height() // 2))

            for i, pen in enumerate(self.pens):
                color, h = pen
                for point in self.coords_hole:
                    pygame.draw.circle(surface, color, point, h // 2, h // 2)
                # дырка
                pygame.draw.lines(surface, color, True, self.coords_hole, h)

        # дырка
        if montrerState == AmuletState.MONTRER_UNE_PARTIE:

            for i, pen in enumerate(self.pens):
                color, h = pen
                for point in self.contour:
                    pygame.draw.circle(surface, color, point, h // 2, h // 2)
                pygame.draw.lines(surface, color, True, self.contour, h)


# базовый класс для поддержки амулетов
class Amulet:
    def __init__(self, amuletName, parent):
        self.parent = parent
        self.location = None
        # грузим картинку для амулета
        self.image = self.load_image(amuletName)
        LOG.write(f'Load amulet {amuletName}')
        # грузим пользовательский цвет для амулета
        config = configparser.ConfigParser()
        config.read(CURRENT_DIRECTORY + '/data/amulets.ini')
        if amuletName in config and 'color' in config[amuletName]:
            r, g, b = config[amuletName]['color'].split(',')
            self.color = pygame.Color(int(r), int(g), int(b))
        else:
            self.color = self.image.get_at((self.image.get_width() // 2, self.image.get_height() // 2))
        # список амулетов
        self.amuletSprites = []
        self.activeHoleID = 'path1'
        self.montrerState = AmuletState.MONTRER_EN_ENTIER

    def load_image(self, name):
        # TODO сделать нормальную обработку
        image = pygame.image.load(os.path.join(CURRENT_DIRECTORY, 'images/amulets', name))
        image.set_colorkey(image.get_at((0, 0)))
        return image

    # создаем спрайты, одна дырка - один спрайт
    def load(self, vMapHoles):
        for hole in vMapHoles:
            self.amuletSprites.append(AmuletSprite(self))
            self.amuletSprites[-1].load(self.image, hole.id, hole.coords_hole, hole.centre_hole, self.color)

    # связываем амулет с локатором - изменится локатор - изменим и амулеты
    def setLocation(self, location):
        self.location = location

    def render(self, surface):
        for a in self.amuletSprites:
            a.render(surface, self.montrerState)

    def onClick(self, pos):
        return False

    # вход - нажатые клавиши pygame.key.get_pressed()
    def onPressedKey(self, pressed_keys):
        return False

    def onTimer(self, currentTime):
        return False

    def setMontrerState(self, montrerState):
        self.montrerState = montrerState


# пользовательский амулет - управление с клавиатуры
class AmuletUser(Amulet):
    def __init__(self, parent):
        super().__init__('amber.png', parent)

    # обновляем настройку отображения спрайтов в зависимости от текущей дырки
    def update(self):
        for a in self.amuletSprites:
            a.update(self.activeHoleID)

    def onClick(self, pos):
        # меняем положение пользовательского амулета
        # пока так, потом возможно нужен режим,
        # или клик для амулета пользователя или клик для пассивного/активного амулета
        # может еще что-то
        clickedAmulet = None
        for a in self.amuletSprites:
            if a.isPointInHole(pos):
                clickedAmulet = a
                break

        if clickedAmulet is not None:
            self.location.currentHoleID = clickedAmulet.id
            self.activeHoleID = clickedAmulet.id
            dispatcher.needUpdate(self)
            return True

        return False

    # вход - нажатые клавиши pygame.key.get_pressed()
    def onPressedKey(self, pressed_keys):
        # self.location.onPressedKey(pressed_keys)
        # self.activeHoleID = self.location.currentHoleID
        oldActiveHoleID = self.activeHoleID
        self.activeHoleID = self.location.onPressedKey(pressed_keys, self.activeHoleID)
        if self.activeHoleID != oldActiveHoleID:
            dispatcher.needUpdate(self)
            return True
        return False

    # дырка, чтобы разобраться в порядке отображения когда несколько амулетов стоят на одной дырке
    def currentHole(self):
        return self.activeHoleID, time.time(), self


# пассивный амулет - назначается пользователем на несколько дыр (2 и больше)
# стоит на дырке заданное время Т1
# потом исчезает на заданное время Т2
# далее переходит на следующую дырку
class AmuletPassive(Amulet):
    def __init__(self, parent, amuletName, listHolesID, intervals):
        super().__init__(amuletName, parent)
        # список дырок назначенных для амулета
        self.listHolesID = listHolesID
        self.intervals = intervals if intervals is not None and len(intervals) == 2 else [5, 1]
        self.currentInterval = 99999999999

        # разметим показ амулета по дыркам
        self.rules = []
        # задаем правила по которым показываем и прячем амулеты по дыркам
        if len(listHolesID) == 1:
            self.rules.append((listHolesID[0], intervals[0], intervals[0]))
            self.rules.append(('', intervals[1], intervals[0]))
        else:
            for holeID in listHolesID:
                self.rules.append((holeID, intervals[0], intervals[0]))

        self.startTime = None

    def start(self):
        self.startTime = time.time()
        newActiveHoleID, newSampleInterval, _ = self.rules[0]
        self.rules[0] = newActiveHoleID, newSampleInterval, self.startTime

    def stop(self):
        pass

    # обновляем настройку отображения спрайтов в зависимости от текущей дырки
    def update(self):
        if self.startTime is None:
            return

        activeHoleID, _, _ = self.rules[0]
        for a in self.amuletSprites:
            a.update(activeHoleID)

    def onClick(self, pos):
        return False

    # таймер на передвижение амулетов
    def onTimer(self, currentTime):
        # print(f'{self.__class__.__name__}.{__name__} {currentTime}')

        if self.startTime is None:
            return False

        activeHoleID, sampleInterval, startSecs = self.rules[0]
        dT = currentTime - startSecs
        # print(f'dT={dT} {activeHoleID}, {sampleInterval}, {startSecs}')

        if dT < sampleInterval:
            # оставляем эту дырку
            return False
        else:
            # двигаемся дальше
            # первый элемент передвигаем в конец
            self.rules.append((activeHoleID, sampleInterval, 0))
            # отсекаем его из начала
            self.rules = self.rules[1:]
            # корректируем новый первый - ставим текущее время
            newActiveHoleID, newSampleInterval, _ = self.rules[0]
            self.rules[0] = newActiveHoleID, newSampleInterval, currentTime
            dispatcher.needUpdate(self)
            return True

    # дырка, чтобы разобраться в порядке отображения когда несколько амулетов стоят на одной дырке
    def currentHole(self):
        if self.startTime is None:
            return None
        activeHoleID, _, startSecs = self.rules[0]
        return activeHoleID, startSecs, self

    def load(self, vMapHoles):
        super().load(vMapHoles)
