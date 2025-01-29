from vars import *
import configparser


class User:
    def __init__(self, name):
        self.name = name
        self.user_file = 'users/' + name + '.ini'
        self.current_map: int = 0
        # карта -> уровень, который сейчас надо проходить (то есть, еще не пройден)
        self.levels: dict[int, int] = {}
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
                        level = 0
                        if 'level' in config[map_section]:
                            level = int(config[map_section]['level'])
                        if level <= 1:
                            continue
                        self.levels[map_number] = level

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
                            f'{self.name} : map={map_number} points={points} procents={procents} game_number={game_number} next_level={level}')

            LOG.write(f'{self.name} : последняя карта {self.current_map} : пройденные уровни по картам : {self.levels}')

        except Exception as e:
            LOG.write(str(e))

    def contains(self, map_number):
        if map_number not in self.levels.keys():
            return False
        else:
            return self.levels[map_number] != 0

    def save(self):
        section = 'start'

        # записываем имя текущего пользователя
        with open(self.user_file, 'w', encoding='utf-8') as f:
            config = configparser.ConfigParser()
            config[section] = {}
            config[section]['current_map'] = str(self.current_map)
            for i, map_number in enumerate(self.levels.keys()):
                if self.levels[map_number] <= 1:
                    # не прошли ни одного уровня вообще не будем писать эту карты
                    continue
                map_section = 'map' + str(i + 1)
                game_number, points, procents = self.game[map_number]
                config[map_section] = {}
                config[map_section]['number'] = str(map_number)
                config[map_section]['points'] = str(points)
                config[map_section]['game'] = str(game_number)
                config[map_section]['level'] = str(self.levels[map_number])
                config[map_section]['procents'] = ';'.join([str(x) for x in procents])

            config.write(f)

    def save_level(self, level_number):
        self.levels[self.current_map] = self.levels[self.current_map] + 1
