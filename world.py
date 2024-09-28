import random
from utils import get_random_position, distance, generate_perlin_noise

class EchoSource:
    def __init__(self, x, y, player):
        self.x = x
        self.y = y
        self.move_cooldown = 0
        self.move_direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        self.max_distance = 100
        self.player = player
        self.speed = 2
    def move(self, world):
        self.move_cooldown -= 1
        if self.move_cooldown <= 0:
            dx = self.player.x - self.x
            dy = self.player.y - self.y
            
            # Normalize the direction vector
            length = max(abs(dx), abs(dy), 1)
            dx = dx / length
            dy = dy / length
            
            # Round to nearest integer (-1, 0, or 1)
            dx = round(dx)
            dy = round(dy)
            
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed
            
            if 0 <= new_x < world.width and 0 <= new_y < world.height and not world.is_obstacle(new_x, new_y):
                self.x = new_x
                self.y = new_y
            
            self.move_cooldown = random.randint(300, 300)  # Slow down the movement

class World:
    def __init__(self, width, height, player):
        self.player = player
        self.width = width
        self.height = height
        self.obstacles = set()
        self.items = {}
        self.generate_world()
        self.text_triggers = {
            (5, 5): ["You found a mysterious note.", "It reads: 'Beware of the shadows.'"],
            (15, 10): ["A cold wind blows through the area.", "You hear whispers in the distance."],
        }
        self.echo_sources = []
        self.generate_echo_sources()

        self.scary_texts = [
            "⛧ You're mine now.",
            "⚮ Leave while you can.",
            "⛥ I see you, intruder.",
            "⚝ Your fear feeds me.",
            "⍜ Run, little one.",
            "⛇ This place hungers.",
            "⚹ You'll never escape.",
            "⍭ I am everywhere.",
            "⛮ Your time is short.",
            "⚶ Join us in darkness."
        ]
        self.used_scary_texts = set()
        
        self.system_texts = {
            "low_temperature": "WARNING: Critically low temp.",
            "high_temperature": "ALERT: Extreme heat.",
            "low_signal": "CAUTION: Weak signal.",
            "very_low_signal": "DANGER: Signal loss.",
            "high_humidity": "NOTICE: High humidity.",
            "sensor_malfunction": "ERROR: Sensors corrupted.",
            "unknown_readings": "ANOMALY: Unknown energy.",
            "power_fluctuation": "WARNING: Power unstable.",
            "radiation_spike": "ALERT: Radiation detected.",
            "magnetic_interference": "CAUTION: Magnetic interference."
        }

    def generate_world(self):
        # Generate cave-like terrain using Perlin noise
        scale = 0.1
        octaves = 6
        persistence = 0.5
        lacunarity = 2.0
        threshold = 0.1  # Adjust this to control cave density

        for x in range(self.width):
            for y in range(self.height):
                if x < 10 or x >= self.width - 10 or y < 10 or y >= self.height - 10:
                    self.obstacles.add((x, y))  # Create border walls
                else:
                    value = generate_perlin_noise(x, y, 0, scale, octaves, persistence, lacunarity)
                    if value > threshold:
                        self.obstacles.add((x, y))

        # Ensure the player's starting position is clear
        player_area = [(x, y) for x in range(self.width // 2 - 5, self.width // 2 + 6)
                              for y in range(self.height // 2 - 5, self.height // 2 + 6)]
        for pos in player_area:
            if pos in self.obstacles:
                self.obstacles.remove(pos)

        self.generate_items()

    def generate_items(self):
        items = ['+']
        num_items = 50
        min_distance = 10  # Minimum distance between items

        for _ in range(num_items):
            attempts = 0
            while attempts < 100:  # Limit attempts to avoid infinite loop
                x, y = get_random_position(self.width, self.height)
                if (x, y) not in self.obstacles and (x, y) not in self.items and \
                   (x, y) != (self.width // 2, self.height // 2) and \
                   all(distance(x, y, ix, iy) >= min_distance for ix, iy in self.items):
                    self.items[(x, y)] = random.choice(items)
                    break
                attempts += 1

        # Ensure we have enough items
        while len(self.items) < num_items:
            x, y = get_random_position(self.width, self.height)
            if (x, y) not in self.obstacles and (x, y) not in self.items and \
               (x, y) != (self.width // 2, self.height // 2):
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
        items = ['+']
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

    def generate_echo_sources(self):
        num_sources = 50  # You can adjust this number
        for _ in range(num_sources):
            x, y = get_random_position(self.width, self.height)
            while self.is_obstacle(x, y) or (x, y) in self.items:
                x, y = get_random_position(self.width, self.height)
            self.echo_sources.append(EchoSource(x, y, self.player))

    def update_echo_sources(self):
        for source in self.echo_sources:
            source.move(self)

    def get_nearest_echo_source(self, x, y):
        if not self.echo_sources:
            return None, float('inf')
        nearest = min(self.echo_sources, key=lambda s: distance(x, y, s.x, s.y))
        return nearest, distance(x, y, nearest.x, nearest.y)

    def get_random_scary_text(self):
        available_texts = set(self.scary_texts) - self.used_scary_texts
        if not available_texts:
            self.used_scary_texts.clear()
            available_texts = set(self.scary_texts)
        
        chosen_text = random.choice(list(available_texts))
        self.used_scary_texts.add(chosen_text)
        return chosen_text

    def get_system_text(self, key):
        return self.system_texts.get(key, "System message unavailable.")