import random
import time
from utils import get_random_position, distance, generate_perlin_noise
from collections import deque
import heapq

class EchoSource:
    def __init__(self, x, y, player):
        self.x = x
        self.y = y
        self.player = player
        self.speed = 1
        self.path = []
        self.path_update_cooldown = 0
        self.last_known_player_pos = (player.x, player.y)
        self.last_move_time = time.time()
        self.move_cooldown = 0.33        
    def move(self, world):
        self.last_move_time = time.time()
        current_player_pos = (self.player.x, self.player.y)
        
        # Check if player has moved significantly
        if distance(self.last_known_player_pos[0], self.last_known_player_pos[1], current_player_pos[0], current_player_pos[1]) > 3:
            self.update_path(world)
            self.last_known_player_pos = current_player_pos
        
        if not self.path:
            self.update_path(world)
        
        if self.path:
            next_x, next_y = self.path.pop(0)
            if not world.is_obstacle(next_x, next_y):
                self.x, self.y = next_x, next_y
        
        self.path_update_cooldown -= 1
        if self.path_update_cooldown <= 0:
            self.update_path(world)

    def update_path(self, world):
        self.path = self.find_path(world, (self.x, self.y), (self.player.x, self.player.y))
        self.path_update_cooldown = random.randint(160, 240)  # Update path every 4-6 seconds (assuming 30 FPS)

    def find_path(self, world, start, goal):
        def heuristic(a, b):
            return abs(b[0] - a[0]) + abs(b[1] - a[1])

        def get_neighbors(pos):
            x, y = pos
            neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
            return [(nx, ny) for nx, ny in neighbors if 0 <= nx < world.width and 0 <= ny < world.height and not world.is_obstacle(nx, ny)]

        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}

        while frontier:
            current = heapq.heappop(frontier)[1]

            if current == goal:
                break

            for next in get_neighbors(current):
                new_cost = cost_so_far[current] + 1
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + heuristic(goal, next)
                    heapq.heappush(frontier, (priority, next))
                    came_from[next] = current

        # Reconstruct path
        path = []
        current = goal
        while current != start:
            path.append(current)
            current = came_from.get(current)
            if current is None:  # No path found
                return []
        path.reverse()
        return path[:self.speed]  # Return only the next few steps based on speed

class World:
    def __init__(self, width, height, player):
        self.player = player
        self.width = width
        self.height = height
        self.obstacles = set()
        self.items = {}
        self.generate_world()
        self.text_triggers = {}
        self.echo_sources = []
        #self.generate_echo_sources()

        self.scary_texts = [
            "⛧ ŸØÜ'RÈ MÏÑÈ ÑØW.",
            "⚮ ŁÈÅVÈ WHÏŁÈ ŸØÜ ÇÅÑ.",
            "⛥ Ï §ÈÈ ŸØÜ, ÏÑTRÜÐÈR.",
            "⚝ ŸØÜR FÈÅR FÈÈÐ§ MÈ.",
            "⍜ RÜÑ, ŁÏTTŁÈ ØÑÈ.",
            "⛇ THÏ§ PŁÅÇÈ HÜÑGÈR§.",
            "⚹ ŸØÜ'ŁŁ ÑÈVÈR È§ÇÅPÈ.",
            "⍭ Ï ÅM ÈVÈRŸWHÈRÈ.",
            "⛮ ŸØÜR TÏMÈ Ï§ §HØRT.",
            "⚶ JØÏÑ Ü§ ÏÑ ÐÅRKÑÈ§§."
        ]
        self.used_scary_texts = set()
        
        self.system_texts = {
            "low_temperature": "WARNING: Critically low temp.",
            "high_temperature": "ALERT: Extreme heat.",
            "low_signal": "CAUTION: Weak signal.",
            "very_low_signal": "ALERT: Signal loss.",
            "high_humidity": "NOTICE: High humidity.",
            "sensor_malfunction": "ERROR: Sensors corrupted.",
            "unknown_readings": "NOTICE: Unknown signal.",
            "power_fluctuation": "WARNING: Power unstable.",
            "radiation_spike": "NOTICE: Radiation detected.",
            "magnetic_interference": "CAUTION: Magnetic interference."
        }

    def generate_world(self):
        # Generate cave-like terrain using Perlin noise
        scale = 0.2
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

        # Move echo sources
        for source in self.echo_sources:
            source.x -= dx
            source.y -= dy

    def generate_echo_sources(self):
        num_sources = 1  # You can adjust this number
        accessible_positions = self.get_accessible_positions()
        min_distance = 50  # Minimum distance from player, adjust as needed
        max_distance = 60
        
        for _ in range(num_sources):
            if not accessible_positions:
                break  # Stop if we run out of accessible positions
            
            valid_positions = [pos for pos in accessible_positions 
                               if distance(pos[0], pos[1], self.player.x, self.player.y) >= min_distance
                               and distance(pos[0], pos[1], self.player.x, self.player.y) <= max_distance]
            
            if not valid_positions:
                break  # No valid positions far enough from the player
            
            pos = random.choice(valid_positions)
            self.echo_sources.append(EchoSource(pos[0], pos[1], self.player))
            accessible_positions.remove(pos)

    def get_accessible_positions(self):
        start_x, start_y = self.width // 2, self.height // 2  # Assuming player starts at the center
        visited = set()
        queue = deque([(start_x, start_y)])
        accessible = []

        while queue:
            x, y = queue.popleft()
            if (x, y) in visited:
                continue

            visited.add((x, y))
            if not self.is_obstacle(x, y):
                accessible.append((x, y))

            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height and (nx, ny) not in visited:
                    queue.append((nx, ny))

        return accessible

    def update_echo_sources(self):
        current_time = time.time()
        for source in self.echo_sources:            
            # Move once every X seconds
            # Calculate distance to player
            dist_to_player = distance(source.x, source.y, self.player.x, self.player.y)
            
            # Adjust move cooldown based on distance
            if dist_to_player > 30:
                move_cooldown = source.move_cooldown * 3
            else:
                # Linear progression
                move_cooldown = 0.033 + (dist_to_player / 30) * (source.move_cooldown * 3 - 0.033)
            if current_time - source.last_move_time >= move_cooldown:
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