# разбор location.ini с описанием уровней и ходов
from vars import *
import configparser
import pygame


class Location:
    def __init__(self, map_number):
        self.location_file = CURRENT_DIRECTORY + '/maps/' + str(map_number) + '/location.ini'
        self.holeByKey = dict()

    def load(self):
        try:
            config = configparser.ConfigParser()
            config.read(self.location_file)

            if 'keys' in config:
                for hole_number in range(1, 20):
                    if str(hole_number) in config['keys']:
                        data = [x for x in config['keys'][str(hole_number)].split(',')]
                        self.holeByKey[str(hole_number)] = dict()
                        for action in data:
                            key, number = action.split(':')
                            self.holeByKey[str(hole_number)][key] = number

        except Exception as e:
            LOG.write(str(e))
            quit()

    # получить следующую дырку при нажатии на клавиши
    # user_keys = pygame.key.get_pressed()
    def next_hole(self, user_keys, current_hole, current_level):
        key_dict = {pygame.K_LEFT: 'L', pygame.K_a: 'L',
                    pygame.K_RIGHT: 'R', pygame.K_d: 'R',
                    pygame.K_UP: 'U', pygame.K_w: 'U',
                    pygame.K_DOWN: 'D', pygame.K_s: 'U'
                    }
        for fixed_key, direct in key_dict.items():
            if user_keys[fixed_key]:
                return self.holeByKey[current_hole][key_dict[fixed_key]]
        return current_hole
