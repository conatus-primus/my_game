# поддержка коллекции картинок
from vars import *
import glob
import random
import copy


def load_image(fullname):
    if not os.path.isfile(fullname):
        print(f'Файл с изображением {fullname} не найден')
    image = pygame.image.load(fullname)
    return image


class MapDscr:
    def __init__(self, filename):
        self.filename = filename
        self.map_number = None
        self.complexity = None
        self.count_path = None
        self.max_count_holes = None
        self.levels: dict[int, list] = {}
        self.image = None
        self.dscr_offset = None
        self.image_size = None
        self.surface = None

    def load(self) -> bool:
        map_name = os.path.basename(self.filename).split('.')[0]
        if map_name.isnumeric():
            self.map_number = int(map_name)
        else:
            return False
        location_path = CURRENT_DIRECTORY + '/maps/' + map_name + '/location.ini'
        LOG.write(f'{self.__class__.__name__} {__name__} : разбор {location_path}')
        try:
            file = open(location_path)
        except IOError as e:
            LOG.write(str(e))
            return False
        else:
            file.close()

        try:
            config = configparser.ConfigParser()
            config.read(location_path)

            if 'location' in config:
                # сложность
                if 'complexity' in config['location']:
                    self.complexity = int(config['location']['complexity'])
                else:
                    raise ('Не хватает данных : ' + location_path)

                # количество дырок
                if 'holes' in config['location']:
                    self.max_count_holes = int(config['location']['holes'])
                else:
                    raise ('Не хватает данных : ' + location_path)

                # количество линий
                if 'path' in config['location']:
                    self.count_path = int(config['location']['path'])
                else:
                    raise ('Не хватает данных : ' + location_path)

                # сколько окон входит в уровнеь и делаем разбивку
                if 'levels' in config['location']:
                    # создадим уровни рандомно
                    count_holes_in_level = [min(int(x), self.max_count_holes) for x in
                                            config['location']['levels'].split(';')]
                    # добавляем максимальное число - всегда есть уровень с максимальным числом дырок
                    count_holes_in_level.append(self.max_count_holes)
                    count_holes_in_level = sorted(list(set(count_holes_in_level)), reverse=True)

                    print(count_holes_in_level)

                    # максимальная конфигурация по умолчанию вся
                    self.levels[count_holes_in_level[0]] = list(range(1, count_holes_in_level[0] + 1))

                    for i in range(1, len(count_holes_in_level)):
                        # исключаем лишние дырки
                        # идея такая что не добавляем рандомно, а исключаем так проще наверное
                        count_as_key = count_holes_in_level[i]
                        prev_combination = self.levels[count_holes_in_level[i - 1]]
                        self.levels[count_as_key] = self.__generate_combination(count_as_key, prev_combination)

                    print(self.levels)

                else:
                    raise ('Не хватает данных : ' + location_path)

        except Exception as e:
            LOG.write(str(e))
            return False

        # грузим картинку - сожмем исходную
        self.image = load_image('maps/' + str(self.map_number) + '.png')

        # разбираем файл
        return True

    @staticmethod
    def __generate_combination(count_hole, upper_level: list[int]):
        # считаем сколько чисел надо исключить
        temp_level = copy.copy(upper_level)
        exclude = len(upper_level) - count_hole
        for _ in range(exclude):
            n = random.randint(0, len(temp_level))
            temp_level.pop(n - 1)
        return temp_level

    def set_position(self, offset, size):
        self.dscr_offset = offset
        self.image_size = size
        self.surface = pygame.Surface(size)

    def render(self, screen):
        # self.surface.blit(self.image_small, (0, 0))
        # scale = pygame.transform.scale(self.surface, (self.image_size[0], self.image_size[0]))
        # screen.blit(scale, self.dscr_offset)
        width, height = self.image_size
        scaled = pygame.transform.scale(self.image, (self.image_size[0], self.image_size[0]))
        screen.blit(scaled, self.dscr_offset)

        offx, offy = self.dscr_offset
        pygame.draw.rect(screen, Biblio.color_ramka, (offx, offy, width, width), 2, 10)
        pygame.draw.rect(screen, FON_COLOR_DARK,
                         (offx - Biblio.margin, offy - Biblio.margin, width + 2 * Biblio.margin,
                          width + 2 * Biblio.margin), Biblio.margin, 20)

        pygame.draw.rect(screen, Biblio.color_ramka, (offx, offy, width, width), 2, 10)

        rect_complexity = pygame.Rect(offx, offy + width + Biblio.margin + 5, width, (height - width) // 2)
        pygame.draw.rect(screen, pygame.Color('black'), rect_complexity, 1)

    def on_click(self, pos):
        print(pos)
        offx, offy = self.dscr_offset
        width, height = self.image_size
        x, y = pos
        return 0 <= x - offx <= width and 0 <= y - offy <= height


class Biblio:
    # отступ и ширина фокусной рамки вокруг картинки
    margin = 10
    color_ramka = pygame.Color(111, 117, 88)

    def __init__(self, parent):
        self.parent = parent
        self.map_dscr_list = []
        # номер карты в массиве когда карту выбрали кликом
        self.active_map_index = None

    # загрузить все доступные карты, каталог фиксированный
    def load(self):
        for filename in glob.glob(CURRENT_DIRECTORY + '/maps/*.png'):
            print(filename)
            # грузим информацию по отдельной карте
            # компонуем по сложностям
            dscr = MapDscr(filename)
            if dscr.load():
                self.map_dscr_list.append(dscr)

        for x in self.map_dscr_list:
            print(x.map_number, x.complexity, x.max_count_holes, x.count_path, x.levels)

            # отсортируем по сложности, кол-во окон, количесту направлений
        self.map_dscr_list = sorted(self.map_dscr_list, key=lambda a: (a.complexity, a.max_count_holes, a.count_path))

        for x in self.map_dscr_list:
            print(x.map_number, x.complexity, x.max_count_holes, x.count_path, x.levels)

        # размечаем расположение, будем показывать первые 16
        margin_x = 60
        margin_y = HEIGHT_HEADER * 3 // 2
        margin_top = HEIGHT_HEADER // 2
        count_per_line = 4
        length = (self.parent.width - (count_per_line + 1) * margin_x) // count_per_line

        index = 0
        for row in range(count_per_line):
            for col in range(count_per_line):
                self.map_dscr_list[index].set_position(
                    # лево верх
                    ((margin_x + length) * col + margin_x, (margin_y + length) * row + margin_top),
                    # ширина высота
                    (length, length + margin_y))
                index += 1
                if index == len(self.map_dscr_list):
                    break
            if index == len(self.map_dscr_list):
                break

        self.active_map_index = 0

    def render(self, screen):
        for x in self.map_dscr_list:
            x.render(screen)

        # TODO лучше бы перенести в Biblio
        if self.active_map_index is not None:
            left, top = self.map_dscr_list[self.active_map_index].dscr_offset
            w, _ = self.map_dscr_list[self.active_map_index].image_size
            pygame.draw.rect(screen, Biblio.color_ramka,
                             (left - Biblio.margin, top - Biblio.margin, w + 2 * Biblio.margin, w + 2 * Biblio.margin),
                             int(Biblio.margin * 0.75), 2 * Biblio.margin)

    def on_click(self, pos):
        self.active_map_index = None
        for i, map in enumerate(self.map_dscr_list):
            if map.on_click(pos) is True:
                self.active_map_index = i
