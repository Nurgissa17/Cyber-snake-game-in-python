import random
import pygame

from snake import Snake
from items import Food, Trap
from score_manager import ScoreManager
from utils import WIDTH, HEIGHT, CELL_SIZE, BLACK, WHITE, GRAY, RED, GRID_LINE, GRID_GLOW, PLAY_MIN_X, PLAY_MIN_Y, PLAY_MAX_X, PLAY_MAX_Y, log_action


class Game:
    MAX_SCORE = 20

    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Cyber Snake: Data Escape")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 28)
        self.title_font = pygame.font.SysFont("Arial Black", 68)
        self.subtitle_font = pygame.font.SysFont("Consolas", 28)
        self.menu_font = pygame.font.SysFont("Consolas", 26, bold=True)

        self.score_manager = ScoreManager()
        self.player_name = "Player"
        self.speed_options = list(range(1, 15))
        self.speed_index = 7
        self.speed_gain_options = list(range(0, 6))
        self.speed_gain_index = 1

        self.reset_game()

    def reset_game(self):
        self.snake = Snake()
        self.food = Food()
        self.traps = [Trap() for _ in range(12)]

        self.score = 0
        self.speed = self.speed_options[self.speed_index]

        self.running = True
        self.game_over = False
        self.game_won = False
        self.paused = False
        self.score_saved = False

        self.place_all_items()

    def place_all_items(self):
        blocked = self.snake.occupied_positions()

        self.food.respawn(blocked)
        blocked.add(self.food.position)

        for index, trap in enumerate(self.traps):
            self.respawn_trap_spread(trap, blocked, index)
            blocked.add(trap.position)

    def respawn_trap_spread(self, trap, blocked, zone_index):
        columns = 4
        rows = 2
        zone_count = columns * rows
        zone = zone_index % zone_count
        column = zone % columns
        row = zone // columns
        zone_width = (PLAY_MAX_X - PLAY_MIN_X) / columns
        zone_height = (PLAY_MAX_Y - PLAY_MIN_Y) / rows
        min_x = PLAY_MIN_X + column * zone_width
        max_x = PLAY_MIN_X + (column + 1) * zone_width
        min_y = PLAY_MIN_Y + row * zone_height
        max_y = PLAY_MIN_Y + (row + 1) * zone_height

        candidates = []
        for x in range(PLAY_MIN_X, PLAY_MAX_X, CELL_SIZE):
            for y in range(PLAY_MIN_Y, PLAY_MAX_Y, CELL_SIZE):
                position = (x, y)
                if position in blocked:
                    continue
                if min_x <= x < max_x and min_y <= y < max_y:
                    candidates.append(position)

        if not candidates:
            trap.respawn(blocked)
            return

        trap.position = random.choice(candidates)

    def add_traps(self, amount):
        for _ in range(amount):
            new_trap = Trap()
            blocked = self.snake.occupied_positions()
            blocked.add(self.food.position)
            blocked.update(trap.position for trap in self.traps)
            self.respawn_trap_spread(new_trap, blocked, len(self.traps))
            self.traps.append(new_trap)

    def draw_text(self, text, x, y, color=WHITE):
        rendered = self.font.render(text, True, color)
        self.screen.blit(rendered, (x, y))

    def draw_background(self):
        self.screen.fill((2, 7, 18))

        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, (4, 32, 68), (x + 1, 0), (x + 1, HEIGHT))
            pygame.draw.line(self.screen, GRID_LINE, (x, 0), (x, HEIGHT))

        for y in range(0, HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, (4, 32, 68), (0, y + 1), (WIDTH, y + 1))
            pygame.draw.line(self.screen, GRID_LINE, (0, y), (WIDTH, y))

        self.draw_gameplay_frame()

    def draw_gameplay_frame(self):
        cyan = (0, 190, 255)
        bright_cyan = (0, 230, 255)
        frame = [
            (22, 80), (22, 34), (46, 14), (150, 14), (170, 26), (630, 26),
            (650, 14), (754, 14), (778, 34), (778, 80), (790, 96), (790, 508),
            (778, 524), (778, 566), (754, 586), (650, 586), (630, 574),
            (170, 574), (150, 586), (46, 586), (22, 566), (22, 524),
            (10, 508), (10, 96)
        ]
        pygame.draw.lines(self.screen, cyan, True, frame, 3)
        pygame.draw.lines(self.screen, (0, 88, 140), True, [(x + 12, y + 12) for x, y in frame], 1)

        for x in range(360, 440, 14):
            pygame.draw.line(self.screen, cyan, (x, 20), (x + 8, 20), 5)
            pygame.draw.line(self.screen, cyan, (x, 580), (x + 8, 580), 5)

        for y in range(250, 350, 24):
            pygame.draw.line(self.screen, cyan, (16, y), (16, y + 16), 5)
            pygame.draw.line(self.screen, cyan, (784, y), (784, y + 16), 5)

        play_rect = pygame.Rect(PLAY_MIN_X, PLAY_MIN_Y, PLAY_MAX_X - PLAY_MIN_X, PLAY_MAX_Y - PLAY_MIN_Y)
        glow = pygame.Surface((play_rect.width + 18, play_rect.height + 18), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*bright_cyan, 55), glow.get_rect(), 8)
        self.screen.blit(glow, (play_rect.x - 9, play_rect.y - 9))
        pygame.draw.rect(self.screen, (1, 18, 36), play_rect, 6)
        pygame.draw.rect(self.screen, bright_cyan, play_rect, 3)
        pygame.draw.rect(self.screen, (120, 245, 255), play_rect.inflate(-8, -8), 1)

    def draw_gameplay_hud(self):
        label_font = pygame.font.SysFont("Consolas", 16, bold=True)
        value_font = pygame.font.SysFont("Consolas", 24, bold=True)

        self.draw_bottom_hud_box(WIDTH - 184, 548, 126, "SCORE", str(self.score), label_font, value_font)

    def draw_bottom_hud_box(self, x, y, width, label, value, label_font, value_font):
        cyan = (0, 220, 255)
        height = 42
        points = [
            (x + 8, y), (x + width - 8, y), (x + width, y + 8),
            (x + width, y + height - 8), (x + width - 8, y + height),
            (x + 8, y + height), (x, y + height - 8), (x, y + 8)
        ]

        pygame.draw.polygon(self.screen, (3, 15, 28), points)
        pygame.draw.lines(self.screen, cyan, True, points, 1)

        label_text = label_font.render(label, True, WHITE)
        value_text = value_font.render(value, True, cyan)
        self.screen.blit(label_text, (x + 12, y + 5))
        self.screen.blit(value_text, (x + 12, y + 18))

    def draw_glow_text(self, text, font, center, color, glow_color):
        for offset in (5, 3):
            glow = font.render(text, True, glow_color)
            glow.set_alpha(70)
            rect = glow.get_rect(center=center)
            self.screen.blit(glow, (rect.x - offset, rect.y))
            self.screen.blit(glow, (rect.x + offset, rect.y))
            self.screen.blit(glow, (rect.x, rect.y - offset))
            self.screen.blit(glow, (rect.x, rect.y + offset))

        rendered = font.render(text, True, color)
        self.screen.blit(rendered, rendered.get_rect(center=center))

    def draw_menu_background(self):
        self.screen.fill((2, 8, 14))

        for radius in range(90, 360, 34):
            rect = pygame.Rect(0, 0, radius * 2, radius * 2)
            rect.center = (WIDTH // 2, 260)
            pygame.draw.arc(self.screen, (0, 72, 74), rect, 0.25, 5.8, 1)

        for x in range(0, WIDTH, 40):
            pygame.draw.line(self.screen, (0, 75, 55), (x, HEIGHT), (WIDTH // 2, 430), 1)
        for y in range(430, HEIGHT, 24):
            pygame.draw.line(self.screen, (0, 135, 80), (0, y), (WIDTH, y), 1)

        neon = (150, 255, 38)
        cyan = (0, 220, 255)
        frame_points = [
            (16, 82), (16, 36), (36, 16), (210, 16), (230, 28),
            (570, 28), (590, 16), (764, 16), (784, 36), (784, 82)
        ]
        pygame.draw.lines(self.screen, neon, False, frame_points, 2)
        pygame.draw.lines(self.screen, neon, False, [(16, 518), (16, 564), (36, 584), (190, 584), (210, 572)], 2)
        pygame.draw.lines(self.screen, neon, False, [(784, 518), (784, 564), (764, 584), (610, 584), (590, 572)], 2)

        for y in range(205, 380, 24):
            pygame.draw.rect(self.screen, (0, 90, 45), (30, y, 12, 12), 1)
            pygame.draw.rect(self.screen, (0, 90, 45), (758, y, 12, 12), 1)

        for x in range(60, WIDTH, 65):
            pygame.draw.circle(self.screen, (80, 255, 40), (x, 500 + (x % 3) * 16), 2)
        pygame.draw.line(self.screen, cyan, (250, 185), (338, 185), 2)
        pygame.draw.line(self.screen, cyan, (462, 185), (550, 185), 2)

    def draw_menu_title(self):
        self.draw_glow_text("CYBER", self.title_font, (278, 132), WHITE, (0, 210, 255))
        self.draw_glow_text("SNAKE", self.title_font, (526, 132), (158, 255, 31), (120, 255, 30))
        self.draw_glow_text("D A T A   E S C A P E", self.subtitle_font, (400, 190), WHITE, (0, 210, 255))

    def draw_menu_button(self, y, text_parts, accent, icon):
        x = 150
        width = 500
        height = 60
        icon_width = 76
        points = [
            (x + 12, y), (x + width - 8, y), (x + width, y + 8),
            (x + width, y + height - 8), (x + width - 8, y + height),
            (x + 12, y + height), (x, y + height - 10), (x, y + 10)
        ]

        glow = pygame.Surface((width + 24, height + 24), pygame.SRCALPHA)
        pygame.draw.polygon(glow, (*accent, 34), [(px - x + 12, py - y + 12) for px, py in points])
        self.screen.blit(glow, (x - 12, y - 12))
        pygame.draw.polygon(self.screen, (3, 20, 24), points)
        pygame.draw.lines(self.screen, accent, True, points, 2)
        pygame.draw.line(self.screen, accent, (x + icon_width, y), (x + icon_width, y + height), 1)

        icon_center = (x + icon_width // 2, y + height // 2)
        if icon == "play":
            pygame.draw.polygon(
                self.screen,
                accent,
                [(icon_center[0] - 13, icon_center[1] - 18), (icon_center[0] - 13, icon_center[1] + 18), (icon_center[0] + 18, icon_center[1])],
                4,
            )
        elif icon == "leaderboard":
            pygame.draw.rect(self.screen, accent, (icon_center[0] - 22, icon_center[1] + 6, 14, 13), 2)
            pygame.draw.rect(self.screen, accent, (icon_center[0] - 7, icon_center[1] - 8, 14, 27), 2)
            pygame.draw.rect(self.screen, accent, (icon_center[0] + 8, icon_center[1] + 1, 14, 18), 2)
            self.draw_tiny_text("2", icon_center[0] - 18, icon_center[1] + 5, accent)
            self.draw_tiny_text("1", icon_center[0] - 2, icon_center[1] - 9, accent)
            self.draw_tiny_text("3", icon_center[0] + 13, icon_center[1], accent)
        elif icon == "power":
            pygame.draw.circle(self.screen, accent, icon_center, 18, 4)
            pygame.draw.line(self.screen, accent, (icon_center[0], icon_center[1] - 24), (icon_center[0], icon_center[1] - 4), 4)
        elif icon == "settings":
            pygame.draw.circle(self.screen, accent, icon_center, 19, 3)
            pygame.draw.circle(self.screen, accent, icon_center, 6, 2)
            for dx, dy in [(0, -25), (0, 25), (-25, 0), (25, 0)]:
                pygame.draw.line(self.screen, accent, icon_center, (icon_center[0] + dx, icon_center[1] + dy), 3)

        text_x = x + icon_width + 26
        max_text_width = x + width - 22 - text_x
        font_size = 26
        while font_size > 18:
            font = pygame.font.SysFont("Consolas", font_size, bold=True)
            total_width = sum(font.render(text, True, color).get_width() for text, color in text_parts)
            if total_width <= max_text_width:
                break
            font_size -= 1

        cursor = text_x
        for text, color in text_parts:
            rendered = font.render(text, True, color)
            self.screen.blit(rendered, (cursor, y + 18))
            cursor += rendered.get_width()

    def draw_tiny_text(self, text, x, y, color):
        font = pygame.font.SysFont("Consolas", 13, bold=True)
        rendered = font.render(text, True, color)
        self.screen.blit(rendered, (x, y))

    def draw_menu_snake(self):
        green = (135, 255, 30)
        dark_green = (5, 52, 20)
        body_points = [(610, 555), (650, 522), (714, 530), (758, 488), (730, 452), (668, 472), (638, 518)]
        pygame.draw.lines(self.screen, green, False, body_points, 24)
        pygame.draw.lines(self.screen, dark_green, False, body_points, 16)
        pygame.draw.circle(self.screen, green, (650, 515), 24, 3)
        pygame.draw.circle(self.screen, green, (620, 538), 20, 3)
        pygame.draw.polygon(self.screen, dark_green, [(575, 455), (625, 430), (665, 455), (624, 488)])
        pygame.draw.polygon(self.screen, green, [(575, 455), (625, 430), (665, 455), (624, 488)], 3)
        pygame.draw.circle(self.screen, green, (615, 455), 5)
        pygame.draw.line(self.screen, green, (570, 472), (548, 490), 2)
        pygame.draw.line(self.screen, green, (590, 483), (575, 506), 2)

    def draw_main_menu(self):
        green = (150, 255, 38)
        cyan = (0, 220, 255)

        self.draw_menu_background()
        self.draw_menu_title()
        self.draw_menu_button(220, [("PRESS ", WHITE), ("ENTER", green), (" TO START", WHITE)], green, "play")
        self.draw_menu_button(290, [("PRESS ", WHITE), ("L", cyan), (" FOR LEADERBOARD", WHITE)], cyan, "leaderboard")
        self.draw_menu_button(360, [("PRESS ", WHITE), ("S", cyan), (" FOR SETTINGS", WHITE)], cyan, "settings")
        self.draw_menu_button(430, [("PRESS ", WHITE), ("ESC", green), (" TO EXIT", WHITE)], green, "power")
        self.draw_menu_snake()

    def draw_speed_selector(self):
        cyan = (0, 220, 255)
        green = (150, 255, 38)
        small_font = pygame.font.SysFont("Consolas", 19, bold=True)
        speed_font = pygame.font.SysFont("Consolas", 24, bold=True)
        speed = self.speed_options[self.speed_index]
        x = 250
        y = 480
        width = 300
        height = 88
        points = [
            (x + 12, y), (x + width - 12, y), (x + width, y + 12),
            (x + width, y + height - 12), (x + width - 12, y + height),
            (x + 12, y + height), (x, y + height - 12), (x, y + 12)
        ]

        pygame.draw.polygon(self.screen, (3, 18, 26), points)
        pygame.draw.lines(self.screen, cyan, True, points, 2)

        label = small_font.render("SNAKE SPEED", True, WHITE)
        left_arrow = speed_font.render("<", True, cyan)
        value = speed_font.render(str(speed), True, green)
        right_arrow = speed_font.render(">", True, cyan)
        hint = small_font.render("LEFT / RIGHT", True, cyan)

        self.screen.blit(label, label.get_rect(center=(x + width // 2, y + 22)))
        self.screen.blit(left_arrow, left_arrow.get_rect(center=(x + 78, y + 50)))
        self.screen.blit(value, value.get_rect(center=(x + width // 2, y + 50)))
        self.screen.blit(right_arrow, right_arrow.get_rect(center=(x + width - 78, y + 50)))
        self.screen.blit(hint, hint.get_rect(center=(x + width // 2, y + 72)))

    def draw_settings_row(self, y, label, value, selected):
        cyan = (0, 220, 255)
        green = (150, 255, 38)
        accent = green if selected else cyan
        font = pygame.font.SysFont("Consolas", 24, bold=True)
        label_font = pygame.font.SysFont("Consolas", 20, bold=True)
        x = 190
        width = 420
        height = 64
        points = [
            (x + 12, y), (x + width - 12, y), (x + width, y + 12),
            (x + width, y + height - 12), (x + width - 12, y + height),
            (x + 12, y + height), (x, y + height - 12), (x, y + 12)
        ]

        pygame.draw.polygon(self.screen, (3, 18, 26), points)
        pygame.draw.lines(self.screen, accent, True, points, 2)
        self.screen.blit(label_font.render(label, True, WHITE), (x + 28, y + 20))
        self.screen.blit(font.render("<", True, cyan), (x + 260, y + 18))
        value_text = font.render(str(value), True, green)
        self.screen.blit(value_text, value_text.get_rect(center=(x + 330, y + height // 2)))
        self.screen.blit(font.render(">", True, cyan), (x + 382, y + 18))

    def draw_settings_screen(self, selected_setting):
        cyan = (0, 220, 255)
        green = (150, 255, 38)
        small = pygame.font.SysFont("Consolas", 18, bold=True)

        self.draw_menu_background()
        self.draw_glow_text("SETTINGS", self.title_font, (400, 145), WHITE, cyan)
        self.draw_settings_row(245, "START SPEED", self.speed_options[self.speed_index], selected_setting == 0)
        self.draw_settings_row(325, "FOOD SPEED +", self.speed_gain_options[self.speed_gain_index], selected_setting == 1)

        hint = [
            ("UP / DOWN", green),
            (" SELECT    ", WHITE),
            ("LEFT / RIGHT", cyan),
            (" CHANGE", WHITE),
        ]
        cursor = 170
        for text, color in hint:
            rendered = small.render(text, True, color)
            self.screen.blit(rendered, (cursor, 430))
            cursor += rendered.get_width()

        self.draw_return_button()

    def draw_leaderboard_title(self):
        leader_width = self.title_font.render("LEADER", True, WHITE).get_width()
        board_width = self.title_font.render("BOARD", True, WHITE).get_width()
        gap = 12
        start_x = WIDTH // 2 - (leader_width + board_width + gap) // 2

        self.draw_glow_text("LEADER", self.title_font, (start_x + leader_width // 2, 92), WHITE, (0, 210, 255))
        self.draw_glow_text(
            "BOARD",
            self.title_font,
            (start_x + leader_width + gap + board_width // 2, 92),
            (150, 255, 38),
            (120, 255, 30),
        )

    def draw_leaderboard_frame(self):
        cyan = (0, 190, 255)
        green = (150, 255, 38)

        self.screen.fill((2, 7, 18))

        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, (4, 30, 70), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, (4, 30, 70), (0, y), (WIDTH, y))

        frame = [
            (42, 34), (70, 16), (160, 16), (175, 26), (625, 26), (640, 16), (730, 16), (758, 34),
            (782, 60), (782, 540), (758, 566), (730, 584), (640, 584), (625, 574), (175, 574),
            (160, 584), (70, 584), (42, 566), (18, 540), (18, 60)
        ]
        pygame.draw.lines(self.screen, cyan, True, frame, 3)
        pygame.draw.lines(self.screen, (0, 90, 150), True, [(p[0] + 12, p[1] + 12) for p in frame], 1)

        for x in range(360, 440, 14):
            pygame.draw.line(self.screen, green, (x, 22), (x + 7, 22), 5)
            pygame.draw.line(self.screen, green, (x, 578), (x + 7, 578), 5)

        for y in range(210, 390, 26):
            pygame.draw.line(self.screen, green, (18, y), (18, y + 16), 4)
            pygame.draw.line(self.screen, green, (782, y), (782, y + 16), 4)

    def draw_leaderboard_row(self, rank, name, score, y):
        cyan = (0, 220, 255)
        green = (150, 255, 38)
        x = 155
        width = 490
        height = 42

        points = [
            (x + 10, y), (x + width - 8, y), (x + width, y + 8),
            (x + width, y + height - 8), (x + width - 8, y + height),
            (x + 10, y + height), (x, y + height - 8), (x, y + 8)
        ]
        pygame.draw.polygon(self.screen, (3, 14, 28), points)
        pygame.draw.lines(self.screen, cyan, True, points, 1)
        pygame.draw.line(self.screen, (0, 75, 105), (x + 58, y + 5), (x + width - 24, y + 5), 1)
        pygame.draw.line(self.screen, (0, 75, 105), (x + 58, y + height - 6), (x + width - 24, y + height - 6), 1)

        rank_text = self.menu_font.render(f"{rank}.", True, cyan)
        name_text = self.menu_font.render(str(name)[:14], True, WHITE)
        score_text = self.menu_font.render(str(score), True, green)

        self.screen.blit(rank_text, (x + 28, y + 8))
        self.screen.blit(name_text, (x + 82, y + 8))
        self.screen.blit(score_text, (x + width - 48 - score_text.get_width() // 2, y + 8))

    def draw_return_button(self):
        cyan = (0, 220, 255)
        x = 205
        y = 512
        width = 390
        height = 58
        icon_width = 80
        points = [
            (x + 12, y), (x + width - 10, y), (x + width, y + 10),
            (x + width, y + height - 10), (x + width - 10, y + height),
            (x + 12, y + height), (x, y + height - 10), (x, y + 10)
        ]

        pygame.draw.polygon(self.screen, (3, 15, 28), points)
        pygame.draw.lines(self.screen, cyan, True, points, 2)
        pygame.draw.line(self.screen, cyan, (x + icon_width, y + 7), (x + icon_width, y + height - 7), 1)
        pygame.draw.line(self.screen, cyan, (x + 36, y + 28), (x + 58, y + 28), 7)
        pygame.draw.line(self.screen, cyan, (x + 36, y + 28), (x + 52, y + 14), 7)
        pygame.draw.line(self.screen, cyan, (x + 36, y + 28), (x + 52, y + 42), 7)
        pygame.draw.line(self.screen, cyan, (x + 58, y + 28), (x + 58, y + 42), 7)

        text_parts = [("PRESS ", WHITE), ("BACKSPACE", cyan), (" TO RETURN", WHITE)]
        text_x = x + icon_width + 25
        max_text_width = x + width - 20 - text_x
        font_size = 22
        while font_size > 16:
            font = pygame.font.SysFont("Consolas", font_size, bold=True)
            total_width = sum(font.render(text, True, color).get_width() for text, color in text_parts)
            if total_width <= max_text_width:
                break
            font_size -= 1

        cursor = text_x
        for text, color in text_parts:
            rendered = font.render(text, True, color)
            self.screen.blit(rendered, (cursor, y + 18))
            cursor += rendered.get_width()

    def draw_clear_leaderboard_hint(self):
        cyan = (0, 220, 255)
        red = (255, 70, 72)
        font = pygame.font.SysFont("Consolas", 18, bold=True)
        parts = [("PRESS ", WHITE), ("D", red), (" TO CLEAR LEADERBOARD", cyan)]
        x = 210
        y = 566
        width = 380
        height = 28
        points = [
            (x + 8, y), (x + width - 8, y), (x + width, y + 8),
            (x + width, y + height - 8), (x + width - 8, y + height),
            (x + 8, y + height), (x, y + height - 8), (x, y + 8)
        ]

        pygame.draw.polygon(self.screen, (3, 15, 28), points)
        pygame.draw.lines(self.screen, cyan, True, points, 1)

        total_width = sum(font.render(text, True, color).get_width() for text, color in parts)
        cursor = x + (width - total_width) // 2
        text_y = y + 5

        for text, color in parts:
            rendered = font.render(text, True, color)
            self.screen.blit(rendered, (cursor, text_y))
            cursor += rendered.get_width()

    def draw_leaderboard_screen(self, scores, scroll_position, visible_count):
        self.draw_leaderboard_frame()
        self.draw_leaderboard_title()

        if not scores:
            self.draw_glow_text("NO SCORES YET", self.subtitle_font, (400, 292), WHITE, (0, 210, 255))
        else:
            row_top = 142
            row_gap = 47
            list_bottom = 490
            start_index = int(scroll_position)
            slide_offset = (scroll_position - start_index) * row_gap
            visible_scores = scores[start_index:start_index + visible_count + 1]

            for i, record in enumerate(visible_scores, start=start_index + 1):
                y = row_top + (i - start_index - 1) * row_gap - slide_offset
                if y < row_top - row_gap or y + 42 > list_bottom:
                    continue
                name = f"Attempt {i}"
                score = record.get("score", 0)
                self.draw_leaderboard_row(i, name, score, int(y))

        self.draw_return_button()
        self.draw_clear_leaderboard_hint()

    def draw_game_over_background(self):
        cyan = (0, 190, 255)
        red = (255, 66, 72)

        self.screen.fill((2, 7, 18))

        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, (4, 32, 68), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, (4, 32, 68), (0, y), (WIDTH, y))

        frame = [
            (22, 80), (22, 34), (46, 14), (150, 14), (170, 26), (630, 26),
            (650, 14), (754, 14), (778, 34), (778, 80), (790, 96), (790, 508),
            (778, 524), (778, 566), (754, 586), (650, 586), (630, 574),
            (170, 574), (150, 586), (46, 586), (22, 566), (22, 524),
            (10, 508), (10, 96)
        ]
        pygame.draw.lines(self.screen, cyan, True, frame, 3)
        pygame.draw.lines(self.screen, (0, 88, 140), True, [(x + 12, y + 12) for x, y in frame], 1)

        for x in range(360, 440, 14):
            pygame.draw.line(self.screen, cyan, (x, 20), (x + 8, 20), 5)
            pygame.draw.line(self.screen, cyan, (x, 580), (x + 8, 580), 5)

        for y in range(250, 350, 24):
            pygame.draw.line(self.screen, cyan, (16, y), (16, y + 16), 5)
            pygame.draw.line(self.screen, cyan, (784, y), (784, y + 16), 5)

        for point in [(100, 255), (692, 360), (620, 495), (704, 495), (690, 215)]:
            pygame.draw.circle(self.screen, (*red, 65), point, 13)
            pygame.draw.circle(self.screen, red, point, 6)

    def draw_game_over_stats(self):
        cyan = (0, 220, 255)
        x = 42
        y = 58
        width = 145
        height = 108
        points = [
            (x + 10, y), (x + width - 8, y), (x + width, y + 8),
            (x + width, y + height - 8), (x + width - 8, y + height),
            (x + 10, y + height), (x, y + height - 8), (x, y + 8)
        ]
        pygame.draw.polygon(self.screen, (3, 14, 28), points)
        pygame.draw.lines(self.screen, cyan, True, points, 1)
        pygame.draw.line(self.screen, (0, 75, 105), (x + 20, y + 76), (x + width - 20, y + 76), 1)

        small = pygame.font.SysFont("Consolas", 20, bold=True)
        big = pygame.font.SysFont("Consolas", 36, bold=True)
        self.screen.blit(small.render("SCORE", True, WHITE), (x + 24, y + 18))
        self.screen.blit(big.render(str(self.score), True, cyan), (x + 24, y + 40))

        if self.game_won:
            max_font = pygame.font.SysFont("Consolas", 14, bold=True)
            pygame.draw.rect(self.screen, (4, 28, 18), (x + 12, y + 82, width - 24, 18), 1)
            self.screen.blit(max_font.render("MAXIMUM POINTS", True, (150, 255, 38)), (x + 18, y + 84))

    def draw_game_over_button(self, y, text_parts, icon):
        cyan = (0, 220, 255)
        x = 230
        width = 340
        height = 58
        icon_width = 82
        points = [
            (x + 12, y), (x + width - 10, y), (x + width, y + 10),
            (x + width, y + height - 10), (x + width - 10, y + height),
            (x + 12, y + height), (x, y + height - 10), (x, y + 10)
        ]

        glow = pygame.Surface((width + 20, height + 20), pygame.SRCALPHA)
        pygame.draw.polygon(glow, (*cyan, 35), [(px - x + 10, py - y + 10) for px, py in points])
        self.screen.blit(glow, (x - 10, y - 10))
        pygame.draw.polygon(self.screen, (3, 15, 28), points)
        pygame.draw.lines(self.screen, cyan, True, points, 2)
        pygame.draw.line(self.screen, cyan, (x + icon_width, y + 7), (x + icon_width, y + height - 7), 1)

        center = (x + icon_width // 2, y + height // 2)
        if icon == "restart":
            pygame.draw.arc(self.screen, cyan, (center[0] - 17, center[1] - 17, 34, 34), 0.7, 5.6, 5)
            pygame.draw.polygon(self.screen, cyan, [(center[0] + 6, center[1] - 22), (center[0] + 20, center[1] - 20), (center[0] + 12, center[1] - 8)])
        elif icon == "home":
            pygame.draw.polygon(self.screen, cyan, [(center[0] - 20, center[1] - 2), (center[0], center[1] - 20), (center[0] + 20, center[1] - 2)])
            pygame.draw.rect(self.screen, cyan, (center[0] - 14, center[1] - 2, 28, 20))
            pygame.draw.rect(self.screen, (3, 15, 28), (center[0] - 4, center[1] + 7, 8, 11))
        elif icon == "exit":
            pygame.draw.rect(self.screen, cyan, (center[0] - 18, center[1] - 16, 20, 32), 3)
            pygame.draw.line(self.screen, cyan, (center[0] - 2, center[1]), (center[0] + 20, center[1]), 4)
            pygame.draw.polygon(self.screen, cyan, [(center[0] + 20, center[1]), (center[0] + 10, center[1] - 9), (center[0] + 10, center[1] + 9)])
        elif icon == "leaderboard":
            pygame.draw.rect(self.screen, cyan, (center[0] - 24, center[1] + 6, 15, 14), 3)
            pygame.draw.rect(self.screen, cyan, (center[0] - 8, center[1] - 10, 16, 30), 3)
            pygame.draw.rect(self.screen, cyan, (center[0] + 10, center[1], 15, 20), 3)
            self.draw_tiny_text("2", center[0] - 19, center[1] + 5, cyan)
            self.draw_tiny_text("1", center[0] - 2, center[1] - 11, cyan)
            self.draw_tiny_text("3", center[0] + 15, center[1] - 1, cyan)

        text_x = x + icon_width + 26
        max_text_width = x + width - 20 - text_x
        font_size = 23
        while font_size > 16:
            font = pygame.font.SysFont("Consolas", font_size, bold=True)
            total_width = sum(font.render(text, True, color).get_width() for text, color in text_parts)
            if total_width <= max_text_width:
                break
            font_size -= 1

        cursor = text_x
        for text, color in text_parts:
            rendered = font.render(text, True, color)
            self.screen.blit(rendered, (cursor, y + 18))
            cursor += rendered.get_width()

    def draw_game_over_screen(self):
        cyan = (0, 220, 255)
        red = (255, 70, 72)

        self.draw_game_over_background()
        self.draw_game_over_stats()

        if self.game_won:
            green = (150, 255, 38)
            self.draw_glow_text("CONGRATULATIONS!", self.title_font, (400, 240), green, green)
            self.draw_glow_text("YOU HAVE REACHED", self.subtitle_font, (400, 318), WHITE, cyan)
            self.draw_glow_text("THE MAXIMUM POINTS!", self.subtitle_font, (400, 360), green, green)
            self.draw_game_over_button(390, [("PRESS ", WHITE), ("R", cyan), (" TO RESTART", WHITE)], "restart")
            self.draw_game_over_button(460, [("PRESS ", WHITE), ("M", cyan), (" FOR MAIN MENU", WHITE)], "home")
            self.draw_game_over_button(530, [("PRESS ", WHITE), ("L", cyan), (" FOR LEADERBOARD", WHITE)], "leaderboard")
        else:
            pygame.draw.line(self.screen, red, (205, 258), (232, 258), 3)
            pygame.draw.line(self.screen, red, (568, 258), (595, 258), 3)
            self.draw_glow_text("GAME OVER", self.title_font, (400, 250), red, red)
            self.draw_game_over_button(310, [("PRESS ", WHITE), ("R", cyan), (" TO RESTART", WHITE)], "restart")
            self.draw_game_over_button(390, [("PRESS ", WHITE), ("M", cyan), (" FOR MAIN MENU", WHITE)], "home")
            self.draw_game_over_button(470, [("PRESS ", WHITE), ("ESC", cyan), (" TO EXIT", WHITE)], "exit")

    def show_menu(self):
        menu = True

        while menu:
            self.draw_main_menu()

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.reset_game()
                        menu = False
                    elif event.key == pygame.K_l:
                        self.show_leaderboard()
                    elif event.key == pygame.K_s:
                        self.show_settings()
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        quit()

    def show_settings(self):
        showing = True
        selected_setting = 0

        while showing:
            self.draw_settings_screen(selected_setting)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        showing = False
                    elif event.key == pygame.K_UP:
                        selected_setting = max(0, selected_setting - 1)
                    elif event.key == pygame.K_DOWN:
                        selected_setting = min(1, selected_setting + 1)
                    elif event.key == pygame.K_LEFT:
                        if selected_setting == 0:
                            self.speed_index = max(0, self.speed_index - 1)
                        else:
                            self.speed_gain_index = max(0, self.speed_gain_index - 1)
                    elif event.key == pygame.K_RIGHT:
                        if selected_setting == 0:
                            self.speed_index = min(len(self.speed_options) - 1, self.speed_index + 1)
                        else:
                            self.speed_gain_index = min(len(self.speed_gain_options) - 1, self.speed_gain_index + 1)

            self.clock.tick(60)

    def show_leaderboard(self):
        showing = True
        target_scroll = 0
        smooth_scroll = 0
        visible_count = 7

        while showing:
            scores = self.score_manager.get_leaderboard()

            max_scroll = max(0, len(scores) - visible_count)
            target_scroll = max(0, min(target_scroll, max_scroll))
            smooth_scroll += (target_scroll - smooth_scroll) * 0.22

            if abs(target_scroll - smooth_scroll) < 0.01:
                smooth_scroll = target_scroll

            self.draw_leaderboard_screen(scores, smooth_scroll, visible_count)

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        showing = False
                    elif event.key == pygame.K_d:
                        self.score_manager.clear_scores()
                        target_scroll = 0
                        smooth_scroll = 0
                    elif event.key == pygame.K_DOWN:
                        if target_scroll < max_scroll:
                            target_scroll += 1
                    elif event.key == pygame.K_UP:
                        if target_scroll > 0:
                            target_scroll -= 1

                if event.type == pygame.MOUSEWHEEL:
                    target_scroll -= event.y

            self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.snake.change_direction((0, -CELL_SIZE))
                elif event.key == pygame.K_DOWN:
                    self.snake.change_direction((0, CELL_SIZE))
                elif event.key == pygame.K_LEFT:
                    self.snake.change_direction((-CELL_SIZE, 0))
                elif event.key == pygame.K_RIGHT:
                    self.snake.change_direction((CELL_SIZE, 0))
                elif event.key == pygame.K_p and not self.game_over:
                    self.paused = not self.paused
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                elif event.key == pygame.K_m and self.game_over:
                    self.show_menu()
                elif event.key == pygame.K_l and self.game_over:
                    self.show_leaderboard()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

    def check_collision(self):
        head = self.snake.body[0]
        x, y = head

        if x < PLAY_MIN_X or x >= PLAY_MAX_X or y < PLAY_MIN_Y or y >= PLAY_MAX_Y:
            self.end_game()
            return

        if self.snake.hit_self():
            self.end_game()
            return

        if head == self.food.position:
            food_value = self.food.value
            self.score += self.food.value
            self.snake.grow()
            self.speed += self.speed_gain_options[self.speed_gain_index]

            trap_increase = 4 if food_value == 5 else 2

            blocked = self.snake.occupied_positions()
            blocked.update(trap.position for trap in self.traps)
            self.food.respawn(blocked)
            self.add_traps(trap_increase)

            if self.score >= self.MAX_SCORE:
                self.end_game(won=True)
                return

        for trap_index, trap in enumerate(self.traps):
            if head == trap.position:
                self.score += trap.value

                blocked = self.snake.occupied_positions()
                blocked.add(self.food.position)
                blocked.update(other.position for other in self.traps if other != trap)
                self.respawn_trap_spread(trap, blocked, trap_index)

                if self.score < 0:
                    self.end_game()
                return

    def end_game(self, won=False):
        self.game_over = True
        self.game_won = won

        if not self.score_saved:
            self.score_manager.save_score(self.player_name, self.score)
            self.score_saved = True

    def draw(self):
        if self.game_over:
            self.draw_game_over_screen()
            pygame.display.update()
            return

        self.draw_background()

        self.snake.draw(self.screen)
        self.food.draw(self.screen)

        for trap in self.traps:
            trap.draw(self.screen)

        self.draw_gameplay_hud()

        if self.paused:
            self.draw_text("PAUSED", 350, 280, GRAY)

        pygame.display.update()

    @log_action
    def run(self):
        self.show_menu()

        while self.running:
            self.handle_events()

            if not self.paused and not self.game_over:
                self.snake.move()
                self.check_collision()

            self.draw()
            self.clock.tick(self.speed)

        pygame.quit()
