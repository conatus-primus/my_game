import pygame
import random
import configparser

from vars import *
from screensaver import ScreenSaver
from game import Game
from message import Message

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read(CURRENT_DIRECTORY + '/data/system.ini')

    # TODO посмотреть что делать, если совсем нет картинок
    map_number = 1
    if 'start' in config:
        if 'map' in config['start']:
            map_number = int(config['start']['map'])

        if 'level' in config['start']:
            level = int(config['start']['level'])
        else:
            level = 'level1_var1'

    # стартовая заставка
    startScreen = ScreenSaver()

    pygame.mixer.pre_init(44100, -16, 1, 512)  # важно прописать до pygame.init()

    pygame.init()

    pygame.mixer.init()
    pygame.mixer.music.load("sounds/fon.mp3")
    # pygame.mixer.music.play(-1)

    s_glass = pygame.mixer.Sound('sounds/glass1.ogg')

    pygame.display.set_caption('Защита окон от монстров')

    game = Game()
    messageError = None

    # TODO посмотреть внимательное еще раз - определиться, где перехватывать исключения при загрузке
    try:
        game.load(map_number)
    except Exception as e:
        LOG.write(str(e))
        messageError = Message(str(e))

    screen = pygame.display.set_mode(SIZE_GAME)

    running = True
    while running:
        pressed = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if startScreen is not None:
                    if startScreen.onClick(event.pos):
                        startScreen = None
                    else:
                        s_glass.play()

            if event.type == pygame.KEYDOWN:
                pressed = True

        if startScreen is not None:
            startScreen.render(screen)
        else:
            # TODO вынести в константы
            screen.fill((240, 155, 89))
            if messageError is not None:
                messageError.render(screen)
            else:
                game.render(screen)

        pygame.display.flip()

        if (pressed):
            game.onPressed(pygame.key.get_pressed())

pygame.quit()
