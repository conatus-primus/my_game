import random
from vars import *
from py.amulet import AmuletPassive


class Rule:
    rules = {
        0: (50, 1.00),
        1: (51, 1.05),
        2: (55, 1.10),
        3: (60, 1.15),
        4: (65, 1.20),
        5: (68, 1.25),
        6: (71, 1.30),
        7: (75, 1.35),
        8: (77, 1.40),
        9: (79, 1.43),
        10: (80, 1.45),
        11: (81, 1.47),
        12: (82, 1.49),
    }

    first = {
        True: 'Уровень пройден',
        False: 'Уровень не пройден'
    }

    second = {
        True: ['Отличная игра!',
               'Ты сегодня в ударе!',
               'Какая игра, просто блеск!',
               'Неплохо, неплохо!',
               'Ты - молодец!',
               'Какой ты быстрый!'
               ],
        False: [
            'В этот раз не повезло.',
            'Сейчас не твой час.',
            'Бывали игры и получше, увы.',
            'Видимо, это серая полоса.'
        ]
    }

    third = {
        True: [
            'Переходим на следующий уровень!',
            'Идем на следующий уровень!',
            'Следующий уровень ждет.'
        ],
        False: [
            'Попробуем еще раз?',
            'Выше нос, всё получится!',
            'Соберись и сыграй еще раз.'
        ]
    }

    fourth = {
        True: ['Ой! Уровни-то все пройдены. Поздравляем!',
               'Игра продолжится снова с первого уровня.',
               'Но будет сложнее, приготовься.'],
        False: ['']
    }

    def __init__(self):
        # процент пропусков
        self.perecent_lose = None
        # коэффициент ускорения скорости
        self.koef_velocity = None


class Round:
    # длительность одного уровня
    interval_sec = 1 * 30
    velocity = 100

    def __init__(self):
        self.clear()

    def clear(self):
        # сколько длится раунд
        self.duration_sec = 0
        # полное количество мобов за раунд
        self.all_mob_count = 0
        # количество пойманных мобов за раунд
        self.caught_mob_count = 0
        # признак окончания игры
        self.game_end = False


