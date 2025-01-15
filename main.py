import pygame
import random
import enum
from vars import *
from screensaver import ScreenSaver
from game import Game, Session
from message import Message


class MouseButton(enum.Enum):
    # левая кнопка мыши
    LEFT = 1,
    # правая кнопка мыши
    RIGHT = 3,
    # средняя кнопка мыши
    MIDDLE = 2,
    # прокрутка вперед
    SCROLL_FRONT = 4,
    # прокрутка назад
    SCROLL_BACK = 5


if __name__ == '__main__':

    # стартовая заставка
    startScreen = ScreenSaver()

    # важно прописать до pygame.init()
    pygame.mixer.pre_init(44100, -16, 1, 512)

    pygame.init()
    pygame.font.init()
    pygame.mixer.init()
    pygame.mixer.music.load("sounds/fon.mp3")

    s_glass = pygame.mixer.Sound('sounds/glass1.ogg')

    # TODO посмотреть что делать, если совсем нет картинок
    session = Session()
    session.read()

    pygame.display.set_caption('Защита окон от монстров')

    game = Game()
    # делаем после инита pygame
    dispatcher.load()
    dispatcher.game = game
    messageError = None

    # TODO посмотреть внимательное еще раз - определиться, где перехватывать исключения при загрузке
    try:
        game.load(session)
    except Exception as e:
        LOG.write(str(e))
        messageError = Message(str(e))

    screen = pygame.display.set_mode(SIZE_GAME)

    running = True
    while running:
        pressed = False
        for event in pygame.event.get():
            if event.type == TIMER_EVENT_ONE_SEC:
                dispatcher.onTimer()

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONUP:
                if startScreen is None and game is not None:
                    game.onClickExtend(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if startScreen is not None:
                    if startScreen.onClick(event.pos):
                        startScreen = None
                    else:
                        s_glass.play()
                elif game is not None:
                    game.onClick(event.pos)

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
            game.onPressedKey(pygame.key.get_pressed())

    session.write()

pygame.quit()
