# загрузка векторного описания карты
# базируется на разборе svg файла
# считываются дырки и направлений движения
# линии движения ориентированы по направлению к своим дырками
import copy
from vars import *
from svgparser import ParserSvgFileDict, ParserSvgString, Gnuplot


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

# перевод строковой дырки с направляющими в цифровой вид
# на входе кортеж ид дырка, координаты дырки строкой, список кортежей направляющих: (ид, координаты строкой)
# на выходе аттрибуты класса ид дырки, вещественные координаты дырки, вещественные координаты центра дырки
# и список кортежей неаправляющий (ид, вещественные координаты)
class ConverterSvgStringsToHole(Gnuplot, Hole):
    def __init__(self, string_hole):
        # сырые данные
        self.string_hole = string_hole

    def load(self):
        self.__parseHole()
        self.__parseLines()
        if self.id is None or self.coords_hole is None or self.centre_hole is None or self.lines is None:
            raise ValueError(f'{self.__class__.__name__}:{__name__} : что-то пошло не так загрузкой дырки')

    def __parseHole(self):
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

    def __parseLines(self):
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
        res.append(self.plot(self.centre_hole))
        res.append(' ')
        res.append(self.plot(self.coords_hole))
        res.append(' ')
        for id, one_line in self.lines:
            res.append(self.plot(one_line))
            res.append(' ')
        return '\n'.join(res)


# разбор svg файла с описанием карты
class ParserMapFile:
    def __init__(self, svg_file):
        self.svg_file = svg_file
        self.holes = None

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
        key_holes = ['path' + str(i) for i in range(1, 10)]
        for key in path.keys():
            if key in key_holes:
                str_holes.append((key, path[key], []))

        # разбираемся с направлениями - распределяем их по дыркам path1N в path1
        # считаем что направления от 1 до 9 : path11 path12 path21 path22
        for i, elem in enumerate(str_holes):
            hole_id = elem[0]
            hole_coord = elem[1]
            hole_lines = elem[2]
            key_lines = [hole_id + str(i) for i in range(1, 10)]
            for key in key_lines:
                if key in path.keys():
                    hole_lines.append((key, path[key]))
                    str_holes[i] = (hole_id, hole_coord, hole_lines)

            # print(f'--------------{hole_id}------------------')
            # переводим в цирфовой вид дырку с направляющими
            holeObject = ConverterSvgStringsToHole(str_holes[i])
            holeObject.load()
            # print(holeObject)
            if self.holes is None:
                self.holes = []
            self.holes.append(holeObject)
            # print('--------------------------------')


# объект с описанием карты
class RawMap(ParserMapFile):
    def __init__(self, map_number):
        self.current_svg_file = CURRENT_DIRECTORY + '/maps/' + str(map_number) + '/' + str(map_number) + '.svg'
        self.current_txt_file = CURRENT_DIRECTORY + '/temp/' + str(map_number) + '.txt'
        super().__init__(self.current_svg_file)

    def load(self):
        super().load()
        self.__print()

    def __print(self):
        with open(self.current_txt_file, 'wt') as fw:
            for obj in self.holes:
                res = obj.__str__()
                print(res, file=fw)
                print(' ', file=fw)


# объект с описанием карты в зависимости от уровня игры
class LevelMap:
    def __init__(self, map_number):
        self.map_number = map_number
        self.rawMap = RawMap(map_number)
        self.holes = None

    def load(self):
        if self.rawMap is not None:
            self.rawMap.load()
            self.holes = self.rawMap.holes

    def setLevelData(self, visible_holes=None):

        self.holes = []

        for hole in self.rawMap.holes:
            if visible_holes is None or hole.id in visible_holes:
                new_hole = Hole()
                new_hole.id = hole.id
                # координаты дырки
                new_hole.coords_hole = hole.coords_hole
                # центр дырки
                new_hole.centre_hole = hole.centre_hole
                # направляющие
                new_hole.lines = []
                for id_line, coords_line in hole.lines:
                    if visible_holes is None or id_line in visible_holes:
                        new_hole.lines.append((id_line, coords_line))
                self.holes.append(new_hole)



