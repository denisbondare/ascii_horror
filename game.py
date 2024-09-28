from config import *
import keyboard
import time
import pygame
from graphics import Graphics
from player import Player
from world import World
from utils import get_random_position, distance
from sounds import SoundSystem

class Game:
    def __init__(self):
        self.width = GAME_WIDTH
        self.height = GAME_HEIGHT
        self.graphics = Graphics(self.width, self.height)
        self.world = World(self.width, self.height)
        self.player = Player(PLAYER_START_X, PLAYER_START_Y)
        self.sound_system = SoundSystem()
        self.running = True
        self.visibility_radius = VISIBILITY_RADIUS
        self.step_counter = 0
        self.sound_system.play_music("ambient_horror")
        self.vertical_step = 0  # Add this line

    def handle_input(self):
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
        item = self.world.get_item(self.player.x, self.player.y)
        if item:
            self.sound_system.play_sound("item_pickup")
            self.world.remove_item(self.player.x, self.player.y)

    def render(self):
        self.graphics.clear()
        self.graphics.draw_borders()
        self.graphics.draw_world(self.world, self.player, self.visibility_radius)
        self.graphics.draw_char(self.player.x, self.player.y, self.player.char)
        self.graphics.render()

    def run(self):
        while self.running:
            self.handle_input()
            self.update()
            self.render()
            pygame.time.wait(50)  # Use pygame's wait function for consistent timing
        self.sound_system.stop_music()

def main_menu():
    graphics = Graphics(GAME_WIDTH, GAME_HEIGHT)
    sound_system = SoundSystem()
    sound_system.play_music("ambient_horror")
    t = 0
    running = True
    while running:
        start_time = time.time()
        
        graphics.clear()
        graphics.draw_animated_background(t)
        graphics.draw_borders()
        graphics.draw_text(16, 9, MENU_TITLE)
        graphics.draw_text(18, 11, MENU_START_OPTION)
        graphics.draw_text(18, 12, MENU_QUIT_OPTION)
        graphics.render()

        t += ANIMATION_SPEED  # Increment time for animation

        if keyboard.is_pressed('1'):
            return True
        elif keyboard.is_pressed('2'):
            sound_system.stop_music()
            return False

        # Limit the frame rate to about 20 FPS
        elapsed_time = time.time() - start_time
        if elapsed_time < 1/FPS:
            time.sleep(1/FPS - elapsed_time)

    return False

if __name__ == "__main__":
    if main_menu():
        game = Game()
        game.run()
    print("Thanks for playing!")
