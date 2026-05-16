import pygame
from utils import CELL_SIZE, GREEN, BLUE, SNAKE_YELLOW, SNAKE_HEAD_GLOW, WHITE


class Snake:
    def __init__(self):
        self.body = [(100, 100), (80, 100), (60, 100)]
        self.direction = (CELL_SIZE, 0)
        self.next_direction = self.direction
        self.grow_next = False
        self.direction_changed = False

    def change_direction(self, new_direction):
        if self.direction_changed:
            return

        opposite = (-self.direction[0], -self.direction[1])

        if new_direction != opposite:
            self.next_direction = new_direction
            self.direction_changed = True

    def move(self):
        self.direction = self.next_direction
        self.direction_changed = False

        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        self.body.insert(0, new_head)

        if self.grow_next:
            self.grow_next = False
        else:
            self.body.pop()

    def grow(self):
        self.grow_next = True

    def hit_self(self):
        return self.body[0] in self.body[1:]

    def occupied_positions(self):
        return set(self.body)

    def draw(self, screen):
        body_colors = [BLUE, BLUE, SNAKE_YELLOW, GREEN, GREEN, GREEN]

        for index, part in enumerate(self.body):
            x, y = part

            if index == 0:
                glow = pygame.Surface((CELL_SIZE * 3, CELL_SIZE * 3), pygame.SRCALPHA)
                pygame.draw.circle(
                    glow,
                    (*SNAKE_HEAD_GLOW, 60),
                    (CELL_SIZE + CELL_SIZE // 2, CELL_SIZE + CELL_SIZE // 2),
                    CELL_SIZE,
                )
                screen.blit(glow, (x - CELL_SIZE, y - CELL_SIZE))

            color = body_colors[min(index, len(body_colors) - 1)]

            if index == 0:
                center = (x + CELL_SIZE // 2, y + CELL_SIZE // 2)
                hex_points = [
                    (center[0], y - 5),
                    (x + CELL_SIZE + 5, y + 3),
                    (x + CELL_SIZE + 5, y + CELL_SIZE - 3),
                    (center[0], y + CELL_SIZE + 5),
                    (x - 5, y + CELL_SIZE - 3),
                    (x - 5, y + 3),
                ]
                pygame.draw.polygon(screen, (2, 35, 62), hex_points)
                pygame.draw.polygon(screen, BLUE, hex_points, 2)
                pygame.draw.polygon(
                    screen,
                    WHITE,
                    [
                        (center[0], center[1] - 7),
                        (center[0] + 7, center[1]),
                        (center[0], center[1] + 7),
                        (center[0] - 7, center[1]),
                    ],
                )
            else:
                pygame.draw.rect(screen, color, (x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2), border_radius=3)
