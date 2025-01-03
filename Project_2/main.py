import pygame
import random
import exceptions
import ships as sh
import grid


#цвета
WHITE = (255,255, 255)
BLACK = (0, 0, 0)
#Размеры игрового поля
block_size = 30
left_margin = 100
upper_margin = 30
size = (left_margin + 30*block_size, upper_margin+15*block_size)
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Морской бой")
#Шрифты и звуки
font_size = int(block_size/1.5)
font = pygame.font.SysFont('Arial', font_size)
game_over_font_size = 3*block_size
explosion_sound = pygame.mixer.Sound("resources/explosion.mp3")
win_sound = "resources/win_music.mp3"
lose_sound = "resources/lose_music.mp3"

#музыка и картинка для появления пирата
pirate_image = pygame.image.load("resources/pirate.png")
pirate_image = pygame.transform.scale(pirate_image, (150, 150))
pygame.mixer.init()
pirate_music = "resources/polundra-vykrik.mp3"

# Переменные для управления пиратом
pirate_visible = False
pirate_timer = 0
pirate_duration = 5000
# Наборы для хранения координат кораблей и точек
around_last_computer_hit_set = set()
computer_available_to_fire_set = {(x, y) for x in range (1,11) for y in range(1,11)}
hit_blocks = set()
dotted_set = set()
dotted_set_for_comp = set()
hit_blocks_for_comp_to_shoot =set()
last_hits_list =[]
destroyed_ships = []

def comp_shoots(set_to_shoot_from):
    """Выполняет ход компьютера, выбирая случайную клетку для выстрела из доступного множества"""
    pygame.time.delay(500)
    computer_fired_block = random.choice(tuple(set_to_shoot_from))#случайный выбор клетки
    computer_available_to_fire_set.discard(computer_fired_block)
    return check_hit_or_miss(computer_fired_block, sh.human_ships_working, True, True)

def determine_orientation(last_hits_list):
    """Определяет ориентацию корабля (горизонтальная или вертикальная) на основе попаданий"""
    if len(last_hits_list) < 2:
        return None  # Если попадание только одно, ориентация неизвестна
    # Берем первые два попадания
    x1, y1 = last_hits_list[0]
    x2, y2 = last_hits_list[1]
    if x1 == x2:
        return "vertical"  # Корабль вертикальный
    elif y1 == y2:
        return "horizontal"  # Корабль горизонтальный
    return None  # Если попадания не образуют прямую (на случай ошибки)

def check_hit_or_miss(fired_block, opponents_ships_list, computer_turn, diagonal_only):
    """Проверяет, попал ли выстрел в корабль или промахнулся"""
    for elem in opponents_ships_list:
        if fired_block in elem:
            ind = opponents_ships_list.index(elem)
            elem.remove(fired_block)
            if not elem:  # Если корабль уничтожен
                explosion_sound.play()
                draw_destroyed_ships(ind, opponents_ships_list, computer_turn, diagonal_only=False)
                if opponents_ships_list == sh.computer_ships_working:
                    sh.computer.ships_set -= 1
                elif opponents_ships_list == sh.human_ships_working:
                    sh.human.ships_set -= 1
                if computer_turn:
                    last_hits_list.clear()
                    around_last_computer_hit_set.clear()
                return True
            # Если корабль не уничтожен
            update_hit_blocks(fired_block, computer_turn)
            if computer_turn:
                last_hits_list.append(fired_block)  # Добавляем попадание
                update_around_last_computer_hit(fired_block, computer_hits=True)
            return True

    # Если промах
    put_dot_on_missed_block(fired_block, computer_turn)
    if computer_turn:
        update_around_last_computer_hit(fired_block, computer_hits=False)
    return False

def update_hit_blocks(fired_block, computer_turn):
    """Обновляет множество попаданий"""
    x, y = fired_block
    if computer_turn:
        x += 15  # Сдвиг для поля компьютера
        hit_blocks_for_comp_to_shoot.add((x - 15, y))  # Добавляем в поле компьютера
    hit_blocks.add((x, y))

def put_dot_on_missed_block(fired_block, computer_turn = False):
    """Устанавливает точку в клетке, где был промах"""
    if not computer_turn:
        dotted_set.add(fired_block)
    else:
        dotted_set.add((fired_block[0]+15, fired_block[1]))
        dotted_set_for_comp.add(fired_block)


