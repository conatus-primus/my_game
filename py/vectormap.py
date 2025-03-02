# загрузка векторного описания карты
# базируется на разборе svg файла
# считываются дырки и направлений движения
# линии движения ориентированы по направлению к своим дырками
import copy
from vars import *
from py.svgparser import ParserSvgFileDict, ParserSvgString, Gnuplot, VectorizerPictures


class Hole:
    def __init__(self):
        # идентификатор дырки
        self.id = None
        # координаты дырки
        self.coords_hole = None
        # центр дырки
        self.centre_hole = None
        # направляющие
        self.lines = None
        # огибающий прямоугольник
        self.rect = None


# перевод строковой дырки с направляющими в цифровой вид
# на входе кортеж ид дырка, координаты дырки строкой, список кортежей направляющих: (ид, координаты строкой)
# на выходе аттрибуты класса ид дырки, вещественные координаты дырки, вещественные координаты центра дырки
# и список кортежей неаправляющий (ид, вещественные координаты)
class ParserHole(Hole):
    def __init__(self, string_hole):
        Hole.__init__(self)
        # сырые данные
        self.string_hole = string_hole

    def load(self):
        self.__parse_hole()
        self.__parse_lines()
        if self.id is None or self.coords_hole is None or self.centre_hole is None or self.lines is None:
            raise ValueError(f'{self.__class__.__name__}:{__name__} : что-то пошло не так загрузкой дырки')

    def __parse_hole(self):
        self.id, string_coords, _ = self.string_hole
        # разбираем координаты дырки
        self.coords_hole = ParserSvgString(string_coords).coords
        if len(self.coords_hole) == 0:
            raise ValueError(f'{self.__class__.__name__}:{__name__} : ошибка перевода в цифру дырки {self.id}')

        # вычислим среднюю точку для установки амулетов и разворота направляющих если понадобится
        # средняя точка как центр тяжести расположена так себе - будем брать центр габаритного прямоугольника
        # вангую что все придет к тому, что и точку придется задавать руками

        left = top = right = bottom = None
        for x, y in self.coords_hole:
            if left is None:
                left = right = x
                top = bottom = y
            else:
                left = min(left, x)
                right = max(right, x)
                top = min(top, y)
                bottom = max(bottom, y)
        self.centre_hole = (left + right) / 2, (top + bottom) / 2

    def __parse_lines(self):
        self.lines = []
        _, _, string_lines = self.string_hole
        for string_line in string_lines:
            id, line_coords = string_line
            line = ParserSvgString(line_coords).coords
            if len(line) <= 1:
                raise ValueError(
                    f'{self.__class__.__name__}:{__name__} : ошибка перевода в цифру направляющей {id} дырки {self.id}')
            # разворачиваем направляющую чтобы она шла к центру дырки
            dist_first = self.__distance2(line[0], self.centre_hole)
            dist_last = self.__distance2(line[-1], self.centre_hole)
            if dist_first < dist_last:
                line = line[::-1]
            self.lines.append((id, line))

    # квадрат расстояния между двумя точками
    def __distance2(self, p_last, p_first):
        return (p_last[0] - p_first[0]) ** 2 + (p_last[1] - p_first[1]) ** 2

    # перекрываем для оладочной печати
    def __str__(self):
        res = []
        res.append(Gnuplot.plot(self.centre_hole))
        res.append(' ')
        res.append(Gnuplot.plot(self.coords_hole))
        res.append(' ')
        for id, one_line in self.lines:
            res.append(Gnuplot.plot(one_line))
            res.append(' ')
        return '\n'.join(res)


# разбор svg файла с описанием карты
class ParserMapFile:
    def __init__(self, svg_file):
        self.svg_file = svg_file
        self.holes: ParserHole = None

    # загрузка данных из файла
    def load(self):
        self.holes = None

        loader = ParserSvgFileDict(self.svg_file)
        loader.load()
        path = loader.elem_g_d

        if len(path) == 0:
            raise ValueError(
                f'{self.__class__.__name__}:{__name__} : отсутствует описание игрового поля для {self.svg_file}')

        # разберемся, где линии, где дырки
        # считаем что дыры path1 - path9
        str_holes = []
        key_holes = ['path' + str(i) for i in range(1, 100)]
        for key in path.keys():
            if key in key_holes:
                str_holes.append((key, path[key], []))

        # разбираемся с направлениями - распределяем их по дыркам path1_N в path1
        # считаем что направления от 1 до 99 : path1_1 path1_2 path2_1 path2_2
        for i, elem in enumerate(str_holes):
            hole_id = elem[0]
            hole_coord = elem[1]
            hole_lines = elem[2]
            key_lines = [hole_id + '_' + str(i) for i in range(1, 100)]
            for key in key_lines:
                if key in path.keys():
                    hole_lines.append((key, path[key]))
                    str_holes[i] = (hole_id, hole_coord, hole_lines)

            # print(f'--------------{hole_id}------------------')
            # переводим в цирфовой вид дырку с направляющими
            hole_object = ParserHole(str_holes[i])
            hole_object.load()
            # print(holeObject)
            if self.holes is None:
                self.holes = []
            self.holes.append(hole_object)
            # print('--------------------------------')


