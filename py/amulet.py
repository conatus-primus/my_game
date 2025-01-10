import pygame
from vars import *
import configparser


class AmuletSprite(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.active = False
        self.image = None
        self.id = None
        self.coords_hole = None
        self.centre = None

    def load(self, image, id, coords_hole, centre_hole, color):
        self.image = image
        self.id = id
        self.coords_hole = coords_hole
        self.centre = centre_hole
        self.color = color
        self.rect = image.get_rect()
        self.rect.x = self.centre[0] - image.get_width() // 2
        self.rect.y = self.centre[1] - image.get_height() // 2

        r, g, b = self.color.r, self.color.g, self.color.b

        self.pens = [
            (pygame.Color(r * 3 // 15, g * 3 // 15, b * 3 // 15), 9),
            (pygame.Color(r * 7 // 15, g * 7 // 15, b * 7 // 15), 7),
            (pygame.Color(r * 11 // 15, g * 11 // 15, b * 11 // 15), 5),
            (pygame.Color(r * 15 // 15, g * 15 // 15, b * 15 // 15), 3),
            (pygame.Color(255, 255, 255), 1)
        ]

    def update(self, currentHoleID):
        self.active = True if currentHoleID == self.id else False

    def render(self, surface):
        if not self.active:
            return
        # сам амулет
        surface.blit(self.image, (self.rect.x, self.rect.y))
        # дырка
        for pen in self.pens:
            color, h = pen
            for point in self.coords_hole:
                pygame.draw.circle(surface, color, point, h // 2, h // 2)
            # дырка
            pygame.draw.lines(surface, color, True, self.coords_hole, h)


# базовый класс для поддержки амулетов
class Amulet:
    def __init__(self, amuletName):
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
        self.amulets = []

    def load_image(self, name):
        # TODO сделать нормальную обработку
        #image = pygame.image.load(os.path.join(CURRENT_DIRECTORY, 'images/amulets', name))
        image = pygame.image.load('D:/YL/my_game/images/mobs/mob3_1.png')
        image.set_colorkey(image.get_at((0, 0)))
        return image

    # создаем спрайты : одна дырка - один спрайт
    def load(self, vectorMapHoles):
        for hole in vectorMapHoles:
            self.amulets.append(AmuletSprite())
            self.amulets[-1].load(self.image, hole.id, hole.coords_hole, hole.centre_hole, self.color)

    # связываем амулет с локатором - изменится локатор - изменим и амулеты
    def setLocation(self, location):
        self.location = location

    def render(self, surface):
        for a in self.amulets:
            a.render(surface)


# пользовательский амулет - управление с клавиатуры
class AmuletUser(Amulet):
    def __init__(self):
        super().__init__('amethyst.png')

    # обновляем настройку отображения спрайтов в зависимости от текущей дырки
    def update(self):
        for a in self.amulets:
            a.update(self.location.currentHoleID)