def draw_destroyed_ships(ind, opponents_ships_list, computer_turn, diagonal_only=False):
    """Обновляет точки вокруг уничтоженного корабля"""
    if opponents_ships_list == sh.computer_ships_working:
        ships_list = sh.computer.ships
    elif opponents_ships_list == sh.human_ships_working:
        ships_list = sh.human.ships
    ship = sorted(ships_list[ind])

    # Добавляем точки вокруг всех клеток корабля
    for block in ship:
        update_dotted_and_hit_sets(block, computer_turn, diagonal_only)


def update_around_last_computer_hit(fired_block, computer_hits=True):
    """Обновляет набор клеток вокруг последнего попадания компьютера"""
    global around_last_computer_hit_set, computer_available_to_fire_set

    if computer_hits:  # Если компьютер попал
        if len(last_hits_list) > 1:  # Если больше одного попадания, проверяем ориентацию
            around_last_computer_hit_set = computer_hits_twice()
        else:  # Если это первое попадание, добавляем все соседние клетки
            x_hit, y_hit = fired_block
            if 1 < x_hit:
                around_last_computer_hit_set.add((x_hit - 1, y_hit))  # Слева
            if x_hit < 10:
                around_last_computer_hit_set.add((x_hit + 1, y_hit))  # Справа
            if 1 < y_hit:
                around_last_computer_hit_set.add((x_hit, y_hit - 1))  # Сверху
            if y_hit < 10:
                around_last_computer_hit_set.add((x_hit, y_hit + 1))  # Снизу
    else:  # Если промах
        around_last_computer_hit_set.discard(fired_block)

    # Убираем из наборов клетки, которые уже недоступны
    around_last_computer_hit_set -= dotted_set_for_comp
    around_last_computer_hit_set -= hit_blocks_for_comp_to_shoot
    computer_available_to_fire_set -= around_last_computer_hit_set
    computer_available_to_fire_set -= dotted_set_for_comp

def computer_hits_twice():
    """Формирует множество клеток для следующего выстрела компьютера,
    если он дважды подряд попал в один корабль"""
    last_hits_list.sort()
    new_around_last_hit_set = set()
    orientation = determine_orientation(last_hits_list)  # Определяем ориентацию корабля

    # Перебираем последние попадания
    for i in range(len(last_hits_list) - 1):
        x1, y1 = last_hits_list[i]
        x2, y2 = last_hits_list[i + 1]
        # Если ориентация вертикальная
        if orientation == "vertical":
            if 1 < y1:
                new_around_last_hit_set.add((x1, y1 - 1))  # Сверху
            if y2 < 10:
                new_around_last_hit_set.add((x1, y2 + 1))  # Снизу
        # Если ориентация горизонтальная
        elif orientation == "horizontal":
            if 1 < x1:
                new_around_last_hit_set.add((x1 - 1, y1))  # Слева
            if x2 < 10:
                new_around_last_hit_set.add((x2 + 1, y1))  # Справа
        # Если ориентация еще не определена (может быть после одного попадания)
        else:
            if 1 < x1:
                new_around_last_hit_set.add((x1 - 1, y1))  # Слева
            if x2 < 10:
                new_around_last_hit_set.add((x2 + 1, y1))  # Справа
            if 1 < y1:
                new_around_last_hit_set.add((x1, y1 - 1))  # Сверху
            if y2 < 10:
                new_around_last_hit_set.add((x1, y2 + 1))  # Снизу
    return new_around_last_hit_set

def update_dotted_and_hit_sets(fired_block, computer_turn, diagonal_only):
    """Функция, обновляющая множества попаданий и промахов"""
    global dotted_set
    x, y = fired_block
    a, b = 0, 11

    # Если это ход компьютера, сдвигаем координаты для его поля
    if computer_turn:
        x += 15
        a += 15
        b += 15
        hit_blocks_for_comp_to_shoot.add(fired_block)

    hit_blocks.add((x, y))

    # Проверяем клетки вокруг выстрела
    for i in range(-1, 2):
        for j in range(-1, 2):
            # Добавляем все соседние клетки (включая диагональные)
            if a < x + i < b and 0 < y + j < 11:
                dotted_set.add((x + i, y + j))
                if computer_turn:
                    dotted_set_for_comp.add((fired_block[0] + i, y + j))

    # Убираем из множества точки, которые уже заняты попаданиями
    dotted_set -= hit_blocks

