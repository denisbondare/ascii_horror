import os
import random
import math
import sys
import time
from utils import is_visible, generate_perlin_noise, get_wave_char
import keyboard

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
        self.cursed_chars = '⛧⎊⏧⏣☈☇⚯⚮⛮⛥⛤⛢⚝⚹⚶⚸⭘⭙⭔⭓⍜⍛⍭⍱⍲'
        self.cursed_words = ['ĄBØMINĄTIØN', 'DÆMØN', 'DĘVĮŁ', 'ĘVĪŁ', 'FĪĘND', 'HĄUNT', 'HØRRØR', 'PHĄNTĄSM', 'SPĪRĪT', 'WRĄĪTH', 'BŁĄSPHĘMY', 'CĄRNĄGĘ', 'DĘSĘCRĄTĪØN', 'ĘNTRÅĪŁS', 'FŁĘSHGØŁĘM', 'GĪBBĘT', 'HĘŁŁSPĄWN', 'ĪMMØŁĄTĪØN', 'MĄDNĘSS', 'NĘCRØPHĄGĘ', 'PĘSTĪŁĘNCĘ', 'QUĘŁCH', 'RĄVĄGĘ', 'SŁĄUGHTĘR', 'TØRMĘNT', 'UNDĘĄD', 'VĪSCĘRĄ', 'WRĘTCH', 'YØKĄĪ']
        self.obstacle_char = '▓'
        self.unseen_char = '░'
        self.empty_char = ' '
        self.echo_chars = '⛧⎊⏧⏣☈☇⚯⚮⛮⛥⛤⛢⚝⚹⚶⚸⭘⭙⭔⭓⍜⍛⍭⍱⍲ĄĪĘØÆĪŁ'
        self.disable_render = False
        self.line_distortion_multiplier = 0.7
        self.symbol_distortion_multiplier = 0.7

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
        
        unseen_char = self.unseen_char
        obstacle_char = self.obstacle_char
        empty_char = self.empty_char
        if distortion_intensity > 0.7 and random.random() < 0.11:
            unseen_char = self.obstacle_char
            obstacle_char = self.empty_char
            empty_char = self.unseen_char
            
        for screen_y in range(self.height):
            if screen_y == 18:
                for screen_x in range(self.width):
                    self.draw_char(screen_x, screen_y, '-')
                continue
            
            line = []
            for screen_x in range(self.width):
                world_x = player.x + (screen_x - player_screen_x)
                world_y = player.y + (screen_y - player_screen_y)
                
                if screen_y in self.corrupted_lines:
                    if distortion_intensity > 0.4 and random.random() < 0.3:
                        cursed_word = random.choice(self.cursed_words)
                        start_pos = random.randint(0, self.width - len(cursed_word))
                        for i in range(self.width):
                            if start_pos <= i < start_pos + len(cursed_word):
                                line.append(cursed_word[i - start_pos])
                            else:
                                line.append(random.choice(chars_set))
                    else:
                        line.append(random.choice(chars_set))
                elif (screen_x, screen_y) in self.distortion_map:
                    line.append(self.distortion_map[(screen_x, screen_y)][0])
                elif screen_y < 18 and 0 <= world_x < world.width and 0 <= world_y < world.height:
                    if is_visible(player.x, player.y, world_x, world_y, visibility_radius, world):
                        if world.is_obstacle(world_x, world_y):
                            line.append(obstacle_char)
                        elif (world_x, world_y) in world.items:
                            line.append(world.items[(world_x, world_y)])
                        else:
                            line.append(empty_char)
                    else:
                        if (screen_x, screen_y) in self.unseen_distortions:
                            line.append(self.unseen_distortions[(screen_x, screen_y)][0])
                        else:
                            line.append(unseen_char)
                else:
                    line.append(empty_char)
            
            # Ensure the line is exactly self.width characters long
            line = line[:self.width]
            if len(line) < self.width:
                line.extend([empty_char] * (self.width - len(line)))
            
            for screen_x, char in enumerate(line):
                self.draw_char(screen_x, screen_y, char)
                    
        self.draw_ripples(player)
                    
        for echo in world.echo_sources:
            world_x, world_y = echo.x, echo.y
            for dy in range(-6, 7):
                screen_y = world_y - player.y + player_screen_y + dy
                if screen_y >= self.game_height:
                    continue
                for dx in range(-18, 19):
                    screen_x = world_x - player.x + player_screen_x + dx
                    
                    
                    # Use Perlin noise to create a fluctuating blob shape
                    ping_pong_time = math.sin(time.time() % 15) + (time.time() % 100) * 0.02
                    noise_value = generate_perlin_noise(dx, dy, ping_pong_time, scale=0.045, octaves=6, persistence=0.6, lacunarity=3.0)
                    
                    # Determine if this position should be part of the echo
                    # Calculate distance from center
                    distance_from_center = math.sqrt((dx/3)**2 + dy**2)
                    # Adjust threshold based on distance
                    threshold = 0 + (distance_from_center / 15) * 0.25  # Adjust multiplier as needed
                    if noise_value > threshold:
                        # Use world coordinates to seed the random choice
                        time_random_shift = int(time.time()*10) % len(self.echo_chars)
                        pattern_index = ((world_x+dx)*100 + (world_y+dy)*100 + time_random_shift) % len(self.echo_chars)
                        
                        char = self.echo_chars[pattern_index]
                        self.draw_char(screen_x, screen_y, char)
                            

        
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
        if random.random() < distortion_intensity * self.symbol_distortion_multiplier:
            for _ in range(int(self.width * self.height * distortion_intensity * 0.1)):
                x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 2)
                char = random.choice(chars_set)
                self.distortion_map[(x, y)] = [char, self.distortion_duration]

        # Update corrupted lines
        self.corrupted_lines = {line for line in self.corrupted_lines if random.random() > 0.2}
        if random.random() < distortion_intensity * self.line_distortion_multiplier:
            new_corrupted_line = random.randint(0, self.height - 2)
            self.corrupted_lines.add(new_corrupted_line)

        # Update unseen area distortions
        for pos in list(self.unseen_distortions.keys()):
            self.unseen_distortions[pos][1] -= 1
            if self.unseen_distortions[pos][1] <= 0:
                del self.unseen_distortions[pos]

        # Generate new unseen area distortions
        if random.random() < distortion_intensity * self.symbol_distortion_multiplier:
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

    def load_ascii_video(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            fps = int(f.readline().strip())
            frame_width = int(f.readline().strip())
            frame_height = int(f.readline().strip())
            frames = [line.strip() for line in f.readlines()]
        return fps, frame_width, frame_height, frames

    def play_ascii_video(self, file_path):
        fps, frame_width, frame_height, frames = self.load_ascii_video(file_path)
        
        start_x = max(0, (self.width - frame_width) // 2)
        start_y = max(0, (self.height - frame_height) // 2)
        
        for frame in frames:
            self.clear()
            for y in range(min(frame_height, self.height)):
                for x in range(min(frame_width, self.width)):
                    char_index = y * frame_width + x
                    if char_index < len(frame):
                        char = frame[char_index]
                        self.draw_char(start_x + x, start_y + y, char)
            self.render()
            time.sleep(1 / fps)
            
            # Check for space key press to exit video playback
            if keyboard.is_pressed('space'):
                break