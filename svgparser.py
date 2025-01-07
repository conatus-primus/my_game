# считывание из svg векторного описания дыр и направлений движения мобов
# линии движения ориентированы по направлению к своему окну
from vars import *
import xml.etree.ElementTree as ET
import os


def SVG(tag):
    return '{http://www.w3.org/2000/svg}' + tag


# отладочный вывод координат в формате gnuplot
def GNUPLOT(coords):
    if coords is None:
        return 'Отсутствую координаты'

    res = []
    if isinstance(coords, tuple):
        # искусственно формируем крест с центром в точке центра
        res.append(f'{coords[0] - 5} {-coords[1]}')
        res.append(f'{coords[0] + 5} {-coords[1]}')
        res.append(' ')
        res.append(f'{coords[0]} {-(coords[1] - 5)}')
        res.append(f'{coords[0]} {-(coords[1] + 5)}')
    else:
        for x, y in coords:
            res.append(f'{x} {-y}')
    return '\n'.join(res)


# разбор svg файла
class SvgParserFile:
    def __init__(self, svg_file):
        self.svg_file = svg_file
        self.holes = None

    # загрузка данных из файла
    def load(self):
        self.holes = None
        tree = ET.parse(self.svg_file)
        root = tree.getroot()

        # TODO : проверить что в формате единицы измерения пиксели
        # выцепляем данные по тегу g/path
        path = dict()
        for elem in root.findall(SVG('g')):
            for elem2 in elem.iter():
                if elem2.tag == SVG('path'):
                    # в словаре должен быть иденитификатор id и координаты d
                    if 'id' in elem2.attrib and 'd' in elem2.attrib:
                        path[elem2.attrib['id']] = elem2.attrib['d']

        if len(path) == 0:
            raise ValueError(f'SvgParser: Отсутствует описание игрового поля для {self.svg_file}')

        # разберемся где линии где дырки
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
            holeObject = RawHoleObject(str_holes[i])
            holeObject.load()
            # print(holeObject)
            if self.holes is None:
                self.holes = []
            self.holes.append(holeObject)
            # print('--------------------------------')


# разбор одной линии svg
'''
M 353.79592,273.20516 252.81426,0.8626346
m 588.4322,502.37288 -0.12711,-6.99152 3.17796,-5.72034 5.72034,-5.21187 6.1017,-1.52542 9.27966,-0.63559 
12.20339,-0.25424 7.5,-0.25424 5.84745,1.01695 8.00848,1.90678 7.5,4.19492 3.81356,3.68644 v 83.8983 h 
-68.64407 l 0.38136,-5.4661 -1.01695,-6.48305 z

Заглавная буква - абсолютные координаты, строчная буква - относительные
m - переместиться к следующей точке
l - линия от текущего положения к этой точке
h - горизонтальная линия
v - вертикальная линия
'''
class SvgParserOneLine:
    #
    def __init__(self, path):
        self.coords = []
        self.__parse(path)

    # разбор строки 353.79592,273.20516
    def __parseTwoCoords(self, sCoord):
        strXY = sCoord.split(',')
        if len(strXY) == 2:
            return (float(strXY[0]), float(strXY[1]))
        else:
            return None

    # разбор строки  h -68.64407
    def __parseOneCoord(self, sCoord):
        return float(sCoord)

    #
    def __parse(self, path):
        elems = path.strip().split()
        if len(elems) == 0:
            raise ValueError('SvgParserOneLine: В path нет описания координат')

        offset = False
        cmd = ''
        self.coords = []
        cmds = ['m', 'l', 'v', 'h']

        while len(elems):
            value = elems[0]

            if value.lower() in cmds:
                cmd = value.lower()
                offset = True if value in cmds else False

            elif value.lower() == 'z':
                # считаем что это последняя команда
                if len(elems) > 1:
                    raise ValueError('SvgParserOneLine: Завершающая команда z, но есть еще необработанные координаты')
                self.coords.append(self.coords[0])

            else:
                # по идее это координаты

                if cmd in ['v', 'h']:
                    xy = self.__parseOneCoord(value)
                else:
                    xy = self.__parseTwoCoords(value)

                if xy is None:
                    raise ValueError('SvgParserOneLine: Ошибочные данные в svg-path')

                # подготовим смещение
                prev_point = (0, 0)
                if offset and len(self.coords):
                    prev_point = self.coords[-1]

                if cmd == 'm':
                    if len(self.coords) == 0:
                        # первая точка по идее абсолютные координаты
                        self.coords.append(xy)
                    else:
                        # не первая точка разбираемся со смещениями
                        self.coords.append((xy[0] + prev_point[0], xy[1] + prev_point[1]))

                else:
                    if len(self.coords) == 0:
                        # такого не может быть если я все правильно понимаю
                        # первая команда обязательно m
                        raise ValueError(f'SvgParserOneLine: Ошибка разбора первой команды {cmd} в svg-path')

                    if cmd == 'l':
                        self.coords.append((xy[0] + prev_point[0], xy[1] + prev_point[1]))
                    elif cmd == 'v':
                        # берем х координату из предыдущей точки, y смещаем
                        self.coords.append((prev_point[0], xy + prev_point[1]))
                    elif cmd == 'h':
                        # берем y координату из предыдущей точки, x смещаем
                        self.coords.append((xy + prev_point[0], prev_point[1]))

            elems.pop(0)

    # для печати
    def __str__(self):
        return GNUPLOT(self.coords)


