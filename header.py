# чердак игрового поля
import pygame
from vars import *
from block import Block


class Header(Block):
    def __init__(self, game):
        super().__init__(game, WIDTH_GAME, HEIGHT_HEADER)
        #self.font = pygame.font.Font(None, HEIGHT_HEADER - 20)
        self.font = pygame.font.SysFont('Comic Sans MS', HEIGHT_HEADER - 20)

    def render(self, ):
        pygame.draw.rect(self.surface, FON_COLOR_MID, (0, 0, self.width, self.height))

        d = 10
        surf_text = self.font.render(dispatcher.session.user, True, (0, 0, 0))
        offset = d, (HEIGHT_HEADER - surf_text.get_height()) // 2
        self.surface.blit(surf_text, offset)

        if dispatcher.game.state is not None and dispatcher.game.state != GameState.GAME_NO:
            # некрасиво жуть
                game, points, percents = dispatcher.user.get_map_data(dispatcher.session.map_number)
                max_count = dispatcher.session.selected_map.get_level_count()
                surf_text = self.font.render(
                    f'Дом № {dispatcher.session.map_number}          Игра {game + 1}          Уровень {len(percents) % max_count + 1}',
                    True, (0, 0, 0))
                offset = (self.width - surf_text.get_width()) // 2, (HEIGHT_HEADER - surf_text.get_height()) // 2
                self.surface.blit(surf_text, offset)

        if dispatcher.logicaaa() is not None:
            dispatcher.logicaaa().render_header(self.surface, self.font)