class Logica(Round):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.pause = False
        self.text = None

        self.game_number = 0
        self.threadhold_percent = 100
        self.mob_number = random.choice([6, 7, 8, 9])
        self.velocity = Round.velocity

        # данные для генерации мобов
        self.create_new_mob_function = None
        self.holes_info = []
        self.all_lines = 0

        self.order = 2
        self.prev_line_index = None
        self.current_level = 1

        self.create_passive_amulet_function = None

    def on_timer_dispatcher(self):
        if self.game_end is True:
            return

        if self.create_new_mob_function is None or self.all_lines == 0 or self.pause is True:
            return

        self.order += 1
        if self.order % 3 != 0:
            return

        # получаем путь для нового моба
        for _ in range(self.current_level):
            new_hole_index = random.randint(0, len(self.holes_info) - 1)
            # print(f'********* random {new_hole_index} : {len(self.holes_info) - 1}')
            id, count = self.holes_info[new_hole_index]
            for i in range(count):
                self.create_new_mob_function(id, i, self.velocity, self.mob_number)

    def on_timer_dispatcher2(self):
        if self.game_end is True:
            return

        if self.create_new_mob_function is None or self.all_lines == 0 or self.pause is True:
            return

        self.order += 1
        if self.order % 3 != 0:
            return

        # получаем путь для нового моба
        new_line_index = None
        while True:
            new_line_index = random.randint(1, self.all_lines)
            if new_line_index == self.prev_line_index:
                continue
            self.prev_line_index = new_line_index
            break

        # генерируем new_line_index мобов
        new_line_index = 1 * new_line_index // 2
        if new_line_index == 0:
            new_line_index = 1
        all = list(range(self.all_lines))

        while len(all) != new_line_index:
            index = random.choice(all)
            all.remove(index)

        for i in all:
            new_line_index = i
            print(f'********* random {new_line_index}')
            for id, count in self.holes_info:
                for i in range(count):
                    new_line_index -= 1
                    if new_line_index == 0:
                        self.create_new_mob_function(id, i, self.velocity, self.mob_number)
                        break
                if new_line_index == 0:
                    break

    def on_timer(self):
        if self.game_end is True:
            return

        dispatcher.need_update(self)
        if self.pause is True:
            return
        self.duration_sec += 1

        if Logica.interval_sec <= self.duration_sec:
            LOG.write(f'Пришло время закончить уровень!!!')

            # признак окончания игры
            self.game_end = True
            # выигрыш проигрыш
            flag_success = self.isSuccess()
            if flag_success is True:
                sounds.succeess()
            else:
                sounds.fail()

            # генерируем текст
            self.__generate_text__(flag_success)

            if flag_success:
                # заработано очков за раунд
                points = self.caught_mob_count
                # обновляем данные игры
                dispatcher.user.write_level_data_for_current_map(points, self.curreent_caught_percent())
                dispatcher.user.save()
                dispatcher.need_update(self)
            else:
                pass

            # сообщаем в игру об окончании
            dispatcher.game.game_over(flag_success)
            return

    # как закончилась игра
    def isSuccess(self):
        game_number, _, _ = dispatcher.user.get_map_data(dispatcher.session.map_number)
        max_procent, _ = Rule.rules.get(game_number, Rule.rules[12])
        return self.curreent_caught_percent() >= max_procent

    def __generate_text__(self, flag_success):
        self.text = []
        self.text.append(Rule.first[flag_success])

        number = random.randint(0, len(Rule.second[flag_success]) - 1)
        self.text.append(Rule.second[flag_success][number])

        number = random.randint(0, len(Rule.third[flag_success]) - 1)
        self.text.append(Rule.third[flag_success][number])

        if flag_success:
            _, _, percents = dispatcher.user.get_map_data(dispatcher.session.map_number)
            level_count_in_map = dispatcher.session.selected_map.get_level_count()

            if len(percents) + 1 == level_count_in_map:
                # это был последний уровень надо начинать новую игру
                self.text += Rule.fourth[flag_success]

    # то что надо выводить в заголовок (время раунда)
    def render_header(self, surface, font):
        if self.game_end is True:
            return

        if self.duration_sec == 0:
            return

        text = f'{self.duration_sec} сек.'
        surf_text = font.render(text, True, (0, 0, 0))
        offset = WIDTH_GAME - surf_text.get_width() - HEIGHT_HEADER, (HEIGHT_HEADER - surf_text.get_height()) // 2
        surface.blit(surf_text, offset)

    #
    def render_marginright(self, surface):
        if self.all_mob_count == 0:
            return

        statistic = []
        color = (0, 0, 0)
        statistic.append(('Монстры в игре', 24, False, color))
        statistic.append((f'Всего', 24, False, color))
        statistic.append((f'{self.all_mob_count}', 24, True, color))
        statistic.append((f'Поймано', 24, False, color))
        statistic.append((f'{self.caught_mob_count}', 24, True, color))
        statistic.append((f'или', 24, False, color))
        percent = self.curreent_caught_percent()
        if percent < self.threadhold_percent:
            color = (237, 28, 36)
        statistic.append((f'{percent}%', 24, True, color))
        color = (0, 0, 0)
        statistic.append(('', 24, False, color))
        statistic.append((f'порог прохождения {self.threadhold_percent}%', 16, True, color))

        offset_y = OFFSET_HEIGHT_MARGIN
        for text, h, bold, color in statistic:
            font = pygame.font.SysFont('Comic Sans MS', h)
            font.set_bold(bold)
            surf_text = font.render(text, True, color)
            offset = (WIDTH_MARGIN - surf_text.get_width()) // 2, offset_y
            surface.blit(surf_text, offset)
            offset_y += surf_text.get_height()

    def render_field(self, surface):
        if self.game_end is False:
            return

        dy = 100
        opacity = 180
        alpha_img = pygame.Surface((WIDTH_MAP, HEIGHT_MAP - 2 * dy), pygame.SRCALPHA)
        alpha_img.fill((183, 194, 147, opacity))

        surface.blit(alpha_img, (0, dy))

        if self.text is None:
            return

        offset_y = dy + HEIGHT_HEADER

        # готовим отображение текста
        font = pygame.font.SysFont('Comic Sans MS', 48)
        font.set_bold(True)
        surf_text = font.render(self.text[0], True, (0, 0, 0))
        offset = (WIDTH_MAP - surf_text.get_width()) // 2, offset_y
        surface.blit(surf_text, offset)

        font.set_bold(False)
        for i in range(1, len(self.text)):
            offset_y += surf_text.get_height() + HEIGHT_HEADER // 2
            if i == 3:
                font = pygame.font.SysFont('Comic Sans MS', 36)
            surf_text = font.render(self.text[i], True, (0, 0, 0))
            offset = (WIDTH_MAP - surf_text.get_width()) // 2, offset_y
            surface.blit(surf_text, offset)

    def set_create_mob_amulet_function(self, create_new_mob_function, create_passive_amulet_function, holes_info):
        self.create_new_mob_function = create_new_mob_function
        self.create_passive_amulet_function = create_passive_amulet_function
        self.holes_info = []
        self.all_lines = 0
        for id, count in holes_info:
            self.holes_info.append((id, count))
            self.all_lines += count
        print(self.holes_info)

        # создаем пассивные амулеты: начиная с 4-ого окна на каждую пару по одному амулету
        # с какого количества начинааем добавлять
        amulet_handles = []
        AmuletPassive.load_amulets(amulet_handles)

        dispatcher.game.message(MessadgID.DEF_AMULETS_CLEAR)
        if self.create_passive_amulet_function is not None and len(amulet_handles) >= 1:
            m = 4
            if len(self.holes_info) >= m:
                passive_amulet_count = (len(self.holes_info) - (m - 2)) // 2

                if dispatcher.param_passive is True:
                    ids = []
                    for i in range(len(self.holes_info)):
                        ids.append('path' + str(i + 1))
                    if ids[0] == 'path1':
                        ids.append(ids[0])
                        ids.pop(0)
                    amulet_index = random.randint(0, len(amulet_handles) - 1)
                    self.create_passive_amulet_function(ids, amulet_handles[amulet_index])
                    dispatcher.game.message(MessadgID.DEF_AMULET_BALL, amulet_handles[amulet_index].id,
                                            amulet_handles[amulet_index].price_max)

                else:

                    res = random.sample(self.holes_info, passive_amulet_count * 2)
                    for i in range(0, len(res), 2):
                        id1, _ = res[i]
                        id2, _ = res[i + 1]
                        if id1 == 'path1':
                            id1, id2 = id2, id1
                        amulet_index = random.randint(0, len(amulet_handles) - 1)
                        self.create_passive_amulet_function([id1, id2], amulet_handles[amulet_index])
                        dispatcher.game.message(MessadgID.DEF_AMULET_BALL, amulet_handles[amulet_index].id,
                                                amulet_handles[amulet_index].price_max)

    def caught_mob(self, success):
        if self.game_end is True:
            return
        if success:
            self.caught_mob_count += 1
        self.all_mob_count += 1

    def curreent_caught_percent(self):
        return int(self.caught_mob_count / self.all_mob_count * 100) if self.all_mob_count != 0 else 0

    def game_start(self):
        # начинаем подсчет секунд
        self.clear()
        print(dispatcher.session.level_content)
        self.game_number, _, _ = dispatcher.user.get_map_data(dispatcher.session.map_number)
        index = self.game_number % len(Rule.rules)

        # ускорение скорости
        self.threadhold_percent, koef = Rule.rules[index]
        self.velocity = Round.velocity * koef

        _, _, percents = dispatcher.user.get_map_data(dispatcher.session.map_number)
        level_count_in_map = dispatcher.session.selected_map.get_level_count()
        self.current_level = len(percents) % level_count_in_map + 1
        sounds.start()

    def game_pause(self):
        self.pause = True

    def game_replay(self):
        # начинаем подсчет секунд
        self.clear()
        self.pause = False
        sounds.start()

    def game_continue(self):
        self.pause = False
        sounds.start()
