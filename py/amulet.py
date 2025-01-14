import pygame
from vars import *
import configparser


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
        self.contour = OVERALL_CONTOUR(coords_hole, 11)
        self.contour2 = OVERALL_CONTOUR(coords_hole, 21)

        r, g, b = self.color.r, self.color.g, self.color.b

        self.pens = [

            (pygame.Color(r * 3 // 15, g * 3 // 15, b * 3 // 15), 9),
            (pygame.Color(r * 7 // 15, g * 7 // 15, b * 7 // 15), 7),
            (pygame.Color(r * 11 // 15, g * 11 // 15, b * 11 // 15), 5),
            (pygame.Color(r * 15 // 15, g * 15 // 15, b * 15 // 15), 3),
            (pygame.Color(255, 255, 255), 1)
        ]

        self.pens2 = [
            (pygame.Color(0, 0, 0), 17),
            (pygame.Color(255, 255, 255), 13),
        ]

        # r, g, b = 207, 101, 0
        # self.pens2 = [
        #     (pygame.Color(r * 3 // 15, g * 3 // 15, b * 3 // 15), 9),
        #     (pygame.Color(r * 7 // 15, g * 7 // 15, b * 7 // 15), 7),
        #     (pygame.Color(r * 11 // 15, g * 11 // 15, b * 11 // 15), 5),
        #     (pygame.Color(r * 15 // 15, g * 15 // 15, b * 15 // 15), 3),
        #     (pygame.Color(255, 255, 255), 1)
        # ]

    def isPointInHole(self, pos):
        return self.rect.collidepoint(pos)

    def update(self, currentHoleID):
        self.active = True if currentHoleID == self.id else False

    def render(self, surface):
        if not self.active:
            return
        # сам амулет
        surface.blit(self.image,
                     (self.centre[0] - self.image.get_width() // 2, self.centre[1] - self.image.get_height() // 2))
        # дырка
        for i, pen in enumerate(self.pens2):
            color, h = pen
            for point in self.coords_hole:
                pygame.draw.circle(surface, color, point, h // 2, h // 2)
            # дырка
            pygame.draw.lines(surface, color, True, self.coords_hole, h)

        for i, pen in enumerate(self.pens):
            color, h = pen
            for point in self.coords_hole:
                pygame.draw.circle(surface, color, point, h // 2, h // 2)
            # дырка
            pygame.draw.lines(surface, color, True, self.coords_hole, h)

        # for i, pen in enumerate(self.pens2):
        #     color, h = self.pens2[i]
        #     for point in self.contour:
        #         pygame.draw.circle(surface, color, point, h // 2, h // 2)
        #     pygame.draw.lines(surface, color, True, self.contour, h)
        #
        #     # color, h = self.pens2[i]
        #     # for point in self.contour2:
        #     #     pygame.draw.circle(surface, color, point, h // 2, h // 2)
        #     # pygame.draw.lines(surface, color, True, self.contour2, h)
        #
        #     pass


# базовый класс для поддержки амулетов
class Amulet:
    def __init__(self, amuletName, parent):
        self.parent = parent
        self.location = None
        # грузим картинку для амулета
        self.image = self.load_image(amuletName)
        # грузим пользовательский цвет для амулета
        config = configparser.ConfigParser()
        config.read(CURRENT_DIRECTORY + '/data/amulets.ini')
        if amuletName in config and 'color' in config[amuletName]:
            r, g, b = config[amuletName]['color'].split(',')
            self.color = pygame.Color(int(r), int(g), int(b))
        else:
            self.color = self.image.get_at((self.image.get_width() // 2, self.image.get_height() // 2))
        # список амулетов
        # не делаем группу у нас необычные спрайты с поли линией
        self.amuletSprites = []
        self.activeHoleID = 'path1'

    def load_image(self, name):
        # TODO сделать нормальную обработку
        image = pygame.image.load(os.path.join(CURRENT_DIRECTORY, 'images/amulets', name))
        image.set_colorkey(image.get_at((0, 0)))
        return image

    # создаем спрайты, одна дырка - один спрайт
    def load(self, vectorMapHoles):
        for hole in vectorMapHoles:
            self.amuletSprites.append(AmuletSprite(self))
            self.amuletSprites[-1].load(self.image, hole.id, hole.coords_hole, hole.centre_hole, self.color)

    # связываем амулет с локатором - изменится локатор - изменим и амулеты
    def setLocation(self, location):
        self.location = location

    def render(self, surface):
        for a in self.amuletSprites:
            a.render(surface)

    def onClick(self, pos):
        pass

    # вход - нажатые клавиши pygame.key.get_pressed()
    def onPressed(self, pressed_keys):
        pass


# пользовательский амулет - управление с клавиатуры
class AmuletUser(Amulet):
    def __init__(self, parent):
        super().__init__('amethyst.png', parent)

    # обновляем настройку отображения спрайтов в зависимости от текущей дырки
    def update(self):
        for a in self.amuletSprites:
            a.update(self.location.currentHoleID)

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
    def onPressed(self, pressed_keys):
        self.location.onPressedKey(pressed_keys)
        self.activeHoleID = self.location.currentHoleID
        dispatcher.needUpdate(self)


# пассивный амулет - назначается пользователем на несколько дыр (2 и больше)
# стоит на дырке заданное время Т1
# потом исчезает на заданное время Т2
# далее переходит на следующую дырку
class AmuletPassive(Amulet):
    def __init__(self, parent, amuletName, listHolesID, intervals):
        super().__init__(amuletName, parent)
        self.listHolesID = listHolesID
        self.intervals = intervals

    def start(self):
        pass

    def stop(self):
        pass

    # обновляем настройку отображения спрайтов в зависимости от текущей дырки
    def update(self):
        for a in self.amuletSprites:
            a.update(self.location.currentHoleID)

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
    def onPressed(self, pressed_keys):
        self.location.onPressedKey(pressed_keys)
        self.activeHoleID = self.location.currentHoleID
        dispatcher.needUpdate(self)
