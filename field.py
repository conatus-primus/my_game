# карта игрового поля
from block import Block
from vectormap import VectorMap
from location import Location
from py.amulet import *
from py.mob import *


class Field(Block):
    def __init__(self, game):
        super().__init__(game, WIDTH_MAP, HEIGHT_MAP)
        self.static_map = None
        self.vectorMap = None
        self.location = None
        self.amulets = []
        self.amulet_user = None
        # данные для панелей пассивных амулетов
        self.strips: dict[str, list(Amulet)] = {}
        self.mobs = []
        self.mob_groups = []
        self.all_mob_groups = pygame.sprite.Group()
        self.last_show_mobs = []
        self.last_track = []

    def load(self, map_number):

        # self.mob = ChangedMob(self, 100, (0, 0), (900, 900), 'images/mobs/mob9_')
        # self.mob.set_start()

        # грузим варианты уровней и движения клавиш
        self.location = Location(map_number)
        self.location.load()

        # грузим векторное описание
        self.vectorMap = VectorMap(map_number)
        self.vectorMap.load()

        # обработка статики в карте (фон + дырки + направляющие)
        self.static_map = StaticMap(map_number)
        self.static_map.load()

        # устанавливаем в векторную карту описание текущего уровня
        self.vectorMap.set_current_level_content(dispatcher.session.level_content)

        # пользовательский амулет
        self.amulet_user = AmuletUser(self)
        # задаем все дырки
        self.amulet_user.load(self.vectorMap.holes + self.vectorMap.disabled_holes)
        # связываем амулет с локатором - изменится локатор - изменим и амулеты
        self.amulet_user.setLocation(self.location)
        self.amulets.append(self.amulet_user)

        # amuletPassive = AmuletPassive(self, 'ruby.png', ['path1', 'path2'], SHOW_TIME_IN_HOLE_SEC)
        # # self.amuletPassive = AmuletPassive(self, 'ruby.png', ['path5'], [2, 0.1])
        # amuletPassive.load(self.vectorMap.holes)
        # amuletPassive.start()
        # # self.amulets.append(amuletPassive)
        #
        # amuletPassive = AmuletPassive(self, 'sapphire.png', ['path2', 'path1'], SHOW_TIME_IN_HOLE_SEC)
        # amuletPassive.load(self.vectorMap.holes)
        # amuletPassive.start()
        # # self.amulets.append(amuletPassive)

        #
        dispatcher.need_update(self)

    def render(self):
        pygame.draw.rect(self.surface, pygame.Color('blue'), (0, 0, self.width, self.height))
        self.static_map.render(self.surface)
        self.vectorMap.render(self.surface)

        # рисуем все амулеты
        for a in self.amulets:
            a.render(self.surface)

        # рисуем планки если они есть
        self.render_strips()

        # рисуем переходные состояния - они самые последние
        for a in self.amulets:
            a.render_last(self.surface)

        for x in self.mobs:
            x.render(self.surface)
        # self.all_mob_groups.draw(self.surface)
        # self.mob.render(self.surface)

        if dispatcher.logicaaa() is not None:
            dispatcher.logicaaa().render_field(self.surface)

        # TODO надо понять как это делать по-нормальному
        temp = []
        for x in self.last_show_mobs:
            if x is None:
                continue
            x.render(self.surface)
            if x.tick_change <= 0 or x.start is False:
                del x
            else:
                temp.append(x)
        self.last_show_mobs = temp

        for x in self.last_track:
            if x is not None and x.is_stop() is False:
                x.render(self.surface)

    # вход - нажатые клавиши pygame.key.get_pressed()
    def on_pressed_key(self, pressed_keys):
        # пересчитать положение амулетов
        if any([a.on_pressed_key(pressed_keys) for a in self.amulets]):
            self.recalc_amulet_relative_position()
            dispatcher.need_update(self)
            return True
        return False

    def update(self, sender):
        self.static_map.set_brightness(dispatcher.session.brightness)
        self.vectorMap.set_current_level_content(dispatcher.session.level_content)
        for a in self.amulets:
            a.update()

    def onClick(self, pos):
        # пересчитать положение амулетов
        if any([a.onClick(pos) for a in self.amulets]):
            self.recalc_amulet_relative_position()
            dispatcher.need_update(self)
            return True
        return False

    def on_timer(self, current_time):
        # пересчитать положение амулетов
        if any([a.on_timer(current_time) for a in self.amulets]):
            self.recalc_amulet_relative_position()
            dispatcher.need_update(self)
            return True
        return False

    # пересчитать положение амулетов
    def recalc_amulet_relative_position(self):
        # есть хотя бы один амулет гарантировано
        hole_position: list[tuple[str, int, Amulet]] = []
        for a in self.amulets:
            res = a.currentHole()
            if res is not None and res[0] != '':
                hole_position.append(res)

        # activeHoleID, startSecs, self
        # слепляем ключ для сортировки время, сдвинутое на 100 плюс номер дырки (номер точно меньше 100)
        hole_position = sorted(hole_position, key=lambda x: -(int(x[0].replace('path', '')) * 100 + x[1]))
        state = AmuletState.MONTRER_EN_ENTIER

        pos = dict()
        self.strips = {}
        for i, item in enumerate(hole_position):
            activeHoleID, _, amulet = item
            state = pos.get(activeHoleID)
            if state is None:
                amulet.setMontrerState(AmuletState.MONTRER_EN_ENTIER)
                pos[activeHoleID] = AmuletState.MONTRER_UNE_PARTIE
            else:
                amulet.setMontrerState(state)
                if state == AmuletState.MONTRER_UNE_PARTIE:
                    pos[activeHoleID] = AmuletState.NE_MONTRER_PAS
            # заполним данные для отрисовки панелей
            if activeHoleID not in self.strips.keys():
                self.strips[activeHoleID] = []
            self.strips[activeHoleID].append(amulet)

    # рисуем планки с количеством амулетов если они есть
    def render_strips(self):
        for hole_id, list_amulet in self.strips.items():
            if hole_id in self.vectorMap.strips:
                # координаты планки
                coords = self.vectorMap.strips[hole_id]

                if len(coords) <= 1:
                    continue
                if len(list_amulet) <= 1:
                    continue

                pos_start, pos_stop = coords[0], coords[-1]
                dx, dy = pos_stop[0] - pos_start[0], pos_stop[1] - pos_start[1]
                dist = (dx ** 2 + dy ** 2) ** 0.5
                if dist == 0:
                    dx, dy = 0, 0
                else:
                    dx, dy = Amulet.strip_max_length * dx / dist, Amulet.strip_max_length * dy / dist

                num = 0
                for i, a in enumerate(list_amulet):
                    point = pos_start[0] + num * dx, pos_start[1] + num * dy
                    a.render_strip(point, self.surface)
                    num += 1

    # начать играть заново
    def game_replay(self):
        print(f'{self.__class__.__name__}:{self.game_replay.__name__} Ждем начала игры....')
        self.game_over(True)

    # создать нового моба
    def create_new_mob(self, hole_id, line_number, velocity, mob_number):
        # print(f'Создаем моба {hole_id}: {line_number}')

        coords = self.vectorMap.line_coords(hole_id, line_number)
        # print(f'mob coords={coords}')
        new_mob = ChangedMob(self, velocity, coords[0], coords[1], 'mob' + str(mob_number),
                             self.all_mob_groups, self.callback_update, len(self.mobs) % 3 + 1
                             )
        self.mobs.append(new_mob)
        new_mob.set_start()
        # self.mob = ChangedMob(self, 100, (0, 0), (900, 900), 'images/mobs/mob9_')
        # self.mob.set_start()

    def create_passive_amulet(self, hole_ids, amulet_handle):
        print(f'Создаем пассивный амулет {id}: {hole_ids}')
        amuletPassive = AmuletPassive(self, amulet_handle.id, hole_ids, SHOW_TIME_IN_HOLE_SEC,
                                      amulet_handle.price_max)
        amuletPassive.load(self.vectorMap.holes)
        amuletPassive.start()
        self.amulets.append(amuletPassive)
        dispatcher.game.message(MessadgID.DEF_AMULET_BALL, amulet_handle.id, amulet_handle.price_max)

    # действия связанные с началом игры
    def game_start(self):
        self.game_over(True)
        # накидываем в логику идентификаторы дыр и пути и себя
        if dispatcher.logicaaa():
            dispatcher.logicaaa().set_create_mob_amulet_function(
                self.create_new_mob, self.create_passive_amulet,
                self.vectorMap.all_active_pathes())

    def game_pause(self):
        self.game_over(True, False)

    def game_over(self, flag_success, delete_amulets=True):
        for mob in self.mobs:
            del mob
        del self.mobs
        self.mobs = []
        del self.all_mob_groups
        self.all_mob_groups = pygame.sprite.Group()
        if delete_amulets is False:
            return
        while len(self.amulets) > 1:
            x = self.amulets[0]
            self.amulets.remove(x)
            if isinstance(x, AmuletPassive):
                del x
            else:
                self.amulets.append(x)
        self.last_track = []
        self.last_show_mobs = []
        self.recalc_amulet_relative_position()

    def callback_update(self, mob):
        mob_del_list = []
        amulet_del_list = []
        delta_rect = 5

        for a in self.amulets:
            amulet_rect = a.get_active_rect(delta_rect)
            if amulet_rect is None:
                continue
            for mob in self.mobs:
                if amulet_rect.collidepoint(mob.rect.center) is True:
                    # было столкновение
                    # вычесть из амулета очки
                    a.minus_balls()
                    if isinstance(a, AmuletPassive):
                        dispatcher.game.message(MessadgID.DEF_AMULET_BALL, a.amulet_name, a.balls)
                    dispatcher.logicaaa().caught_mob(True)
                    # зафиксировать моба для удаления
                    mob_del_list.append(mob)
                    if a.count_balls() is False:
                        amulet_del_list.append(a)

        for mob in mob_del_list:
            if mob in self.mobs:
                self.mobs.remove(mob)
                mob.last_show(True)
                self.last_show_mobs.append(mob)

        for a in amulet_del_list:
            LOG.write(f'*** Закончился лимит: удалился {a}')
            self.amulets.remove(a)
            amulet_rect = a.get_active_rect(delta_rect)
            if amulet_rect is not None:
                track = AmuletTrack(amulet_rect.center, a.color)
                self.last_track.append(track)
            del a
        if len(amulet_del_list):
            self.recalc_amulet_relative_position()

        # пробежать по дыркам без амулетов может с кем-то пересеклись
        hole_rects = self.vectorMap.get_active_rects(delta_rect)

        for rect in hole_rects:
            mob_del_list = []
            for mob in self.mobs:
                if rect.collidepoint(mob.rect.center) is True:
                    dispatcher.logicaaa().caught_mob(False)
                    mob_del_list.append(mob)
                    # создадим на основе этого моба красного моба, летящего в центр окна
                    self.create_mob_to_centre_from(mob, rect)

            for mob in mob_del_list:
                self.mobs.remove(mob)
                del mob

    # создать свободного моба, которого не поймали
    # он будет долетать до середины окна и уничтожаться
    # моб создается как продолжение моба, который столкнулся с окном
    def create_mob_to_centre_from(self, mob_as_sample, rect):
        pos_start = mob_as_sample.rect.center
        pos_stop = rect.center
        velocity = mob_as_sample.velocity
        mob_path = mob_as_sample.mob_path
        mob = Mob(self, velocity, pos_start, pos_stop, mob_path, self.all_mob_groups, None)
        mob_as_sample.last_show(False)
        mob.image = mob_as_sample.image
        mob.set_start()
        self.last_show_mobs.append(mob)


class StaticMap:
    def __init__(self, map_number):
        # грузим фон
        self.path = CURRENT_DIRECTORY + '/maps/' + str(map_number) + '.png'
        # базовый фон
        self.image = pygame.image.load(self.path)
        # фон с яркостью
        self.brightenImage = pygame.image.load(self.path)
        # ставим яркость по умолчанию
        self.brightness = dispatcher.session.brightness
        self.set_brightness(self.brightness)
        self.image_test = pygame.image.load(CURRENT_DIRECTORY + '/images/nuage.png')

    def load(self):
        pass

    def set_brightness(self, brightness):
        self.brightness = brightness
        if self.brightness >= len(BRIGHTEN):
            self.brightness = 0
        bright_color = (BRIGHTEN[self.brightness], BRIGHTEN[self.brightness], BRIGHTEN[self.brightness])
        self.brightenImage = pygame.image.load(self.path)
        self.brightenImage.fill(bright_color, special_flags=pygame.BLEND_RGB_SUB)

    def render(self, surface):
        # рисуем фон
        surface.blit(self.brightenImage, (0, 0))
        surface.blit(self.image_test, (100, 350))