# перевод строковой дырки с направляющими в цифровой вид
# на входе кортеж ид дырка, координаты дырки строкой, список кортежей направляющих: (ид, координаты строкой)
class RawHoleObject:
    def __init__(self, string_hole):
        # сырые данные
        self.string_hole = string_hole
        # идентификатор дырки
        self.id = None
        # координаты дырки
        self.coords_hole = None
        # центр дырки
        self.centre_hole = None
        # направляющие
        self.coord_lines = None

    def load(self):
        self.__parseHole()
        self.__parseLines()
        if self.id is None or self.coords_hole is None or self.centre_hole is None or self.coord_lines is None:
            raise ValueError(f'SvgParserOneHole: Что-то пошло не так с дыркой из карты {MAP_NUMBER}')

    def __parseHole(self):
        self.id, string_coords, _ = self.string_hole
        # разбираем координаты дырки
        self.coords_hole = SvgParserOneLine(string_coords).coords
        if len(self.coords_hole) == 0:
            raise ValueError(f'SvgParserOneHole: Ошибка перевода в цифру дырки {self.id}')

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
        self.coord_lines = []
        _, _, string_lines = self.string_hole
        for string_line in string_lines:
            id, line_coords = string_line
            line = SvgParserOneLine(line_coords).coords
            if len(line) <= 1:
                raise ValueError(f'SvgParserOneHole: Ошибка перевода в цифру направляющей {id} дырки {self.id}')
            # разворачиваем направляющую чтобы она шла к центру дырки
            dist_first = self.__distance2(line[0], self.centre_hole)
            dist_last = self.__distance2(line[-1], self.centre_hole)
            if dist_first < dist_last:
                line = line[::-1]
            # теряем идентификатор направляющей - он нам не нуже
            self.coord_lines.append(line)

    # квадрат расстояния между двумя точками
    def __distance2(self, p_last, p_first):
        return (p_last[0] - p_first[0])**2 + (p_last[1] - p_first[1])**2

    # перекрываем для оладочной печати
    def __str__(self):
        res = []
        res.append(GNUPLOT(self.centre_hole))
        res.append(' ')
        res.append(GNUPLOT(self.coords_hole))
        res.append(' ')
        for line in self.coord_lines:
            res.append(GNUPLOT(line))
            res.append(' ')
        return '\n'.join(res)


# объект с описанием карты
class RawMapObject(SvgParserFile):
    def __init__(self, map_number):
        self.map_number = map_number
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