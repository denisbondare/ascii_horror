import keyboard
import time
import pygame
import random
from graphics import Graphics
from player import Player
from world import World
from utils import get_random_position, distance
from sounds import SoundSystem

class Game:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.graphics = Graphics(width, height)
        self.world = World(256, 256)  # Much larger world
        self.player = Player(128, 128)  # Start player in the center of the world
        self.sound_system = SoundSystem()
        self.running = True
        self.visibility_radius = 5
        self.step_counter = 0
        self.sound_system.play_music("ambient_horror")
        self.vertical_step = 0
        self.text_queue = []
        self.current_text = ""
        self.text_index = 0
        self.text_display_active = False
        self.last_type_time = 0
        self.intro_text = [            
            "Depth: 2,743 meters below surface.",
            "Temperature: 57°C. Humidity: 98%.",
            "Signal strength: 80%.",
            "Mission: Collect 50 material samples.",
            "Arrow keys to control machine.",
            "Automatic evacuation upon completion.",
            "Warning: Unusual readings detected.",
            "Press Enter to initiate operation."
        ]
        self.show_intro = True
        self.text_fully_displayed = False
        self.samples_collected = 0
        self.total_samples = 50
        self.temperature = 57.0
        self.humidity = 98
        self.signal_strength = 80
        self.temp_direction = random.choice([-1, 1])
        self.humidity_direction = random.choice([-1, 1])
        self.update_counter = 0

    def handle_input(self):
        if self.text_display_active:
            if keyboard.is_pressed('enter') and self.text_fully_displayed:
                self.next_text()
            return

        dx, dy = 0, 0
        moved = False
        if keyboard.is_pressed('up') and self.player.y > 1:
            self.vertical_step += 1
            if self.vertical_step >= 2:
                dy = -1
                self.vertical_step = 0
            moved = True
        elif keyboard.is_pressed('down') and self.player.y < self.world.height - 2:
            self.vertical_step += 1
            if self.vertical_step >= 2:
                dy = 1
                self.vertical_step = 0
            moved = True
        elif keyboard.is_pressed('left') and self.player.x > 1:
            dx = -1
            moved = True
        elif keyboard.is_pressed('right') and self.player.x < self.world.width - 2:
            dx = 1
            moved = True
        elif keyboard.is_pressed('u'):
            self.samples_collected += 10
        elif keyboard.is_pressed('d'):
            self.signal_strength -= 10
        elif keyboard.is_pressed('esc'):
            self.running = False

        if not self.world.is_obstacle(self.player.x + dx, self.player.y + dy):
            self.world.move(dx, dy)  # Move the world instead of the player
            if moved:
                self.step_counter += 1
                if self.step_counter % 2 == 0:
                    self.sound_system.play_sound("footstep")

    def update(self):
        if self.text_display_active:
            current_time = time.time()
            if current_time - self.last_type_time > 0.05 and self.text_index < len(self.current_text):
                self.text_index += 1
                self.sound_system.play_sound("typing")
                self.last_type_time = current_time
            elif self.text_index >= len(self.current_text):
                self.text_fully_displayed = True
            return

        item = self.world.get_item(self.player.x, self.player.y)
        if item:
            self.sound_system.play_sound("item_pickup")
            self.world.remove_item(self.player.x, self.player.y)
            self.samples_collected += 1
        # Update temperature and humidity less frequently
        self.update_counter += 1
        if self.update_counter >= 10:  # Update every 10 frames
            # Update temperature
            self.temperature += self.temp_direction * random.uniform(0.1, 0.2)
            if self.temperature <= 57.0 or self.temperature >= 59.0:
                self.temp_direction *= -1
            self.temperature = max(57.0, min(59.0, self.temperature))

            # Update humidity
            if random.random() < 0.3:  # 30% chance to change humidity each update
                self.humidity += self.humidity_direction
                if self.humidity <= 96 or self.humidity >= 99:
                    self.humidity_direction *= -1
                self.humidity = max(96, min(99, self.humidity))

            self.update_counter = 0

        # Check for text triggers
        text_event = self.world.check_text_trigger(self.player.x, self.player.y)
        if text_event:
            self.show_text(text_event)

        # Update signal strength
        if random.random() < 0.1:  # 10% chance to change signal strength each update
            self.signal_strength += random.uniform(-2, 2)
            self.signal_strength = max(0, min(100, self.signal_strength))

    def render(self):
        self.graphics.clear()
        self.graphics.draw_borders()
        self.graphics.draw_world(self.world, self.player, self.visibility_radius, self.signal_strength)
        self.graphics.draw_char(self.player.x, self.player.y, self.player.char)
        
        if self.text_display_active:
            self.graphics.draw_animated_text(self.current_text, self.text_index)
        else:
            self.graphics.draw_stats(self.samples_collected, self.total_samples, self.temperature, self.humidity, self.signal_strength)
        
        self.graphics.render()

    def run(self):
        if self.show_intro:
            self.show_text(self.intro_text)
            self.show_intro = False

        while self.running:
            self.handle_input()
            self.update()
            self.render()
            pygame.time.wait(50)  # Use pygame's wait function for consistent timing
        self.sound_system.stop_music()

    def show_text(self, text_lines):
        self.text_queue = text_lines
        self.next_text()

    def next_text(self):
        if self.text_queue:
            self.current_text = self.text_queue.pop(0)
            self.text_index = 0
            self.text_display_active = True
            self.text_fully_displayed = False
        else:
            self.text_display_active = False
            self.current_text = ""
            self.text_index = 0
            self.text_fully_displayed = False

def main_menu():
    graphics = Graphics(42, 22)
    sound_system = SoundSystem()
    sound_system.play_music("ambient_horror")
    t = 0
    running = True
    while running:
        start_time = time.time()
        
        graphics.clear()
        graphics.draw_animated_background(t)
        graphics.draw_borders()
        graphics.draw_text(12, 0, f"SYS: {time.strftime('%H:%M:%S')} | MEM: 64kb")
        graphics.draw_text(8, 9, "SMI-1980 Operating Interface")
        graphics.draw_text(12, 11, "1. Initialize")
        graphics.draw_text(12, 12, "2. Terminate")
        graphics.draw_text(14, 21, "v1.19 | 1980 | Subterra LTD")
        graphics.render()

        t += 0.1  # Increment time for animation

        if keyboard.is_pressed('1'):
            return True
        elif keyboard.is_pressed('2'):
            sound_system.stop_music()
            return False

        # Limit the frame rate to about 20 FPS
        elapsed_time = time.time() - start_time
        if elapsed_time < 0.05:
            time.sleep(0.05 - elapsed_time)

    return False

if __name__ == "__main__":
    if main_menu():
        game = Game(42, 22)
        game.run()
    print("Thanks for playing!")
