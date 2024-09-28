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
        self.corrupted_line_duration = 3  # frames
        self.unseen_distortions = {}
        self.ripples = []
        self.corrupted_chars = '!#$%^&*()_-={}[]|\\:;"\'<>,.?/'
        self.cursed_chars = '⛧⍟⎈⎊⏧⏣☈☇⚯⚮⛮⛥⛤⛢⚝⚹⚶⚸⛇⛈⭘⭙⭔⭓⍜⍛⍭⍱⍲'
        self.disable_render = False

    def clear(self):
        if self.disable_render:
            return
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
        if self.disable_render:
            return
        
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
        chars_set = self.corrupted_chars
        if distortion_intensity > 0.66:
            chars_set += self.cursed_chars        
        
        player_screen_x = self.width // 2
        player_screen_y = self.game_height // 2
        
        if random.random() > 0.04:
            visibility_radius = visibility_radius
        else:
            visibility_radius = visibility_radius * 0.66
            
        for screen_y in range(self.height):
            for screen_x in range(self.width):
                if screen_y==18:
                    self.draw_char(screen_x, screen_y, '-')
                    continue
                
                world_x = player.x + (screen_x - player_screen_x)
                world_y = player.y + (screen_y - player_screen_y)
                
                if screen_y in self.corrupted_lines:
                    self.draw_char(screen_x, screen_y, random.choice(chars_set))
                elif (screen_x, screen_y) in self.distortion_map:
                    self.draw_char(screen_x, screen_y, self.distortion_map[(screen_x, screen_y)][0])
                elif screen_y<18 and 0 <= world_x < world.width and 0 <= world_y < world.height:
                    if is_visible(player.x, player.y, world_x, world_y, visibility_radius, world):
                        if world.is_obstacle(world_x, world_y):
                            self.draw_char(screen_x, screen_y, '▓')
                        elif (world_x, world_y) in world.items:
                            self.draw_char(screen_x, screen_y, world.items[(world_x, world_y)])
                        else:
                            self.draw_char(screen_x, screen_y, ' ')
                    else:
                        if (screen_x, screen_y) in self.unseen_distortions:
                            self.draw_char(screen_x, screen_y, self.unseen_distortions[(screen_x, screen_y)][0])
                        else:
                            self.draw_char(screen_x, screen_y, '░')
                else:
                    self.draw_char(screen_x, screen_y, ' ')
                    
        self.draw_ripples(player)
                    
        for echo in world.echo_sources:
            world_x = echo.x
            world_y = echo.y
            screen_x = world_x - player.x + player_screen_x
            screen_y = world_y - player.y + player_screen_y
            self.draw_char(screen_x, screen_y, '☥')        
        
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
        stats_text = f"{samples_collected}/{total_samples} | T: {'+' if temperature > 0 else ''}{temperature:.1f}°C | H: {humidity}% | Signal: {round(signal_strength)}%"
        self.draw_text(1, self.game_height + 1, stats_text)

    def apply_distortions(self, signal_strength):
        distortion_intensity = min(1,max(0, 1 - (signal_strength**1.05 / 100)))
        chars_set = self.corrupted_chars
        if distortion_intensity > 0.66:
            chars_set += self.cursed_chars
        
        # Update existing distortions
        for pos in list(self.distortion_map.keys()):
            self.distortion_map[pos][1] -= 1
            if self.distortion_map[pos][1] <= 0:
                del self.distortion_map[pos]

        # Generate new distortions
        if random.random() < distortion_intensity * 0.9:
            for _ in range(int(self.width * self.height * distortion_intensity * 0.1)):
                x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 2)
                char = random.choice(chars_set)
                self.distortion_map[(x, y)] = [char, self.distortion_duration]

        # Update corrupted lines
        self.corrupted_lines = {line for line in self.corrupted_lines if random.random() > 0.2}
        if random.random() < distortion_intensity * 0.9:
            new_corrupted_line = random.randint(0, self.height - 2)
            self.corrupted_lines.add(new_corrupted_line)

        # Update unseen area distortions
        for pos in list(self.unseen_distortions.keys()):
            self.unseen_distortions[pos][1] -= 1
            if self.unseen_distortions[pos][1] <= 0:
                del self.unseen_distortions[pos]

        # Generate new unseen area distortions
        if random.random() < distortion_intensity * 0.9:
            x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 2)
            char = random.choice('▒▓█▄▀░')
            self.unseen_distortions[(x, y)] = [char, self.distortion_duration]

        return distortion_intensity

    def add_ripple(self, x, y):
        self.ripples.append((x, y, 0))  # (x, y, radius)

    def update_ripples(self):
        for i, (x, y, radius) in enumerate(self.ripples):
            self.ripples[i] = (x, y, radius + 1)
        self.ripples = [(x, y, r) for x, y, r in self.ripples if r < 100]  # Remove old ripples

    def draw_ripples(self, player):
        for x, y, radius in self.ripples:
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if dx*dx + dy*dy <= radius*radius and dx*dx + dy*dy > (radius-1)*(radius-1):
                        x = x + dx
                        y = y + dy
                        screen_x = x - player.x + self.width // 2
                        screen_y = y - player.y + self.height // 2
                        self.draw_char(screen_x, screen_y, '~')

