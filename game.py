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
        self.player = Player(128, 128)  # Start player in the center of the world
        self.world = World(256, 256, self.player)  # Much larger world
        self.sound_system = SoundSystem()
        self.running = True
        self.visibility_radius = 10
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
            "Mission: Collect 10 material samples.",
            "Arrow keys to control machine.",
            "Automatic evacuation upon completion.",
            "Warning: Unusual readings detected.",
            "Press Enter to initiate operation."
        ]
        self.show_intro = True
        self.text_fully_displayed = False
        self.samples_collected = 0
        self.total_samples = 10
        self.temperature = 57.0
        self.humidity = 98
        self.signal_strength = 80
        self.temp_direction = random.choice([-1, 1])
        self.humidity_direction = random.choice([-1, 1])
        self.update_counter = 0
        self.last_update_time = time.time()
        self.movement_step = 0
        self.echo_cooldown = 0
        self.last_scary_text_time = 0
        self.last_system_message_time = {}
        self.current_system_message = ""
        self.system_message_index = 0
        self.system_message_start_time = 0
        self.current_scary_text = ""
        self.scary_text_index = 0
        self.scary_text_start_time = 0
        self.current_message = ""
        self.message_index = 0
        self.message_start_time = 0
        self.message_type = None  # Can be "scary" or "system"
        self.game_over = False
        self.game_won = False
        self.low_signal_start_time = None
        self.total_time = 0
        self.start_time = time.time()
        
    def set_temperature(self, value):
        self.temperature = value
        self.temperature = max(-148, min(100, self.temperature))

    def set_signal_strength(self, value):
        self.signal_strength = value
        self.signal_strength = max(1, min(100, self.signal_strength))
        self.sound_system.update_signal_strength(self.signal_strength)

    def handle_input(self):
        if self.text_display_active:
            if keyboard.is_pressed('enter'):
                if self.text_fully_displayed:
                    self.next_text()
                else:
                    self.text_index = len(self.current_text)
                    self.text_fully_displayed = True
            return

        dx, dy = 0, 0
        moved = False
        self.movement_step += 1
        if self.movement_step >= 1:  # Slow down overall movement
            if keyboard.is_pressed('up') and self.player.y > 1:
                self.vertical_step += 1
                if self.vertical_step >= 3:  # Further slow down vertical movement
                    dy = -1
                    self.vertical_step = 0
                moved = True
            elif keyboard.is_pressed('down') and self.player.y < self.world.height - 2:
                self.vertical_step += 1
                if self.vertical_step >= 3:  # Further slow down vertical movement
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
                self.update_signal_strength(10)
            elif keyboard.is_pressed('i'):
                self.update_signal_strength(-10)
            elif keyboard.is_pressed('esc'):
                self.running = False
            # Test keys for winning and losing
            elif keyboard.is_pressed('w'):  # 'w' for win
                self.samples_collected = self.total_samples
            elif keyboard.is_pressed('l'):  # 'l' for lose
                self.signal_strength = 1
                self.low_signal_start_time = time.time() - 6  # Force immediate loss

            if moved:
                self.movement_step = 0

        if not self.world.is_obstacle(self.player.x + dx, self.player.y + dy):
            self.world.move(dx, dy)  # Move the world instead of the player
            if moved:
                self.step_counter += 1
                if self.step_counter % 2 == 0:
                    self.sound_system.play_sound("footstep")

    def update(self):
        if self.game_over or self.game_won:
            return

        current_time = time.time()
        frame_time = 1 / 10 
        
        # Calculate the time elapsed since the last update
        elapsed_time = current_time - self.last_update_time
        
        # Only process the last frame
        if elapsed_time >= frame_time:
            self.last_update_time = current_time
            self._process_frame(elapsed_time)

        # Check win condition
        if self.samples_collected >= self.total_samples:
            self.game_won = True
            self.total_time = int(time.time() - self.start_time)

        # Check lose condition
        if self.signal_strength < 10:
            if self.low_signal_start_time is None:
                self.low_signal_start_time = current_time
            elif current_time - self.low_signal_start_time >= 5:
                self.game_over = True
        else:
            self.low_signal_start_time = None

    def _process_frame(self, delta_time):
        if self.text_display_active:
            if time.time() - self.last_type_time > 0.02 and self.text_index < len(self.current_text):
                self.text_index += random.randint(1, 2)
                self.sound_system.play_sound("typing")
                self.last_type_time = time.time()
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

        # Update ambient sounds
        self.sound_system.update_ambient_sounds(delta_time)

        # Update echo sources
        self.world.update_echo_sources()
        
        nearest_source, distance = self.world.get_nearest_echo_source(self.player.x, self.player.y)
        
        # Handle echo effects
        self.echo_cooldown -= 1
        if self.echo_cooldown <= 0:
            if nearest_source and distance < nearest_source.max_distance:  # Only play echo if within range
                direction = (nearest_source.x - self.player.x) / distance
                self.sound_system.play_echo(direction, distance)
                # Calculate screen coordinates for the echo source
                self.graphics.add_ripple(nearest_source.x, nearest_source.y)
                self.echo_cooldown = random.randint(30, 60)  # Wait 30-60 frames before next echo

        # Update ripples
        self.graphics.update_ripples()

        signal_change = 91 * (distance**1.5 / nearest_source.max_distance)
        temperature_change = -148.0 * (1 - distance**1.7 / nearest_source.max_distance) + random.uniform(-0.3, 0.3)
        max_temp = 59 + random.uniform(-0.1, 0.1)
        self.set_temperature(min(max_temp, max(-148.0, temperature_change)))
        max_signal = 91 + random.uniform(-1, 1)+ random.uniform(-1, 1)
        self.set_signal_strength(min(max_signal, max(1, signal_change)))

        # Handle echo effects and scary texts
        if nearest_source and distance < nearest_source.max_distance / 4:
            if time.time() - self.last_scary_text_time > 15 and random.random() < 0.1:
                self.show_message(self.world.get_random_scary_text(), "scary")

        # Handle system messages only if there's no current message
        if not self.current_message:
            self.check_system_messages()

        # Update text animations
        self.update_text_animations()

    def check_system_messages(self):
        current_time = time.time()
        
        # Check temperature
        if self.temperature < -100 and self.check_message_cooldown("low_temperature", current_time):
            self.show_message(self.world.get_system_text("low_temperature"), "system")
        elif self.temperature > 90 and self.check_message_cooldown("high_temperature", current_time):
            self.show_message(self.world.get_system_text("high_temperature"), "system")

        # Check signal strength
        if self.signal_strength < 20 and self.check_message_cooldown("low_signal", current_time):
            self.show_message(self.world.get_system_text("low_signal"), "system")
        elif self.signal_strength < 10 and self.check_message_cooldown("very_low_signal", current_time):
            self.show_message(self.world.get_system_text("very_low_signal"), "system")

        # Check humidity
        #if self.humidity > 98 and self.check_message_cooldown("high_humidity", current_time):
        #    self.show_message(self.world.get_system_text("high_humidity"), "system")

        # Random system messages (very rare)
        if random.random() < 0.005:  # Adjust this probability as needed
            random_message = random.choice(["sensor_malfunction", "unknown_readings", "power_fluctuation", "radiation_spike", "magnetic_interference"])
            if self.check_message_cooldown(random_message, current_time):
                self.show_message(self.world.get_system_text(random_message), "system")

    def check_message_cooldown(self, message_type, current_time):
        if message_type not in self.last_system_message_time or current_time - self.last_system_message_time[message_type] > 30:
            self.last_system_message_time[message_type] = current_time
            return True
        return False

    def show_message(self, text, message_type):
        if not self.current_message or message_type == "scary":
            self.current_message = text
            self.message_index = 0
            self.message_start_time = time.time()
            self.message_type = message_type
            if message_type == "scary":
                self.last_scary_text_time = time.time()

    def update_text_animations(self):
        current_time = time.time()

        if self.current_message:
            if self.message_index < len(self.current_message):
                if current_time - self.message_start_time > 0.02 * self.message_index:
                    self.message_index += random.randint(1, 2)
                    self.sound_system.play_sound("typing")
            elif current_time - self.message_start_time > 2:
                self.current_message = ""
                self.message_type = None

    def render(self):
        if self.game_won:
            self.render_win_screen()
        elif self.game_over:
            self.render_lose_screen()
        else:
            self.graphics.clear()
            self.graphics.draw_borders()
            self.graphics.draw_world(self.world, self.player, self.visibility_radius, self.signal_strength)
            self.graphics.draw_char(self.player.x, self.player.y, self.player.char)
            
            if self.text_display_active:
                self.graphics.draw_animated_text(self.current_text, self.text_index)
            elif self.current_message:
                self.graphics.draw_animated_text(self.current_message[:self.message_index], self.message_index)
            else:
                self.graphics.draw_stats(self.samples_collected, self.total_samples, self.temperature, self.humidity, self.signal_strength)
            
            self.graphics.render()

    def render_win_screen(self):
        self.graphics.clear()
        self.graphics.draw_animated_background(time.time())
        self.graphics.draw_borders()
        self.graphics.draw_text(16, 0, f"SYS: {time.strftime('%H:%M:%S')} | MEM: 64kb")
        self.graphics.draw_text(12, 9, "| OPERATION COMPLETE |")
        self.graphics.draw_text(13, 11, f"Total Time: {self.total_time}s")
        self.graphics.draw_text(13, 13, " 1. Restart ")
        self.graphics.draw_text(13, 14, " 2. Terminate ")
        self.graphics.draw_text(12, 21, "| v1.19 | 1980 | Subterra LTD")
        self.graphics.render()

    def render_lose_screen(self):
        self.graphics.clear()
        self.graphics.draw_animated_background(time.time())
        self.graphics.draw_borders()
        self.graphics.draw_text(16, 0, f"SYS: {time.strftime('%H:%M:%S')} | MEM: 64kb")
        self.graphics.draw_text(13, 9, "| CONNECTION LOST |")
        self.graphics.draw_text(13, 13, " 1. Restart ")
        self.graphics.draw_text(13, 14, " 2. Terminate ")
        self.graphics.draw_text(12, 21, "| v1.19 | 1980 | Subterra LTD")
        self.graphics.render()

    def run(self):
        if self.show_intro:
            self.show_text(self.intro_text)
            self.show_intro = False

        while self.running:
            self.handle_input()
            self.update()
            self.render()

            if self.game_over or self.game_won:
                choice = self.handle_end_game_input()
                if choice == 1:
                    return True  # Restart the game
                elif choice == 2:
                    self.running = False

        self.sound_system.stop_music()
        return False  # Terminate the game

    def handle_end_game_input(self):
        if keyboard.is_pressed('1'):
            return 1
        elif keyboard.is_pressed('2'):
            return 2
        return None

    def show_text(self, text_lines):
        self.text_queue = text_lines
        self.next_text()
        self.text_display_active = True

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
        graphics.draw_text(16, 0, f"SYS: {time.strftime('%H:%M:%S')} | MEM: 64kb")
        graphics.draw_text(5, 9, "| SMI-1980 Operating Interface |")
        graphics.draw_text(13, 11, " 1. Initialize ")
        graphics.draw_text(13, 12, " 2. Terminate ")
        graphics.draw_text(12, 21, "| v1.19 | 1980 | Subterra LTD")
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
    while True:
        if main_menu():
            game = Game(42, 22)
            if not game.run():
                break
        else:
            break