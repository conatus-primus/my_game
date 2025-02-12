import enum
from invite import Invite, Start
from game import Game
from message import Message
from finish import Finish
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
    run_list = [Invite(), Start()]

    sounds = Sounds()
    pygame.display.set_caption('Защита окон от монстров')

    # создаем игру
    game = Game()

    # делаем после ini pygame
    # здесь загружаем текущую сессию
    dispatcher.load(game)
    message_error = None

    screen = pygame.display.set_mode(SIZE_GAME)

    clock = pygame.time.Clock()

    # эмуляция двойного клика мыши (предлагают 0.5 сек между двумя кликами)
    double_click_time = 0.5
    click_time = time.time()
    click_pos = pygame.mouse.get_pos()

    running = True
    running2 = True

    while running and running2:
        pressed = False
        for event in pygame.event.get():

            if dispatcher.flag_finish is True:
                dispatcher.on_stop()
                dispatcher.finish_screen = Finish()
                dispatcher.flag_finish = False
                game = None

            if event.type == TIMER_EVENT_DISPATCHER:
                dispatcher.on_timer()
                if dispatcher.session.logica is not None:
                    dispatcher.session.logica.on_timer_dispatcher()

            if event.type == TIMER_EVENT_GAME:
                if dispatcher.session.logica is not None:
                    dispatcher.session.logica.on_timer()

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONUP:

                # эмуляция двойного клика мыши
                if time.time() - click_time < double_click_time and click_pos == pygame.mouse.get_pos():
                    print("Double click detected")
                    if run_list is None and game is not None:
                        game.on_double_click(event)

                click_time = time.time()
                click_pos = pygame.mouse.get_pos()

                if run_list is None and game is not None:
                    game.on_click_extend(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                print(event.pos)
                if run_list is not None:
                    if run_list[0].onClick(event.pos):

                        # ---------------------------------------------
                        run_list.pop(0)
                        if len(run_list) == 0:
                            run_list = None
                            # TODO посмотреть внимательное - определиться, где перехватывать исключения при загрузке
                            try:
                                game.load()
                            except Exception as e:
                                LOG.write(str(e))
                                message_error = Message(str(e))
                        else:
                            run_list[0].load()
                        # sounds.sVgux.play()
                        # ---------------------------------------------

                elif game is not None:
                    game.onClick(event.pos)

            if event.type == pygame.KEYDOWN:
                pressed = True

        dispatcher.tick = tick = clock.tick(FPS)

        if run_list is not None:
            run_list[0].render(screen, tick)

            # ---------------------------------------------
            # отрабатываем случай когда курсор стоит на логине и нажали на кнопку продолжения
            # из-за того что логин перехватывает ввод пришлось ввести game.start
            # флаг меняется в логине и тогда здесь можно отработать переход на игру
            # некрасиво конечно, но как смогли... надо еще получше осознать все это...
            if game is not None and game.start is True:
                game.start = False
                run_list = None
                # TODO посмотреть внимательное еще раз - определиться, где перехватывать исключения при загрузке
                try:
                    game.load()
                except Exception as e:
                    LOG.write(str(e))
                    message_error = Message(str(e))
                # sounds.sVgux.play()
            # ---------------------------------------------

        else:
            # TODO вынести в константы
            screen.fill((240, 155, 89))

            if dispatcher.finish_screen is not None:
                running2 = dispatcher.finish_screen.render(screen)

            if message_error is not None:
                message_error.render(screen)
            else:
                if game is not None:
                    game.render(screen)

        pygame.display.flip()

        if pressed and game is not None:
            game.on_pressed_key(pygame.key.get_pressed())

    dispatcher.on_stop()

pygame.quit()
