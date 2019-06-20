from enum import Enum
from typing import List

from swarm_bots.utils.direction import Direction


class Spin(Enum):
    CLOCKWISE = 0
    ANTI_CLOCKWISE = 1

    def get_opposite(self) -> 'Spin':
        if self == Spin.CLOCKWISE:
            return Spin.ANTI_CLOCKWISE
        return Spin.CLOCKWISE

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
