import random
import math
import noise

def get_random_position(width, height):
    return random.randint(0, width - 1), random.randint(0, height - 1)

def distance(x1, y1, x2, y2):
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

def is_visible(x1, y1, x2, y2, radius):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    return (dx / 2) ** 2 + dy ** 2 <= radius ** 2

def generate_perlin_noise(x, y, t, scale=0.1, octaves=6, persistence=0.5, lacunarity=2.0):
    return noise.pnoise3(x * scale, 
                         y * scale, 
                         t * scale,
                         octaves=octaves, 
                         persistence=persistence, 
                         lacunarity=lacunarity, 
                         repeatx=1024, 
                         repeaty=1024, 
                         base=0)

def get_wave_char(value):
    if value < -0.5:
        return '~'
    elif value < 0:
        return '-'
    elif value < 0.5:
        return '='
    else:
        return '≈'
