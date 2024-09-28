import keyboard
import time
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
        self.world = World(width, height)
        self.player = Player(width // 2, height // 2)
        self.sound_system = SoundSystem()
        self.running = True
        self.visibility_radius = 5

    def handle_input(self):
        new_x, new_y = self.player.x, self.player.y
        if keyboard.is_pressed('up') and self.player.y > 1:
            new_y -= 1
        elif keyboard.is_pressed('down') and self.player.y < self.height - 2:
            new_y += 1
        elif keyboard.is_pressed('left') and self.player.x > 1:
            new_x -= 1
        elif keyboard.is_pressed('right') and self.player.x < self.width - 2:
            new_x += 1
        elif keyboard.is_pressed('esc'):
            self.running = False

        if not self.world.is_obstacle(new_x, new_y):
            self.player.x, self.player.y = new_x, new_y

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
        self.sound_system.play_music("ambient_horror")
        while self.running:
            self.handle_input()
            self.update()
            self.render()
            time.sleep(0.05)  # Add a small delay to reduce CPU usage

def main_menu():
    graphics = Graphics(42, 22)
    while True:
        graphics.clear()
        graphics.draw_borders()
        graphics.draw_text(16, 9, "ASCII Horror")
        graphics.draw_text(18, 11, "1. Start")
        graphics.draw_text(18, 12, "2. Quit")
        graphics.render()

        key = keyboard.read_event(suppress=True).name
        if key == '1':
            return True
        elif key == '2':
            return False

if __name__ == "__main__":
    if main_menu():
        game = Game(42, 22)
        game.run()
    print("Thanks for playing!")
