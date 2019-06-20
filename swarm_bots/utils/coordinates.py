from swarm_bots.utils.direction import Direction


class Coordinates:
    def __init__(self, x: int, y: int):
        self.y = y
        self.x = x

    def get_to_other_direction(self, to_coordinates: 'Coordinates') -> 'Direction':
        if self.x != to_coordinates.x and self.y != to_coordinates.y:
            raise ValueError("x or y coordinate must be same to get direction")
        if self.x == to_coordinates.x:
            if to_coordinates.y > self.y:
                return Direction.UP
            return Direction.DOWN
        if to_coordinates.x > self.x:
            return Direction.RIGHT
        return Direction.LEFT

    def get_straight_distance_to_other(self, direction: Direction, to_coordinates: 'Coordinates') -> int:
        if self.x != to_coordinates.x and self.y != to_coordinates.y:
            raise ValueError("x or y coordinate must be same to get straight distance")
        if self.x == to_coordinates.x:
            if direction.is_x_axis():
                raise ValueError(f"wrong {direction} for straight distance between {self}, {to_coordinates}")
            if direction.is_x_or_y_rising():
                return to_coordinates.y - self.y
            return -(to_coordinates.y - self.y)
        if not direction.is_x_axis():
            raise ValueError(f"wrong {direction} for straight distance between {self}, {to_coordinates}")
        if direction.is_x_or_y_rising():
            return to_coordinates.x - self.x
        return -(to_coordinates.x - self.x)

    def get_array_index(self):
        return self.x, self.y

    def create_moved_coordinate(self, direction: Direction, move_steps: int):
        new_coordinate = Coordinates(self.x, self.y)
        new_coordinate.move_coordinate(direction, move_steps)
        return new_coordinate

    def create_neighbour_coordinate(self, direction: Direction):
        return self.create_moved_coordinate(direction, 1)

    def move_coordinate(self, direction: Direction, move_steps: int):
        if direction.is_x_or_y_rising():
            value_to_add = move_steps
        else:
            value_to_add = -move_steps
        if direction.is_x_axis():
            self.x += value_to_add
        else:
            self.y += value_to_add

    def move_to_neighbour(self, direction: Direction):
        self.move_coordinate(direction, 1)

    def copy(self) -> 'Coordinates':
        return self.__copy__()

    def __copy__(self) -> 'Coordinates':
        return Coordinates(x=self.x, y=self.y)

    def __str__(self):
        return "{x: "+str(self.x)+", y: "+str(self.y)+"}"

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))