# объект с описанием карты
class RawMap(ParserMapFile):
    def __init__(self, map_number):
        self.current_svg_file = 'maps/' + str(map_number) + '/' + str(map_number) + '.svg'
        self.current_txt_file = 'temp/' + str(map_number) + '.txt'
        super().__init__(self.current_svg_file)

    def load(self):
        super().load()
        self.__print()

    def __print(self):
        pass
        # with open(self.current_txt_file, 'wt') as fw:
        #     for obj in self.holes:
        #         res = obj.__str__()
        #         print(res, file=fw)
        #         print(' ', file=fw)


# объект с описанием карты в зависимости от уровня игры
class VectorMap:
    def __init__(self, map_number):
        self.map_number = map_number
        self.raw_map = RawMap(map_number)
        self.holes = None
        self.disabled_holes = None
        self.strips = dict()
        self.current_level_content = None

    def load(self):
        if self.raw_map is not None:
            self.raw_map.load()
            self.holes = self.raw_map.holes

        if self.holes is None:
            return

        # нда, наблюдаем некую стихийность разработки
        # наконец, определились...
        # вводим панели для показа наличия нескольких амулетов на одной дырке
        # уходим от концепции обводки дырки если на ней несколько амулетов
        # будем все пассивные амулеты рисовать на панели, расположенной около дырки
        # панели векторизуются одной линией с идентификатором stripN, где N - номер дырки

        # откроем отдельно еще раз svg и скачаем оттуда наши панели
        vect_map = VectorizerPictures(self.raw_map.current_svg_file)
        vect_map.load()

        for hole in self.holes:
            strip_id = hole.id.replace('path', 'strip')
            # находим в файле такой идентификатор
            strip_string = vect_map.line_by_id(strip_id)
            if strip_string is not None:
                self.strips[hole.id] = copy.deepcopy(ParserSvgString(strip_string).coords)
        print(self.strips)

    def set_current_level_content(self, current_level_content):
        if self.current_level_content == current_level_content:
            return

        self.current_level_content = current_level_content

        self.holes = []
        self.disabled_holes = []

        for hole in self.raw_map.holes:
            new_hole = Hole()
            new_hole.id = hole.id
            # координаты дырки
            new_hole.coords_hole = hole.coords_hole
            new_hole.rect = OVERALL_RECT(new_hole.coords_hole)
            # центр дырки
            new_hole.centre_hole = hole.centre_hole
            # направляющие
            new_hole.lines = []
            for id_line, coords_line in hole.lines:
                new_hole.lines.append((id_line, coords_line))

            if current_level_content is None or hole.id in current_level_content:
                self.holes.append(new_hole)
            else:
                self.disabled_holes.append(new_hole)

    # получить список активных дырок и количество путей к ним
    def all_active_pathes(self):
        res = []
        for hole in self.holes:
            res.append((hole.id, len(hole.lines)))
        return res

    # получить список огибающих прямоугольников для активных дырок
    def get_active_rects(self, delta):
        res = []
        for hole in self.holes:
            rect = pygame.Rect(hole.rect.left - delta, hole.rect.top - delta, hole.rect.width + 2 * delta,
                               hole.rect.height + 2 * delta)
            res.append(rect)
        return res

    # получить начало и конец одного из путей по идентификатору дырки и номеру линии
    def line_coords(self, hole_id, line_number):
        for hole in self.holes:
            if hole.id != hole_id:
                continue
            if 0 <= line_number < len(hole.lines):
                _, coords = hole.lines[line_number]
                return coords[0], coords[-1]
            else:
                return None
        return None

    def render(self, surface):
        pens = [
            (pygame.Color(40, 40, 40), 11),
            (pygame.Color(80, 80, 80), 9),
            (pygame.Color(120, 120, 120), 7),
            (pygame.Color(160, 160, 160), 5),
            (pygame.Color(200, 200, 200), 3),
            (pygame.Color(240, 240, 240), 1)
        ]

        for pen in pens:
            color, h = pen
            for n_hole, one_hole in enumerate(self.holes):
                # круги в точках перегиба дырки, чтобы сгладить широкую линию
                for point in one_hole.coords_hole:
                    pygame.draw.circle(surface, color, point, h // 2, h // 2)
                # дырка
                pygame.draw.lines(surface, color, True, one_hole.coords_hole, h)
                # направляющие дырки
                for n_line, line in enumerate(one_hole.lines):
                    id, coords = line
                    # закругление внешнего конца для красоты
                    pygame.draw.circle(surface, color, coords[0], h // 2, h // 2)
                    # сама направляющая
                    pygame.draw.lines(surface, color, False, coords, h)

        pens = [
            (pygame.Color(200, 200, 200), 5),
            (pygame.Color(80, 80, 80), 3)
        ]

        for pen in pens:
            color, h = pen
            for n_hole, one_hole in enumerate(self.disabled_holes):
                # круги в точках перегиба дырки, чтобы сгладить широкую линию
                for point in one_hole.coords_hole:
                    pygame.draw.circle(surface, color, point, h // 2, h // 2)
                pygame.draw.lines(surface, color, True, one_hole.coords_hole, h)
