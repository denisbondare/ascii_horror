import random
from utils import get_random_position
from config import *

class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.obstacles = set()
        self.items = {}
        self.generate_world()

    def generate_world(self):
        self.create_rooms_and_halls()
        self.add_items()

    def create_rooms_and_halls(self):
        # Start with an empty grid
        self.grid = [[1 for _ in range(self.width)] for _ in range(self.height)]
        
        # Create a number of rooms and halls
        num_structures = random.randint(5, 15)
        for _ in range(num_structures):
            if random.random() < 0.7:  # 70% chance for a room
                self.create_room()
            else:
                self.create_hall()
        
        # Connect isolated structures
        self.connect_structures()
        
        # Convert grid to obstacles
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == 1:
                    self.obstacles.add((x, y))

    def create_room(self):
        width = random.randint(3, 8)
        height = random.randint(3, 8)
        x = random.randint(1, self.width - width - 1)
        y = random.randint(1, self.height - height - 1)
        
        for i in range(y, y + height):
            for j in range(x, x + width):
                self.grid[i][j] = 0
        
        # Add doors
        num_doors = random.randint(1, 4)
        for _ in range(num_doors):
            door_side = random.choice(['top', 'bottom', 'left', 'right'])
            if door_side == 'top':
                self.grid[y][random.randint(x + 1, x + width - 2)] = 0
            elif door_side == 'bottom':
                self.grid[y + height - 1][random.randint(x + 1, x + width - 2)] = 0
            elif door_side == 'left':
                self.grid[random.randint(y + 1, y + height - 2)][x] = 0
            else:
                self.grid[random.randint(y + 1, y + height - 2)][x + width - 1] = 0

    def create_hall(self):
        if random.random() < 0.5:  # Horizontal hall
            width = random.randint(5, 15)
            height = random.randint(2, 3)
            x = random.randint(1, self.width - width - 1)
            y = random.randint(1, self.height - height - 1)
        else:  # Vertical hall
            width = random.randint(2, 3)
            height = random.randint(5, 15)
            x = random.randint(1, self.width - width - 1)
            y = random.randint(1, self.height - height - 1)
        
        for i in range(y, y + height):
            for j in range(x, x + width):
                self.grid[i][j] = 0

    def connect_structures(self):
        def find_empty_neighbor(x, y):
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            random.shuffle(directions)
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height and self.grid[ny][nx] == 0:
                    return nx, ny
            return None

        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.grid[y][x] == 0:
                    neighbor = find_empty_neighbor(x, y)
                    if neighbor:
                        nx, ny = neighbor
                        self.grid[y + (ny - y) // 2][x + (nx - x) // 2] = 0

    def add_items(self):
        items = ['!', '?', '*']
        num_items = (self.width * self.height) // ITEM_DENSITY
        for _ in range(num_items):
            x, y = get_random_position(self.width - 2, self.height - 2)
            x, y = x + 1, y + 1  # Offset by 1 to avoid borders
            if (x, y) not in self.obstacles and (x, y) not in self.items and (x, y) != (PLAYER_START_X, PLAYER_START_Y):
                self.items[(x, y)] = random.choice(items)

    def is_obstacle(self, x, y):
        return (x, y) in self.obstacles

    def get_item(self, x, y):
        return self.items.get((x, y))

    def remove_item(self, x, y):
        if (x, y) in self.items:
            del self.items[(x, y)]