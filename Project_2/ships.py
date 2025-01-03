"""Этот модуль создает логику появления кораблей на игровом поле"""

import pygame
import random
import copy
import exceptions

#Изображения кораблей
ship_images = {
    1: pygame.image.load("resources/ship_1.png"),
    2: pygame.image.load("resources/ship_2.png"),
    3: pygame.image.load("resources/ship_3.png"),
    4: pygame.image.load("resources/ship_4.png")
}
#Параметры игрового поля
block_size = 30
left_margin = 100
upper_margin = 30
size = (left_margin + 30*block_size, upper_margin+15*block_size)
screen = pygame.display.set_mode(size)
# Масштабирование изображений кораблей
for size, image in ship_images.items():
    ship_images[size] = pygame.transform.scale(image, (block_size * size, block_size))

class Ships:
    """Класс для генерации и управления кораблями на игровом поле"""
    def __init__(self):
        self.available_blocks = {(a, b) for a in range(1, 11) for b in range(1, 11)}  # Доступные клетки для расстановки
        self.ships_set = set()  # Клетки, занятые кораблями
        self.ships = []  # Список с координатами кораблей
        self.populate_grid()  # Расставляем корабли

    def create_start_block(self):
        """Выбираем клетку, с которой начнем рисовать корабли"""
        x_or_y = random.randint(0, 1)
        str_rev = random.choice((-1, 1))#направление(прямо или в обратном направлении)
        x, y = random.choice(tuple(self.available_blocks))
        return x, y, x_or_y, str_rev

    def create_ship(self, num_of_blocks):
        """Создает корабль с заданным количеством палуб"""
        ship_coordinates = []
        x, y, x_or_y, str_rev = self.create_start_block()
        for _ in range(num_of_blocks):
            ship_coordinates.append((x, y))
            if not x_or_y:# Горизонтальное размещение
                if (x <= 1 and str_rev == -1) or (x >= 10 and str_rev == 1):# Проверка выхода за границы
                    str_rev *= -1# Меняем направление
                    x = ship_coordinates[0][0] + str_rev
                else:
                    x = ship_coordinates[-1][0] + str_rev
            else:# Вертикальное размещение
                if (y <= 1 and str_rev == -1) or (y >= 10 and str_rev == 1):
                    str_rev *= -1
                    y = ship_coordinates[0][1] + str_rev
                else:
                    y = ship_coordinates[-1][1] + str_rev
        # Проверяем, корректно ли размещен корабль
        if self.is_ship_valid(ship_coordinates):
            return ship_coordinates
        return self.create_ship(num_of_blocks)

    def is_ship_valid(self, new_ship):
        """Проверяет, можно ли разместить новый корабль (без пересечений и соприкосновений)"""
        for x, y in new_ship:
            for k in range(-1, 2):
                for m in range(-1, 2):
                    if (x + k, y + m) in self.ships_set:
                        return False
        return True

    def add_new_ship_to_set(self, new_ship):
        """ Добавляет клетки нового корабля в множество занятых клеток"""
        for elem in new_ship:
            self.ships_set.add(elem)

    def update_available_blocks_for_creating_ships(self, new_ship):
        """Обновляет множество доступных клеток для размещения кораблей,
        исключая клетки, занятые новым кораблем, и клетки вокруг него"""
        for elem in new_ship:
            for k in range(-1, 2):
                for m in range(-1, 2):
                    if 1 <= (elem[0] + k) <= 10 and 1 <= (elem[1] + m) <= 10:
                        self.available_blocks.discard((elem[0] + k, elem[1] + m))

    def populate_grid(self):
        """Расставляет корабли на игровом поле"""
        ships_coordinates_list = []
        for num_of_blocks in range(4, 0, -1):
            for _ in range(5 - num_of_blocks):
                try:
                    new_ship = self.create_ship(num_of_blocks)
                    if not self.is_ship_valid(new_ship):
                        raise exceptions.ShipOverlapException("Корабли пересекаются или соприкасаются!")
                    ships_coordinates_list.append(new_ship)
                    self.add_new_ship_to_set(new_ship)
                    self.update_available_blocks_for_creating_ships(new_ship)
                except exceptions.ShipOverlapException as e:
                    print(f"Ошибка: {e}")
                    continue
        self.ships = ships_coordinates_list  # Сохраняем корабли в атрибут
        return ships_coordinates_list
computer = Ships()
human = Ships()
human_ships_working = copy.deepcopy(human.ships)
computer_ships_working = copy.deepcopy(computer.ships)
human.ships_set = len(human.ships)# Устанавливаем начальное количество кораблей
computer.ships_set = len(computer.ships)
def draw_ships(ships_coordinates_list, is_human=True):
    """Рисует корабли на игровом поле"""
    for elem in ships_coordinates_list:
        ship = sorted(elem)
        x_start = ship[0][0]
        y_start = ship[0][1]
        ship_length = len(ship)

        x = block_size * (x_start - 1) + left_margin
        y = block_size * (y_start - 1) + upper_margin
        if is_human:# Если корабли игрока, сдвигаем их на другую половину поля
            x += 15* block_size
        # Проверяем ориентацию корабля (горизонтальная или вертикальная)
        if ship_length > 1 and x_start == ship[1][0]:  # Вертикальный корабль
            rotated_image = pygame.transform.rotate(ship_images[ship_length], 90)
            screen.blit(rotated_image, (x, y))
        else:  # Горизонтальный корабль
            screen.blit(ship_images[ship_length], (x, y))

