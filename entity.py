class Entity:
    def __init__(self, x, y, char):
        self.x = x
        self.y = y
        self.char = char

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
