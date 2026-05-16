import pygame
from utils import CELL_SIZE, BLUE, GOLD, RED, random_position


class Item:
    def __init__(self, color, value):
        self.position = random_position()
        self.color = color
        self.value = value

    def respawn(self, blocked_positions):
        while True:
            new_position = random_position()
            if new_position not in blocked_positions:
                self.position = new_position
                break

    def draw(self, screen):
        x, y = self.position
        center = (x + CELL_SIZE // 2, y + CELL_SIZE // 2)
        pygame.draw.circle(screen, self.color, center, CELL_SIZE // 2 - 1)
        pygame.draw.circle(screen, (255, 255, 255), center, CELL_SIZE // 2 - 2, 2)


class Food(Item):
    def __init__(self):
        self.regular_food_count = 0
        super().__init__(BLUE, 1)

    def respawn(self, blocked_positions):
        if self.regular_food_count >= 4:
            self.color = GOLD
            self.value = 5
            self.regular_food_count = 0
        else:
            self.color = BLUE
            self.value = 1
            self.regular_food_count += 1

        super().respawn(blocked_positions)


class Trap(Item):
    def __init__(self):
        super().__init__(RED, -3)
