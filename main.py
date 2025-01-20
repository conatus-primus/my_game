import pygame
import random
import enum
from vars import *
from invite import Invite, Start
from game import Game
from message import Message
from py.shared import *

FPS = 60


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

    # важно прописать до pygame.init()
    pygame.mixer.pre_init(44100, -16, 1, 512)

    pygame.init()
    pygame.font.init()
    pygame.mixer.init()

    # TODO посмотреть что делать, если совсем нет картинок

    # стартовая заставка
    runList = [Invite(), Start()]

    sounds = Sounds()
    pygame.display.set_caption('Защита окон от монстров')

    # создаем игру
    game = Game()

    # делаем после ini pygame
    # здесь загружаем текущую сессию
    dispatcher.load(game)
    messageError = None

    screen = pygame.display.set_mode(SIZE_GAME)

    clock = pygame.time.Clock()

    running = True
    while running:
        pressed = False
        for event in pygame.event.get():
            if event.type == TIMER_EVENT_ONE_SEC:
                dispatcher.onTimer()

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONUP:
                if runList is None and game is not None:
                    game.onClickExtend(event)

            if event.type == pygame.MOUSEBUTTONDOWN:

                if runList is not None:
                    if runList[0].onClick(event.pos):

                        runList.pop(0)
                        if len(runList) == 0:
                            runList = None
                            dispatcher.session.user = 'inna'
                            # TODO посмотреть внимательное еще раз - определиться, где перехватывать исключения при загрузке
                            try:
                                game.load()
                            except Exception as e:
                                LOG.write(str(e))
                                messageError = Message(str(e))
                        else:
                            runList[0].load()



                        sounds.sVgux.play()

                elif game is not None:
                    game.onClick(event.pos)

            if event.type == pygame.KEYDOWN:
                pressed = True

        tick = clock.tick(FPS)

        if runList is not None:
            runList[0].render(screen, tick)
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

    dispatcher.session.write()

pygame.quit()
