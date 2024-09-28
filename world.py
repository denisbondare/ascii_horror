import random
from utils import get_random_position

class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.obstacles = set()
        self.items = {}
        self.generate_world()
        self.text_triggers = {
            (5, 5): ["You found a mysterious note.", "It reads: 'Beware of the shadows.'"],
            (15, 10): ["A cold wind blows through the area.", "You hear whispers in the distance."],
        }

    def generate_world(self):
        # Generate border walls
        for x in range(self.width):
            for y in range(10):
                self.obstacles.add((x, y))
                self.obstacles.add((x, self.height - 1 - y))
        for y in range(self.height):
            for x in range(10):
                self.obstacles.add((x, y))
                self.obstacles.add((self.width - 1 - x, y))

        # Generate obstacles
        num_obstacles = (self.width * self.height) // 20  # Reduced number of obstacles
        for _ in range(num_obstacles):
            x, y = get_random_position(self.width, self.height)
            if (x, y) not in self.obstacles and (x, y) != (self.width // 2, self.height // 2):
                self.obstacles.add((x, y))

        # Generate items
        items = ['*']
        num_items = (self.width * self.height) // 50  # Reduced number of items
        for _ in range(num_items):
            x, y = get_random_position(self.width, self.height)
            if (x, y) not in self.obstacles and (x, y) not in self.items and (x, y) != (self.width // 2, self.height // 2):
                self.items[(x, y)] = random.choice(items)

    def is_obstacle(self, x, y):
        return (x, y) in self.obstacles

    def get_item(self, x, y):
        return self.items.get((x, y))

    def remove_item(self, x, y):
        if (x, y) in self.items:
            del self.items[(x, y)]
            return True
        return False

    def generate_new_item(self):
        items = ['!', '?', '*']
        x, y = get_random_position(self.width, self.height)
        attempts = 0
        while attempts < 100:  # Limit attempts to avoid infinite loop
            if (x, y) not in self.obstacles and (x, y) not in self.items:
                self.items[(x, y)] = random.choice(items)
                return
            x, y = get_random_position(self.width, self.height)
            attempts += 1

    def check_text_trigger(self, x, y):
        if (x, y) in self.text_triggers:
            return self.text_triggers[(x, y)]
        return None

    def move(self, dx, dy):
        # Move all objects in the opposite direction of player movement
        new_obstacles = set()
        for x, y in self.obstacles:
            new_obstacles.add((x - dx, y - dy))
        self.obstacles = new_obstacles

        new_items = {}
        for (x, y), item in self.items.items():
            new_items[(x - dx, y - dy)] = item
        self.items = new_items

        new_text_triggers = {}
        for (x, y), trigger in self.text_triggers.items():
            new_text_triggers[(x - dx, y - dy)] = trigger
        self.text_triggers = new_text_triggers