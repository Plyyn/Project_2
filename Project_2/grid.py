"""Этот модуль создает игровое поле"""

import pygame


block_size = 30
left_margin = 100
upper_margin = 30
size = (left_margin + 30*block_size, upper_margin+15*block_size)
# Буквы для обозначения столбцов
letters = ['A', 'B','C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
pygame.init()
BLACK = (0, 0, 0)
# Создание окна игры
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Морской бой")
font_size = int(block_size/1.5)
font = pygame.font.SysFont('Arial', font_size)


class Grid:
    def __init__(self, title, offset):
        self.title = title
        self.offset = offset
        self.draw_grid()
        self.sign_grids()
        self.add_nums_letters_to_grid()

    def draw_grid(self):
        """Рисуем вертикальные и горизонтальные линии для создания игровых полей"""
        for i in range(11):
            # Горизонтальные линии
            pygame.draw.line(screen, BLACK, (left_margin+self.offset, upper_margin+i*block_size), (left_margin +10*block_size+self.offset, upper_margin+i*block_size),  1)
            # Вертикальные линии
            pygame.draw.line(screen, BLACK, (left_margin+i*block_size +self.offset,upper_margin), (left_margin+i*block_size+self.offset, upper_margin+10*block_size),1 )

    def add_nums_letters_to_grid(self):
        """Функция для добавления цифр и букв в игровое поле"""
        for i in range(10):
            num_vert = font.render(str(i+1), False, BLACK)
            letters_hor = font.render(letters[i], False, BLACK)
            num_vert_width = num_vert.get_width()
            num_vert_height = num_vert.get_height()
            letters_hor_width = letters_hor.get_width()
            # Размещаем цифры
            screen.blit(num_vert, (left_margin-(block_size//2 +num_vert_width//2)+self.offset, upper_margin + i*block_size + (block_size//2 - num_vert_height//2)))
            # Размещаем буквы
            screen.blit(letters_hor, (left_margin +i*block_size +(block_size//2 - letters_hor_width//2)+self.offset, upper_margin +10*block_size))


    def sign_grids(self):
        """Функция для подписи поля компьютера и человека"""
        player = font.render(self.title, True, BLACK)
        sign_width = player.get_width()
        screen.blit(player, (left_margin + block_size * 5 - sign_width // 2+self.offset, upper_margin - block_size // 2 - font_size))
