# разбор location.ini с описанием уровней и ходов
from vars import *
import configparser
import pygame


class Location:
    def __init__(self, map_number):
        self.location_file = CURRENT_DIRECTORY + '/maps/' + str(map_number) + '/location.ini'
        self.hole_by_key = dict()
        self.levels = dict()
        # по умолчанию
        self.current_hole_id = 'path1'

    def load(self):
        try:
            config = configparser.ConfigParser()
            config.read(self.location_file)

            if 'keys' in config:
                for hole_number in range(1, 20):
                    if str(hole_number) in config['keys']:
                        data = [x for x in config['keys'][str(hole_number)].split(',')]
                        hole_name = 'path' + str(hole_number)
                        self.hole_by_key[hole_name] = dict()
                        for action in data:
                            key, number = action.split(':')
                            self.hole_by_key[hole_name][key] = 'path' + number

            # [level2]
            # 1=path1:1,2 path3:1,2
            # 2=path4:1,2 path5:1,2
            for level in range(1, 10):
                level_name = 'level' + str(level)
                if level_name not in config:
                    continue
                for variant in range(1, 32):
                    variant_name = str(variant)
                    if variant_name not in config[level_name]:
                        break
                    variant_strings = config[level_name][variant_name].split()
                    variant_list = []
                    # path1:1,2
                    # path3:1,2
                    for var in variant_strings:
                        hole, _ = var.split(':')
                        # path3
                        variant_list += var.replace(',', ' ' + hole).replace(':', ' ' + hole).split()
                        # path3
                        # path31
                        # path32

                    if level_name not in self.levels:
                        self.levels[level_name] = dict()
                    self.levels[level_name][variant_name] = variant_list

            print(self.levels)

        except Exception as e:
            LOG.write(str(e))
            quit()

    # получить следующую дырку при нажатии на клавиши
    # user_keys = pygame.key.get_pressed()
    def on_pressed_key(self, user_keys, active_hole_id):
        key_dict = {pygame.K_LEFT: 'L', pygame.K_a: 'L',
                    pygame.K_RIGHT: 'R', pygame.K_d: 'R',
                    pygame.K_UP: 'U', pygame.K_w: 'U',
                    pygame.K_DOWN: 'D', pygame.K_s: 'D'
                    }
        for fixed_key, direct in key_dict.items():
            if user_keys[fixed_key]:
                self.current_hole_id = self.hole_by_key[self.current_hole_id][key_dict[fixed_key]]
                old_active_hole_id = active_hole_id
                active_hole_id = self.hole_by_key[active_hole_id][key_dict[fixed_key]]
                print(f'{old_active_hole_id} --> {active_hole_id}')
                break
        return active_hole_id
