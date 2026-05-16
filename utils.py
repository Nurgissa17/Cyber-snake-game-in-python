import random
import time

CELL_SIZE = 20
WIDTH = 800
HEIGHT = 600
PLAY_MIN_X = 40
PLAY_MIN_Y = 40
PLAY_MAX_X = 760
PLAY_MAX_Y = 540

BLACK = (8, 10, 38)
WHITE = (240, 240, 240)
GREEN = (158, 205, 43)
BLUE = (21, 169, 205)
GOLD = (255, 200, 0)
RED = (255, 60, 60)
GRAY = (90, 90, 100)

GRID_LINE = (31, 74, 132)
GRID_GLOW = (16, 36, 88)
SNAKE_YELLOW = (225, 174, 12)
SNAKE_HEAD_GLOW = (255, 44, 184)


def log_action(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} finished in {end - start:.4f} seconds")
        return result
    return wrapper


def random_position():
    x = random.randrange(PLAY_MIN_X, PLAY_MAX_X, CELL_SIZE)
    y = random.randrange(PLAY_MIN_Y, PLAY_MAX_Y, CELL_SIZE)
    return (x, y)
