from vars import *
import configparser


class User:
    def __init__(self, name):
        self.name = name
        self.user_file = 'users/' + name + '.ini'
        self.current_map: int = 0
        # карта -> список уровней, каждый уровень - список дырок
        self.levels: dict[int, int] = {}

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
                        if 'level' in config[map_section]:
                            self.levels[map_number] = int(config[map_section]['level'])
                else:
                    break
            LOG.write(f'Пользователь {self.name} : последняя карта {self.current_map} : пройденные уровни по картам : {self.levels}')

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
                map_section = 'map' + str(i + 1)
                config[map_section] = {}
                config[map_section]['number'] = str(map_number)
                config[map_section]['level'] = str(self.levels[map_number])
            config.write(f)

    def save_level(self, level_number):
        self.levels[self.current_map] = self.levels[self.current_map] + 1