def draw_from_dotted_set(dotted_set):
    """Рисует точки в клетках, где были промахи"""
    for elem in dotted_set:
        pygame.draw.circle(
            screen, BLACK,
            (left_margin + (elem[0] - 1) * block_size + block_size // 2,
             upper_margin + (elem[1] - 1) * block_size + block_size // 2),
            block_size // 6
        )
def draw_hit_blocks(hit_blocks):
    """Рисует кресты в клетках, куда были попадания"""
    for block in hit_blocks:
        x1 = block_size*(block[0]-1) +left_margin
        y1 = block_size*(block[1]-1) +upper_margin
        pygame.draw.line(screen, BLACK,(x1, y1),(x1 +block_size, y1+block_size), block_size//6)
        pygame.draw.line(screen, BLACK, (x1, y1+block_size),(x1+block_size,y1), block_size//6)

def display_game_result(message, sound_file):
    """
    Отображает экран с результатом игры и воспроизводит звук
    """
    screen.fill(WHITE)
    game_over_font = pygame.font.Font(None, game_over_font_size)
    text = game_over_font.render(message, True, (0, 0, 0))
    screen.blit(text, (300, 125))
    pygame.display.update()
    # Воспроизводим звук
    pygame.mixer.music.stop()  # Останавливаем текущую музыку
    pygame.mixer.music.load(sound_file)  # Загружаем звук для результата игры
    pygame.mixer.music.play()
    # Ждем завершения звука без блокировки
    clock = pygame.time.Clock()
    while pygame.mixer.music.get_busy():  # Пока музыка играет
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        clock.tick(60)  # Ограничиваем FPS

def main():
    global fired_block
    global pirate_visible, pirate_timer
    global pirate_appeared
    pirate_appeared = False
    clock = pygame.time.Clock()
    game_over = False
    computer_turn = False
    screen.fill(WHITE)
    computer_grid = grid.Grid("Computer", 0)#Поле для компьютера
    human_grid =grid.Grid("Human", 15*block_size)#Поле для игрока
    #sh.draw_ships(sh.computer.ships, is_human=False)
    sh.draw_ships(sh.human.ships, is_human= True)
    pygame.display.update()
    #Основной цикл игры
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif not computer_turn and event.type == pygame.MOUSEBUTTONDOWN:# Если ход игрока
                x, y = event.pos# Получаем координаты клика
                # Проверяем, попал ли клик в поле противника
                if (left_margin <= x <= left_margin +10*block_size) and (upper_margin <= y <= upper_margin + 10*block_size):
                    fired_block = ((x - left_margin)//block_size + 1, (y - upper_margin) // block_size + 1)
                    # Проверяем, попал ли выстрел в корабль и меняем ход (если промах, ход передается компьютеру)
                    computer_turn = not check_hit_or_miss(fired_block,sh.computer_ships_working, computer_turn, True)
                else:
                    # Если игрок выстрелил за пределы поля, выбрасываем исключение
                    raise exceptions.ShootInWrongAreaException("Вы не можете стрелять за пределами поля противника")
        if computer_turn: # Ход компьютера
            if around_last_computer_hit_set:# Если компьютер ранее попал в корабль, он стреляет рядом
                computer_turn = comp_shoots(around_last_computer_hit_set)
            else:# Если нет предыдущих попаданий, компьютер стреляет случайно
                computer_turn = comp_shoots(computer_available_to_fire_set)
        #Выводим экран выигрыша, если у компьютера закончились целые корабли
        if sh.computer.ships_set == 0:  # Выигрыш игрока
            display_game_result("YOU WIN!", win_sound)
            game_over = True
            break
        elif sh.human.ships_set == 0:  # Проигрыш игрока
            display_game_result("YOU LOST", lose_sound)
            game_over = True
            break
        #Реализуем появление пирата в случайный момент времени
        if not pirate_visible and not pirate_appeared and random.randint(1, 1000) == 1:
            pirate_visible = True
            pirate_appeared = True
            pirate_timer = pygame.time.get_ticks()  # Запоминаем время появления пирата
            pygame.mixer.music.load(pirate_music)
            pygame.mixer.music.play()

            # Если пират виден, отображаем его на экране
        if pirate_visible:
            screen.blit(pirate_image, (4*block_size // 2 + 335, 4*block_size // 2 + 125))  # Рисуем пирата в центре экрана

            # Проверяем, нужно ли убрать пирата
            if pygame.time.get_ticks() - pirate_timer > pirate_duration:
                pirate_visible = False
                pygame.mixer.music.stop()

        pygame.display.update()  # Обновляем экран
        clock.tick(60)
        # Отрисовка промахов, попаданий и уничтоженных кораблей
        draw_from_dotted_set(dotted_set)
        draw_hit_blocks(hit_blocks)
        sh.draw_ships(destroyed_ships)
        pygame.display.update()

main()
pygame.quit()

