import copy
from typing import List, Iterable

from swarm_bots.utils.coordinates import Coordinates
from swarm_bots.utils.direction import Direction


class LineToMiddle:
    # example for left edge with line like this:
    # 0 0 0 1 0 1 0
    # block_positions_example = [3,5]

    @staticmethod
    def get_block_positions_from_block_line(block_line: Iterable[bool]) -> List[int]:
        block_positions: List[int] = list()
        position = 0
        for block in block_line:
            if block:
                block_positions.append(position)
            position += 1
        # we reverse positions 5,3,1 -> 1,3,5 cause we add further blocks first
        return block_positions[::-1]

    def __init__(self, start_coordinates: Coordinates, direction: Direction, block_line: Iterable[bool]):
        self.block_line = copy.deepcopy(block_line)
        self.block_positions = LineToMiddle.get_block_positions_from_block_line(block_line)
        self.direction = direction
        self.start_coordinates = start_coordinates.copy()
        self.blocks_placed = 0
        self.blocks_to_place = len(self.block_positions)
        # last position where block could be placed or not
        if not self.is_finished():
            self.last_position = self.start_coordinates.create_moved_coordinate(
                self.direction,
                self.block_positions[0]
            )
        else:
            self.last_position = self.start_coordinates

    def get_to_block_direction(self) -> Direction:
        return self.direction

    def get_from_block_direction(self) -> Direction:
        return self.direction.get_opposite()

    def get_next_block_position(self) -> Coordinates:
        return self.start_coordinates.create_moved_coordinate(self.direction, self.block_positions[0])

    def get_last_position(self) -> Coordinates:
        return self.last_position

    def place_block(self) -> Coordinates:
        if self.is_finished():
            raise ValueError("cannot place block when line finished")
        self.blocks_placed += 1
        self.last_position = self.start_coordinates.create_moved_coordinate(
            self.get_to_block_direction(),
            self.block_positions.pop(0)
        )
        return self.last_position

    def is_finished(self) -> bool:
        return self.blocks_placed == self.blocks_to_place

    def __copy__(self):
        return LineToMiddle(start_coordinates=self.start_coordinates.copy(), direction=self.direction,
                            block_line=self.block_line)

    def copy(self):
        return self.__copy__()

    def __hash__(self):
        return hash((self.direction, self.start_coordinates))
