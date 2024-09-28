import os
from utils import is_visible

class Graphics:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.buffer = [[' ' for _ in range(width)] for _ in range(height)]
        self.previous_buffer = None

    def clear(self):
        self.buffer = [[' ' for _ in range(self.width)] for _ in range(self.height)]

    def draw_char(self, x, y, char):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.buffer[y][x] = char

    def draw_borders(self):
        for x in range(self.width):
            self.draw_char(x, 0, '-')
            self.draw_char(x, self.height - 1, '-')
        for y in range(self.height):
            self.draw_char(0, y, '|')
            self.draw_char(self.width - 1, y, '|')

    def render(self):
        if self.buffer != self.previous_buffer:
            print("\033[H", end="")  # Move cursor to top-left corner
            for row in self.buffer:
                print(''.join(row))
            self.previous_buffer = [row[:] for row in self.buffer]

    def draw_text(self, x, y, text):
        for i, char in enumerate(text):
            self.draw_char(x + i, y, char)

    def draw_world(self, world, player, visibility_radius):
        for y in range(self.height):
            for x in range(self.width):
                if is_visible(player.x, player.y, x, y, visibility_radius):
                    if world.is_obstacle(x, y):
                        self.draw_char(x, y, '#')
                    elif (x, y) in world.items:
                        self.draw_char(x, y, world.items[(x, y)])
                else:
                    self.draw_char(x, y, ' ')
