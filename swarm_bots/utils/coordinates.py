from swarm_bots.utils.direction import Direction


class Coordinates:
    def __init__(self, x: int, y: int):
        self.y = y
        self.x = x

    def get_array_index(self):
        return self.x, self.y

    def create_moved_coordinate(self, direction: Direction, move_steps: int):
        if direction.is_x_or_y_rising():
            value_to_add = move_steps
        else:
            value_to_add = -move_steps
        if direction.is_x_axis():
            return Coordinates(self.x + value_to_add, self.y)
        else:
            return Coordinates(self.x, self.y + value_to_add)

    def create_neighbour_coordinate(self, direction: Direction):
        return self.create_moved_coordinate(direction, 1)

    def __str__(self):
        return "{x: "+str(self.x)+", y: "+str(self.y)+"}"
