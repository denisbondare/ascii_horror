import os
import random
import sys
from utils import is_visible, generate_perlin_noise, get_wave_char

class Graphics:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.game_height = height - 3  # Reserve 3 lines for text
        self.buffer = [[' ' for _ in range(width)] for _ in range(height)]
        self.previous_buffer = [[' ' for _ in range(width)] for _ in range(height)]
        self.distortion_map = {}
        self.distortion_duration = 2  # frames
        self.corrupted_lines = set()
        self.corrupted_line_duration = 5  # frames
        self.unseen_distortions = {}

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
        # Move cursor to top-left corner
        sys.stdout.write("\033[H")
        sys.stdout.flush()
        
        for y, row in enumerate(self.buffer):
            if row != self.previous_buffer[y]:
                # Move cursor to the beginning of the line
                sys.stdout.write(f"\033[{y + 1};1H")
                # Write the entire row
                sys.stdout.write(''.join(row))
                sys.stdout.flush()
                self.previous_buffer[y] = row[:]
        
        # Move cursor to the bottom of the screen
        sys.stdout.write(f"\033[{self.height + 1};1H")
        sys.stdout.flush()

    def draw_text(self, x, y, text):
        for i, char in enumerate(text):
            self.draw_char(x + i, y, char)

    def draw_world(self, world, player, visibility_radius, signal_strength):
        distortion_intensity = self.apply_distortions(signal_strength)
        
        player_screen_x = self.width // 2
        player_screen_y = self.game_height // 2

        for y in range(self.height):
            for x in range(self.width):
                world_x = player.x + (x - player_screen_x)
                world_y = player.y + (y - player_screen_y)
                
                if y in self.corrupted_lines:
                    self.draw_char(x, y, random.choice('!@#$%^&*()_+-={}[]|\\:;"\'<>,.?/'))
                elif (x, y) in self.distortion_map:
                    self.draw_char(x, y, self.distortion_map[(x, y)][0])
                elif 0 <= world_x < world.width and 0 <= world_y < world.height:
                    if is_visible(player_screen_x, player_screen_y, x, y, visibility_radius):
                        if world.is_obstacle(world_x, world_y):
                            self.draw_char(x, y, '▓')
                        elif (world_x, world_y) in world.items:
                            self.draw_char(x, y, world.items[(world_x, world_y)])
                        else:
                            self.draw_char(x, y, ' ')
                    else:
                        if (x, y) in self.unseen_distortions:
                            self.draw_char(x, y, self.unseen_distortions[(x, y)][0])
                        else:
                            self.draw_char(x, y, '░')
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

    def apply_distortions(self, signal_strength):
        distortion_intensity = max(0, 1 - (signal_strength / 100))
        
        # Update existing distortions
        for pos in list(self.distortion_map.keys()):
            self.distortion_map[pos][1] -= 1
            if self.distortion_map[pos][1] <= 0:
                del self.distortion_map[pos]

        # Generate new distortions
        if random.random() < distortion_intensity * 0.1:
            for _ in range(int(self.width * self.height * distortion_intensity * 0.1)):
                x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
                char = random.choice('!#$%^&()_+-={}[]|\\:;"\'<>,.?/')
                self.distortion_map[(x, y)] = [char, self.distortion_duration]

        # Update corrupted lines
        self.corrupted_lines = {line for line in self.corrupted_lines if random.random() > 0.2}
        if random.random() < distortion_intensity * 0.1:
            new_corrupted_line = random.randint(0, self.height - 1)
            self.corrupted_lines.add(new_corrupted_line)

        # Update unseen area distortions
        for pos in list(self.unseen_distortions.keys()):
            self.unseen_distortions[pos][1] -= 1
            if self.unseen_distortions[pos][1] <= 0:
                del self.unseen_distortions[pos]

        # Generate new unseen area distortions
        if random.random() < distortion_intensity * 0.1:
            x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
            char = random.choice('▒▓█▄▀░')
            self.unseen_distortions[(x, y)] = [char, self.distortion_duration]

        return distortion_intensity
