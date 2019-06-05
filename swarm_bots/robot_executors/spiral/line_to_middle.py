from typing import List

from swarm_bots.utils.coordinates import Coordinates
from swarm_bots.utils.direction import Direction


class LineToMiddle:
    def __init__(self, start_coordinates: Coordinates, direction: Direction, length: int, block_positions: List[int]):
        self.length = length
        self.block_positions = block_positions
        self.direction = direction
        self.start_coordinates = start_coordinates
        self.block_placed = 0
        # TODO: validate if finished?
        self.finished = False

    # TODO: implement line structure and methods for scanner executor
    def get_offset(self) -> int:
        raise NotImplementedError()

    def is_finished(self) -> bool:
        return self.finished
