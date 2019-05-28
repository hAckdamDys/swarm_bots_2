class Coordinates:
    def __init__(self, x: int, y: int):
        self.y = y
        self.x = x

    def get_array_index(self):
        return self.x, self.y
