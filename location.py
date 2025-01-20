# разбор location.ini с описанием уровней и ходов
from vars import *
import configparser
import pygame


class Location:
    def __init__(self, map_number):
        self.location_file = CURRENT_DIRECTORY + '/maps/' + str(map_number) + '/location.ini'
        self.holeByKey = dict()
        self.levels = dict()
        # по умолчанию
        self.currentHoleID = 'path1'
        self.currentLevelID = 'path1'

    def load(self):
        try:
            config = configparser.ConfigParser()
            config.read(self.location_file)

            if 'keys' in config:
                for hole_number in range(1, 20):
                    if str(hole_number) in config['keys']:
                        data = [x for x in config['keys'][str(hole_number)].split(',')]
                        holeName = 'path' + str(hole_number)
                        self.holeByKey[holeName] = dict()
                        for action in data:
                            key, number = action.split(':')
                            self.holeByKey[holeName][key] = 'path' + number

            # [level2]
            # 1=path1:1,2 path3:1,2
            # 2=path4:1,2 path5:1,2
            for level in range(1, 10):
                levelName = 'level' + str(level)
                if levelName not in config:
                    continue
                for variant in range(1, 32):
                    variantName = str(variant)
                    if variantName not in config[levelName]:
                        break
                    variantStrings = config[levelName][variantName].split()
                    variantList = []
                    # path1:1,2
                    # path3:1,2
                    for var in variantStrings:
                        hole, _ = var.split(':')
                        # path3
                        variantList += var.replace(',', ' ' + hole).replace(':', ' ' + hole).split()
                        # path3
                        # path31
                        # path32

                    if levelName not in self.levels:
                        self.levels[levelName] = dict()
                    self.levels[levelName][variantName] = variantList

            print(self.levels)

        except Exception as e:
            LOG.write(str(e))
            quit()

    # получить следующую дырку при нажатии на клавиши
    # user_keys = pygame.key.get_pressed()
    def onPressedKey(self, user_keys, activeHoleID):
        key_dict = {pygame.K_LEFT: 'L', pygame.K_a: 'L',
                    pygame.K_RIGHT: 'R', pygame.K_d: 'R',
                    pygame.K_UP: 'U', pygame.K_w: 'U',
                    pygame.K_DOWN: 'D', pygame.K_s: 'D'
                    }
        for fixed_key, direct in key_dict.items():
            if user_keys[fixed_key]:
                # self.currentHoleID = self.holeByKey[self.currentHoleID][key_dict[fixed_key]]
                # activeHoleID = self.currentHoleID
                self.currentHoleID = self.holeByKey[self.currentHoleID][key_dict[fixed_key]]
                oldActiveHoleID = activeHoleID
                activeHoleID = self.holeByKey[activeHoleID][key_dict[fixed_key]]
                print(f'{oldActiveHoleID} --> {activeHoleID}')
                break
        return activeHoleID

    # установить выбранный уровень
    def setLevelID(self, level):
        self.currentLevelID = level

    # установить текущую дырку
    def setHoleID(self, hole):
        self.currentHoleID = hole

    def currentLevelContent(self):
        return ['path1', 'path1_1', 'path1_2', 'path2', 'path2_1', 'path2_2', 'path3', 'path3_1', 'path3_2', 'path4',
                'path4_1',
                'path4_2', 'path5', 'path5_1', 'path5_2']
