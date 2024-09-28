import os
from utils import is_visible, generate_perlin_noise, get_wave_char

class Graphics:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.game_height = height - 3  # Reserve 3 lines for text
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
        player_screen_x = self.width // 2
        player_screen_y = self.game_height // 2

        for y in range(self.game_height):
            for x in range(self.width):
                world_x = player.x + (x - player_screen_x)
                world_y = player.y + (y - player_screen_y)
                
                if 0 <= world_x < world.width and 0 <= world_y < world.height:
                    if is_visible(player_screen_x, player_screen_y, x, y, visibility_radius):
                        if world.is_obstacle(world_x, world_y):
                            self.draw_char(x, y, '▓')
                        elif (world_x, world_y) in world.items:
                            self.draw_char(x, y, world.items[(world_x, world_y)])
                        else:
                            self.draw_char(x, y, ' ')  # Empty space is now truly empty
                    else:
                        self.draw_char(x, y, '░')  # Use a different character for unseen areas
                else:
                    self.draw_char(x, y, ' ')

        # Draw player in the center
        self.draw_char(player_screen_x, player_screen_y, player.char)

    def draw_text_area(self):
        for x in range(self.width):
            self.draw_char(x, self.game_height, '-')
        self.draw_char(0, self.game_height, '+')
        self.draw_char(self.width - 1, self.game_height, '+')

    def draw_animated_text(self, text, current_char):
        self.draw_text_area()
        displayed_text = text[:current_char]
        self.draw_text(1, self.game_height + 1, displayed_text)

    def draw_animated_background(self, t):
        for y in range(self.height):
            for x in range(self.width):
                value = generate_perlin_noise(x, y, t)
                char = get_wave_char(value)
                self.draw_char(x, y, char)

    def draw_stats(self, samples_collected, total_samples, temperature, humidity, signal_strength):
        self.draw_text_area()
        stats_text = f"{samples_collected}/{total_samples} | T: {temperature:.1f}°C | H: {humidity}% | Signal: {signal_strength}%"
        self.draw_text(1, self.game_height + 1, stats_text)
