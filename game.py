import keyboard
import time
import pygame
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
        self.world = World(width, height - 3)  # Adjust world height
        self.player = Player(width // 2, (height - 3) // 2)  # Adjust player starting position
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
            "Mission: Collect 50 material samples.",
            "Arrow keys to control machine.",
            "Automatic evacuation upon completion.",
            "Warning: Unusual readings detected.",
            "Press Enter to initiate operation."
        ]
        self.show_intro = True
        self.text_fully_displayed = False

    def handle_input(self):
        if self.text_display_active:
            if keyboard.is_pressed('enter') and self.text_fully_displayed:
                self.next_text()
            return

        new_x, new_y = self.player.x, self.player.y
        moved = False
        if keyboard.is_pressed('up') and self.player.y > 1:
            self.vertical_step += 1
            if self.vertical_step >= 2:
                new_y -= 1
                self.vertical_step = 0
            moved = True
        elif keyboard.is_pressed('down') and self.player.y < self.height - 2:
            self.vertical_step += 1
            if self.vertical_step >= 2:
                new_y += 1
                self.vertical_step = 0
            moved = True
        elif keyboard.is_pressed('left') and self.player.x > 1:
            new_x -= 1
            moved = True
        elif keyboard.is_pressed('right') and self.player.x < self.width - 2:
            new_x += 1
            moved = True
        elif keyboard.is_pressed('esc'):
            self.running = False

        if not self.world.is_obstacle(new_x, new_y):
            self.player.x, self.player.y = new_x, new_y
            if moved:
                self.step_counter += 1
                if self.step_counter % 2 == 0:  # Play footstep sound every other step
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

        # Check for text triggers
        text_event = self.world.check_text_trigger(self.player.x, self.player.y)
        if text_event:
            self.show_text(text_event)

    def render(self):
        self.graphics.clear()
        self.graphics.draw_borders()
        self.graphics.draw_world(self.world, self.player, self.visibility_radius)
        self.graphics.draw_char(self.player.x, self.player.y, self.player.char)
        
        if self.text_display_active:
            self.graphics.draw_animated_text(self.current_text, self.text_index)
        
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
        graphics.draw_text(16, 9, "ASCII Horror")
        graphics.draw_text(18, 11, "1. Start")
        graphics.draw_text(18, 12, "2. Quit")
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
