from enum import Enum


class Direction(Enum):
    # left, up, right, down or 0,1,2,3
    LEFT = 0
    WEST = 0
    UP = 1
    NORTH = 1
    RIGHT = 2
    EAST = 2
    DOWN = 3

    def is_x_axis(self):
        return self.value == Direction.LEFT.value or self.value == Direction.RIGHT.value

    # this class is needed to know if x or y will rise when go forward
    def is_x_or_y_rising(self):
        return self.value == Direction.RIGHT.value or self.value == Direction.UP.value
