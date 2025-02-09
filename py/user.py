import copy

from vars import *
from py.biblio import MapDscr
import configparser


class User:
    def __init__(self, name):
        self.name = name
        self.user_file = 'users/' + name + '.ini'
        self.current_map: int = 0
        # карта -> уровень, который сейчас надо проходить (то есть, еще не пройден)
        # self.levels: dict[int, int] = {}
        # в словаре кортеж:
        #   сколько раз сыграли уже игру -> int
        #   сколько набрано очков за все игры -> int
        #   сколько процентов по уровням в текущей игре ->  list[int]
        self.game: dict[int, tuple] = {}

    def load(self):
        try:
            config = configparser.ConfigParser()
            config.read(self.user_file)

            if 'start' in config:
                # текущая карта
                if 'current_map' in config['start']:
                    self.current_map = int(config['start']['current_map'])
                    LOG.write(f'Текущая карта существует {self.current_map}')

            for number in range(999):
                # проверяем есть ли такая карта
                map_section = 'map' + str(number + 1)
                # лезем в конфиг, смотрим секцию
                if map_section in config:
                    if 'number' in config[map_section]:
                        map_number = int(config[map_section]['number'])

                        # уровень который сейчас надо проходить
                        # level = 0
                        # if 'level' in config[map_section]:
                        #     level = int(config[map_section]['level'])
                        # if level <= 1:
                        #     continue
                        # self.levels[map_number] = level

                        points = 0
                        if 'points' in config[map_section]:
                            points = int(config[map_section]['points'])
                        procents = []
                        if 'procents' in config[map_section]:
                            procents = [int(x) for x in config[map_section]['procents'].split(';')]
                        game_number = 0
                        if 'game' in config[map_section]:
                            game_number = int(config[map_section]['game'])
                        self.game[map_number] = (game_number, points, procents)

                        LOG.write(
                            f'{self.name} : map={map_number} points={points} procents={procents} game_number={game_number}')

            LOG.write(f'{self.name} : последняя карта {self.current_map}')

        except Exception as e:
            LOG.write(str(e))

    def contains(self, map_number):
        if map_number not in self.game.keys():
            return False
        else:
            game_number, points, procents = self.game[map_number]
            return len(procents) != 0

    def save(self):
        LOG.write(f'Сохраняемся {self.name}: {self.current_map}')
        section = 'start'

        # записываем имя текущего пользователя
        with open(self.user_file, 'w', encoding='utf-8') as f:
            config = configparser.ConfigParser()
            config[section] = {}
            config[section]['current_map'] = str(self.current_map)

            for i, key in enumerate(self.game.keys()):

                map_section = 'map' + str(i + 1)
                game_number, points, procents = self.game[key]
                # не прошел даже 1 уровень
                if len(procents) < 1:
                    continue

                config[map_section] = {}
                config[map_section]['number'] = str(key)
                config[map_section]['points'] = str(points)
                config[map_section]['game'] = str(game_number)
                config[map_section]['procents'] = ';'.join([str(x) for x in procents if x != 0])

            config.write(f)

    def write_level_data_for_current_map(self, new_points, new_percent):
        LOG.write(f'Новый уровень {self.name}: {self.current_map}')

        if self.current_map not in self.game.keys():
            LOG.write(
                f'Хотим подвинуть уровень. Нет карты {self.current_map}. Что-то пошло не так, пользователь уже должен иметь эту карту')
            return

        game_number, points, procents = self.game[self.current_map]
        procents.append(new_percent)
        points += new_points

        print(dispatcher.session.selected_map.get_level_count())
        if len(procents) == dispatcher.session.selected_map.get_level_count():
            # новый игра
            self.game[self.current_map] = game_number + 1, points, procents
        elif len(procents) > dispatcher.session.selected_map.get_level_count():
            self.game[self.current_map] = game_number, points, [procents[-1]]

        # if self.current_map in self.levels:
        #     self.levels[self.current_map] += 1
        # if self.levels[self.current_map] == dispatcher.session.selected_map.get_level_count():
        #     self.levels[self.current_map] = 1
        #     game_number, points, procents = self.game[self.current_map]
        #     self.game[self.current_map] =  game_number + 1, points, []

    # в словаре кортеж:
    #   сколько раз сыграли уже игру -> int
    #   сколько набрано очков за все игры -> int
    #   сколько процентов по уровням в текущей игре ->  list[int]
    def get_map_data(self, map_number):
        if map_number not in self.game.keys():
            # создадим пустое
            return (0, 0, [])
        else:
            return self.game[map_number]

    def set_choice(self, map_number):
        self.current_map = map_number

        if map_number in self.game.keys():
            return

        self.game[map_number] = self.get_map_data(map_number)
