from entity import Entity

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, '@')
