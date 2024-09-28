import random
from utils import get_random_position

class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.obstacles = set()
        self.items = {}
        self.generate_world()

    def generate_world(self):
        # Generate obstacles
        num_obstacles = (self.width * self.height) // 10
        for _ in range(num_obstacles):
            x, y = get_random_position(self.width, self.height)
            if (x, y) not in self.obstacles and (x, y) != (self.width // 2, self.height // 2):
                self.obstacles.add((x, y))

        # Generate items
        items = ['!', '?', '*']
        num_items = (self.width * self.height) // 20
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