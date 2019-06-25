from swarm_bots.robot_executors.spiral.source_positions.position import SourcePosition
from swarm_bots.utils.coordinates import Coordinates
from swarm_bots.utils.direction import Direction
from swarm_bots.utils.spin import Spin


class SpunPositions:
    def __init__(self, spin: Spin, width: int, height: int):
        self.height = height
        self.width = width
        self.spin = spin

    def get_position(self, direction: Direction) -> SourcePosition:
        max_x = self.width - 1
        max_y = self.height - 1
        if direction == Direction.LEFT:
            if self.spin == Spin.CLOCKWISE:
                return SourcePosition(Coordinates(0, 0))
            else:
                return SourcePosition(Coordinates(0, max_y))
        elif direction == Direction.UP:
            if self.spin == Spin.CLOCKWISE:
                return SourcePosition(Coordinates(0, max_y))
            else:
                return SourcePosition(Coordinates(max_x, max_y))
        elif direction == Direction.RIGHT:
            if self.spin == Spin.CLOCKWISE:
                return SourcePosition(Coordinates(max_x, max_y))
            else:
                return SourcePosition(Coordinates(max_x, 0))
        elif direction == Direction.DOWN:
            if self.spin == Spin.CLOCKWISE:
                return SourcePosition(Coordinates(max_x, 0))
            else:
                return SourcePosition(Coordinates(0, 0))
