from enum import Enum
from typing import List

from swarm_bots.utils.coordinates import Coordinates
from swarm_bots.utils.direction import Direction


class Spin(Enum):
    CLOCKWISE = 0
    ANTI_CLOCKWISE = 1

    def get_opposite(self) -> 'Spin':
        if self == Spin.CLOCKWISE:
            return Spin.ANTI_CLOCKWISE
        return Spin.CLOCKWISE

    def get_pre_corner_coordinates(self, corner: Coordinates) -> Coordinates:
        if self == Spin.CLOCKWISE:
            if corner.x == 0:
                if corner.y == 0:
                    return Coordinates(0, 1)
                # we assume y == height
                return Coordinates(1, corner.y)
            # we assume x == width
            elif corner.y != 0:
                # we assume y == height
                return Coordinates(corner.x, corner.y - 1)
            return Coordinates(corner.x - 1, 0)
        if corner.x == 0:
            if corner.y == 0:
                return Coordinates(1, 0)
            # we assume y == height
            return Coordinates(0, corner.y - 1)
        # we assume x == width
        elif corner.y != 0:
            # we assume y == height
            return Coordinates(corner.x - 1, corner.y)
        return Coordinates(corner.x, 1)

    def get_edge_move_direction(self, edge_side: Direction) -> Direction:
        if self == Spin.CLOCKWISE:
            if edge_side == Direction.UP:
                return Direction.RIGHT
            elif edge_side == Direction.RIGHT:
                return Direction.DOWN
            elif edge_side == Direction.DOWN:
                return Direction.LEFT
            else:
                return Direction.UP
        if edge_side == Direction.UP:
            return Direction.LEFT
        elif edge_side == Direction.LEFT:
            return Direction.DOWN
        elif edge_side == Direction.DOWN:
            return Direction.RIGHT
        else:
            return Direction.UP

    def get_edge_next_corner(self, edge_side: Direction, width: int, height: int) -> Coordinates:
        if self == Spin.CLOCKWISE:
            if edge_side == Direction.UP:
                return Coordinates(width, height)
            elif edge_side == Direction.RIGHT:
                return Coordinates(width, 0)
            elif edge_side == Direction.DOWN:
                return Coordinates(0, 0)
            else:
                return Coordinates(0, height)
        if edge_side == Direction.UP:
            return Coordinates(0, height)
        elif edge_side == Direction.LEFT:
            return Coordinates(0, 0)
        elif edge_side == Direction.DOWN:
            return Coordinates(width, 0)
        else:
            return Coordinates(width, height)

    def get_directions(self) -> List[Direction]:
        if self == Spin.CLOCKWISE:
            return [Direction.DOWN, Direction.LEFT, Direction.UP, Direction.RIGHT]
        return [Direction.DOWN, Direction.RIGHT, Direction.UP, Direction.LEFT]

    def should_edge_reverse_indexes(self, edge_side: Direction) -> bool:
        should_reverse = False
        if self == Spin.CLOCKWISE:
            should_reverse = True
        if edge_side == Direction.UP:
            return not should_reverse
        elif edge_side == Direction.RIGHT:
            return should_reverse
        elif edge_side == Direction.DOWN:
            return should_reverse
        else:
            return not should_reverse
