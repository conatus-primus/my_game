from vars import *
import configparser
import pygame
import os


class User:
    def __init__(self, name):
        self.user_file = 'users/' + name + '.ini'
        self.current_map: int = 0
        # карта -> список уровней, каждый уровень - список дырок
        self.levels: dict[int, list] = {}

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
                        mapfile = 'maps/' + str(map_number) + '.png'
                        if os.path.isfile(mapfile):
                            LOG.write(f'Файл с картой существует {mapfile}')
                        else:
                            continue

                        for num in range(1, MAX_LEVEL_COUNT + 1):
                            level_key = str(num)
                            if level_key not in config[map_section]:
                                break
                            # разберем
                            holes = list(
                                set([int(x.replace('path', '')) for x in config[map_section][level_key].split(',')]))
                            if len(holes) == 0:
                                break
                            if map_number not in self.levels.keys():
                                self.levels[map_number] = []
                            self.levels[map_number].append(sorted(holes))
                else:
                    break
                # print(self.levels)

        except Exception as e:
            LOG.write(str(e))

    def contains(self, map_number):
        if map_number not in self.levels.keys():
            return False
        else:
            return len(self.levels[map_number]) != 0

