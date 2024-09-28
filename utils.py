import random
import math

def get_random_position(width, height):
    return random.randint(0, width - 1), random.randint(0, height - 1)

def distance(x1, y1, x2, y2):
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

def is_visible(x1, y1, x2, y2, radius):
    return distance(x1, y1, x2, y2) <= radius
