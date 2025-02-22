# поддержка коллекции картинок
import glob
import random
import copy
from py.panel import *


class Show:
    # отступ и ширина фокусной рамки вокруг картинки
    margin = 8
    color_ramka = pygame.Color(111, 117, 88)


def load_image(fullname):
    if not os.path.isfile(fullname):
        print(f'Файл с изображением {fullname} не найден')
    image = pygame.image.load(fullname)
    return image


class MapDscr:
    def __init__(self, filename):
        self.filename = filename
        self.map_number: int = None
        self.complexity = None
        self.count_path = None
        self.max_count_holes = None
        self.levels: list[list] = []
        self.image = None
        self.dscr_offset = None
        self.image_size = None
        self.surface = None
        self.stars = ImagePanel(self, FON_COLOR)
        self.image_levels = Dispatcher.load_image('images/system/level_vert.png')
        # уровни по порядку: количество дырок и список идентификаторов дырок (в начале список пустой)
        # список заполним когда пользователь начнет играть в этом уровне (или сгенерим или возьмем у пользователя)
        self.holes_in_level: list[tuple] = []

    # вернуть количество уровней
    def get_level_count(self):
        return len(self.holes_in_level)

    def load(self) -> bool:
        map_name = os.path.basename(self.filename).split('.')[0]
        if map_name.isnumeric():
            self.map_number = int(map_name)
        else:
            return False
        location_path = 'maps/' + map_name + '/location.ini'
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
                    count_holes_in_level = sorted(list(set(count_holes_in_level)))

                    print('количество дырок в уровнях', count_holes_in_level)
                    for x in count_holes_in_level:
                        self.holes_in_level.append((x, []))

                    print(self.holes_in_level)

                    # # максимальная конфигурация по умолчанию вся
                    # for _ in range(len(count_holes_in_level)):
                    #     self.levels.append([])
                    #
                    # self.levels[len(count_holes_in_level) - 1] = list(range(1, count_holes_in_level[0] + 1))
                    #
                    # for i in range(1, len(count_holes_in_level)):
                    #     # исключаем лишние дырки
                    #     # идея такая что не добавляем рандомно, а исключаем так проще наверное
                    #     append_index = len(count_holes_in_level) - 1 - i
                    #     count_as_key = count_holes_in_level[i]
                    #     prev_combination = self.levels[append_index + 1]
                    #     self.levels[append_index] = self.__generate_combination(count_as_key, prev_combination)
                    #
                    # print(self.levels)

                else:
                    raise ('Не хватает данных : ' + location_path)

        except Exception as e:
            LOG.write(str(e))
            return False

        # грузим картинку - сожмем исходную
        self.image = load_image('maps/' + str(self.map_number) + '.png')

        # панель звездочек
        cell_length = load_image('images/system/star_panel.png').get_height()
        self.stars.load('images/system/star_panel.png', 'images/system/star_panel.png', (cell_length, cell_length),
                        self.complexity)
        self.stars.set_enabled_count(self.complexity)

        # панель уровней
        # self.levels_panel.load('images/system/star_panel.png', 'images/system/star_panel_disable.png', (22, 22), 5)
        # self.levels_panel.set_enabled_count(3)

        # разбираем файл
        return True

    # пользователь не работал с этой картой, генерим уровень (нумерация с 1)
    def generate_next_level(self):
        game, points, percents = dispatcher.user.get_map_data(dispatcher.session.map_number)
        max_count = dispatcher.session.selected_map.get_level_count()
        level_number = len(percents) % max_count
        # на всякий случай путаница у нас тут
        level_number %= len(self.holes_in_level)
        count, _ = self.holes_in_level[level_number]
        return ['path' + str(i) for i in range(1, count + 1)]

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
        width, height = self.image_size
        offx, offy = self.dscr_offset

        scaled = pygame.transform.scale(self.image, (self.image_size[0], self.image_size[0]))

        # если у пользователя нет такой карты с уровнями значит он ее еще не проходил - затеняем
        if dispatcher.user is not None and not dispatcher.user.contains(self.map_number):
            scaled.fill((140, 140, 140), special_flags=pygame.BLEND_RGB_SUB)

        screen.blit(scaled, self.dscr_offset)

        opacity = 190
        h_title = 30
        alpha_img = pygame.Surface((width, h_title), pygame.SRCALPHA)
        alpha_img.fill((183, 194, 147, opacity))
        screen.blit(alpha_img, (offx, offy))
        font = pygame.font.SysFont('Comic Sans MS', h_title // 2)
        font.set_bold(True)
        surf_text = font.render(f'Дом № {self.map_number}', True, (0, 0, 0))
        offset_text = offx + (width - surf_text.get_width()) // 2, offy + (h_title - surf_text.get_height()) // 2
        screen.blit(surf_text, offset_text)

        pygame.draw.rect(screen, Show.color_ramka, (offx, offy, width, width), 2, 10)
        pygame.draw.rect(screen, FON_COLOR_DARK,
                         (offx - Show.margin, offy - Show.margin, width + 2 * Show.margin,
                          width + 2 * Show.margin), Show.margin, 20)

        pygame.draw.rect(screen, Show.color_ramka, (offx, offy, width, width), 2, 10)

        rect_complexity = pygame.Rect(offx, offy + width + Show.margin + 2, width, (height - width) // 2)

        self.stars.render(screen,
                          (rect_complexity.x + (rect_complexity.width - self.stars.width) // 2, rect_complexity.y))

        # не рисуем - ход признан неудачным
        # self.render_levels(screen)

    def render_levels(self, screen):
        width, height = self.image_size
        offx, offy = self.dscr_offset
        h_by_levels = self.image_levels.get_height() // MAX_LEVEL_COUNT * len(self.holes_in_level)
        surf = pygame.Surface((self.image_levels.get_width(), h_by_levels))
        surf.blit(self.image_levels, (0, 0))

        dy = (width - self.image_levels.get_height()) // 2
        screen.blit(surf, (offx + width + 3, offy + dy))
        pygame.draw.rect(screen, Show.color_ramka,
                         (offx + width + 2, offy + dy - 1, self.image_levels.get_width() + 2,
                          self.image_levels.get_height() + 2), 1)

    def on_click(self, pos):
        offx, offy = self.dscr_offset
        width, height = self.image_size
        x, y = pos
        return 0 <= x - offx <= width and 0 <= y - offy <= height


class Biblio:
    count_per_line = 4

    def __init__(self, parent):
        self.parent = parent
        self.map_dscr_list = []
        # номер карты в массиве когда карту выбрали кликом
        self.active_map_index = None

    def load(self):
        for filename in glob.glob(CURRENT_DIRECTORY + '/maps/*.png'):
            print(filename)
            # грузим информацию по отдельной карте
            # компонуем по сложностям
            dscr = MapDscr(filename)
            if dscr.load():
                self.map_dscr_list.append(dscr)

        # for x in self.map_dscr_list:
        #     print(x.map_number, x.complexity, x.max_count_holes, x.count_path, x.levels)

        # отсортируем по сложности, кол-во окон, количеству направлений
        self.map_dscr_list = sorted(self.map_dscr_list,
                                    key=lambda a: (a.complexity, a.max_count_holes, a.count_path))

        # for x in self.map_dscr_list:
        #     print(x.map_number, x.complexity, x.max_count_holes, x.count_path, x.levels)

        # размечаем расположение, будем показывать первые 16
        margin_x = 60
        margin_y = HEIGHT_HEADER * 3 // 2
        margin_top = HEIGHT_HEADER // 2
        length = (self.parent.width - (Biblio.count_per_line + 1) * margin_x) // Biblio.count_per_line

        self.active_map_index = 0
        index = 0
        for row in range(Biblio.count_per_line):
            for col in range(Biblio.count_per_line):
                self.map_dscr_list[index].set_position(
                    # лево верх
                    ((margin_x + length) * col + margin_x, (margin_y + length) * row + margin_top),
                    # ширина высота
                    (length, length + margin_y))
                if self.map_dscr_list[index].map_number == dispatcher.user.current_map:
                    self.active_map_index = index
                index += 1
                if index == len(self.map_dscr_list):
                    break
            if index == len(self.map_dscr_list):
                break

    def render(self, screen):
        for x in self.map_dscr_list:
            x.render(screen)

        # TODO лучше бы перенести в Biblio
        if self.active_map_index is not None:
            left, top = self.map_dscr_list[self.active_map_index].dscr_offset
            w, _ = self.map_dscr_list[self.active_map_index].image_size
            d = 1
            pygame.draw.rect(screen, Show.color_ramka,
                             (left - Show.margin - d, top - Show.margin - d, w + 2 * Show.margin + 2 * d,
                              w + 2 * Show.margin + 2 * d),
                             int(Show.margin), 2 * Show.margin)

            # не рисуем - идея признана неудачной
            # self.map_dscr_list[self.active_map_index].render_levels(screen)

    def get_clicked_map(self):
        if 0 <= self.active_map_index <= len(self.map_dscr_list):
            return self.map_dscr_list[self.active_map_index]
        else:
            return None

    def on_click(self, pos):
        for i, map in enumerate(self.map_dscr_list):
            if map.on_click(pos) is True:
                self.active_map_index = i
                return True
        return False

    def __load_map(self, map):
        # TODO фиксируем текущую карту
        LOG.write(f'Играем с {map.filename}')

        # TODO да я знаю, часть параметров дублируется, это эволюция кода, со временем почистим ненужное
        dispatcher.user.set_choice(map.map_number)
        dispatcher.session.map_number = map.map_number
        dispatcher.session.selected_map = map
        dispatcher.session.level_content = map.generate_next_level()
        sounds.vgux()

    def on_double_click(self, event) -> bool:
        for i, map in enumerate(self.map_dscr_list):
            if map.on_click(event.pos) is True:
                self.__load_map(map)
                return True

        return False

    def on_pressed_key(self, pressed_keys):
        row, column = self.active_map_index // Biblio.count_per_line, self.active_map_index % Biblio.count_per_line

        key_dict = {pygame.K_LEFT: ('L', -1), pygame.K_a: ('L', -1),
                    pygame.K_RIGHT: ('R', 1), pygame.K_d: ('R', 1),
                    pygame.K_UP: ('U', -Biblio.count_per_line), pygame.K_w: ('U', -Biblio.count_per_line),
                    pygame.K_DOWN: ('D', Biblio.count_per_line), pygame.K_s: ('D', Biblio.count_per_line)
                    }
        if pressed_keys[pygame.K_RETURN]:
            if 0 <= self.active_map_index < len(self.map_dscr_list):
                self.__load_map(self.map_dscr_list[self.active_map_index])
                return True

        for fixed_key, params in key_dict.items():
            direct, koef = params
            prev = self.active_map_index
            if pressed_keys[fixed_key]:
                self.active_map_index += koef
                if self.active_map_index < 0:
                    if direct == 'L':
                        self.active_map_index = 0
                    elif direct == 'U':
                        self.active_map_index = prev
                elif self.active_map_index >= len(self.map_dscr_list):
                    if direct == 'R':
                        self.active_map_index = len(self.map_dscr_list) - 1
                    elif direct == 'D':
                        self.active_map_index = prev
        return False
