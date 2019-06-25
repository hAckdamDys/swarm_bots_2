from typing import List, Union

from swarm_bots.robot_executors.spiral.line_to_middle import LineToMiddle
from swarm_bots.robot_executors.spiral.source_positions.position import SourcePosition
from swarm_bots.robot_executors.spiral.source_positions.spun_positions import SpunPositions
from swarm_bots.utils.direction import Direction
from sortedcontainers import SortedDict

from swarm_bots.utils.spin import Spin


class GridEdge:
    def __init__(self,
                 spun_positions: SpunPositions,
                 lines: List[LineToMiddle],
                 edge_side: Direction,
                 spin: Spin
                 ):
        self.spin = spin
        self.closest_source = spun_positions.get_position(edge_side)
        self.should_reverse_indexes = spin.should_edge_reverse_indexes(edge_side=edge_side)
        self.length = len(lines)
        self.lines = lines
        self.how_many_finished = 0
        self.indexes_from_lines = dict()
        self.not_finished_line_indexes: SortedDict[LineToMiddle] = SortedDict()
        for i in range(self.length):
            self.indexes_from_lines[self.lines[i]] = i
            if self.lines[i].is_finished():
                self.how_many_finished += 1
            else:
                self.not_finished_line_indexes[i] = self.lines[i]
        self.last_offset = 0

    def get_closest_source(self) -> SourcePosition:
        return self.closest_source

    def get_line(self, offset: int) -> LineToMiddle:
        offset = offset % (self.length - self.how_many_finished)
        self.last_offset = offset
        if self.should_reverse_indexes:
            offset = self.length - self.how_many_finished - 1 - offset
        return self.not_finished_line_indexes.peekitem(offset)[1]

    def get_next_line(self) -> Union[LineToMiddle, None]:
        if self.last_offset >= (self.length - self.how_many_finished):
            return None
        self.last_offset += 1
        offset = self.length - self.how_many_finished - 1 - self.last_offset
        return self.get_line(offset)

    def get_next_offset(self) -> int:
        return self.last_offset + 3

    def is_finished(self) -> bool:
        return self.how_many_finished == self.length

    def set_line_finished(self, line: LineToMiddle):
        line_index = self.indexes_from_lines[line]
        self.not_finished_line_indexes.pop(line_index)
        self.how_many_finished += 1

    def get_number_of_finished_lines(self):
        return self.how_many_finished
