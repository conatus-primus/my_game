# считывание из svg векторного описания дыр и направлений движения мобов
# линии движения ориентированы по направлению к своему окну
from vars import *
import xml.etree.ElementTree as ET
import os


# отладочный вывод координат в формате gnuplot
class Gnuplot:
    def plot(self, coords):
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
# на выходе словарь идентификатор -> текстовая строка с геометрией объекта в формате svg
class ParserSvgFileDict:
    def __init__(self, svg_file):
        self.svg_file = svg_file
        self.elem_g_d = None
        self.elem_g_rect = None

    # загрузка данных из файла
    def load(self):
        LOG.write(f'{self.__class__.__name__}:{__name__} : загрузка {self.svg_file}')
        tree = ET.parse(self.svg_file)
        root = tree.getroot()

        # выцепляем данные по тегу g/path
        self.elem_g_d = dict()
        self.elem_g_rect = dict()

        for elem in root.findall(self.__svg_prefix('g')):
            for elem2 in elem.iter():
                # линия
                if elem2.tag == self.__svg_prefix('path'):
                    # в словаре должен быть иденитификатор id и координаты d
                    if 'id' in elem2.attrib and 'd' in elem2.attrib:
                        self.elem_g_d[elem2.attrib['id']] = elem2.attrib['d']

                # прямоугольник
                if elem2.tag == self.__svg_prefix('rect'):
                    attrs = ['id', 'width', 'height', 'x', 'y']
                    if all([x in elem2.attrib for x in attrs]):
                        self.elem_g_rect[elem2.attrib['id']] = float(elem2.attrib['x']), float(
                            elem2.attrib['y']), float(elem2.attrib['width']), float(elem2.attrib['height'])

    def __svg_prefix(self, tag):
        return '{http://www.w3.org/2000/svg}' + tag

    # найти линию по идентификатору
    def lineByID(self, id):
        return self.elem_g_d[id] if id in self.elem_g_d else None

    # найти прямоугольник по идентификатору
    def rectByID(self, id):
        return self.elem_g_rect[id] if id in self.elem_g_rect else None


# разбор одной линии формата svg
# на выходе список кортежей (x, y)
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
class ParserSvgString(Gnuplot):
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
            raise ValueError(f'{self.__class__.__name__}:{__name__}: в path нет описания координат')

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
                    raise ValueError(
                        f'{self.__class__.__name__}:{__name__} : завершающая команда z, но есть еще необработанные координаты')
                self.coords.append(self.coords[0])

            else:
                # по идее это координаты
                if cmd in ['v', 'h']:
                    xy = self.__parseOneCoord(value)
                else:
                    xy = self.__parseTwoCoords(value)

                if xy is None:
                    raise ValueError(f'{self.__class__.__name__}:{__name__} : ошибочные данные в svg-path')

                # подготовим смещение
                prev_point = (0, 0)
                if offset and len(self.coords):
                    prev_point = self.coords[-1]

                if cmd == 'm':
                    if len(self.coords) == 0:
                        # первая точка по идее абсолютные координаты
                        self.coords.append(xy)
                    else:
                        # не первая точка, разбираемся со смещениями
                        self.coords.append((xy[0] + prev_point[0], xy[1] + prev_point[1]))

                else:
                    if len(self.coords) == 0:
                        # такого не может быть если я все правильно понимаю
                        # первая команда обязательно m
                        raise ValueError(
                            f'{self.__class__.__name__}:{__name__} : ошибка разбора первой команды {cmd} в svg-path')

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
        return self.plot(self.coords)


# получение цифровых примитивов
class LoaderSvgPrimitives(ParserSvgFileDict):
    def __init__(self, svg_file):
        super().__init__(svg_file)

    # получить габаритный прямоугольник по идентификатору
    # возвращается лево верх ширина высота
    def overallRectangle(self, id):
        rect = self.rectByID(id)
        if rect is not None:
            return rect

        coords = self.lineByID(id)
        if coords is None or len(coords) == 0:
            return None

        l = r = coords[0][0]
        t = b = coords[0][1]
        for x, y in coords:
            l = min(x, l)
            r = max(x, r)
            t = min(y, t)
            b = max(y, b)
        return l, t, r - l, b - t
