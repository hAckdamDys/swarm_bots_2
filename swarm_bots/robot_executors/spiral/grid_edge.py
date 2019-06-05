from typing import List

from swarm_bots.robot_executors.spiral.line_to_middle import LineToMiddle
from swarm_bots.robot_executors.spiral.source_position import SourcePosition
from swarm_bots.utils.coordinates import Coordinates


class GridEdge:
    def __init__(self, robot_coordinates: Coordinates, source_positions: List[SourcePosition]):
        self.robot_coordinates = robot_coordinates
        self.source_positions = source_positions
        # TODO: validate if finished?
        self.finished = False

    def get_closest_source(self) -> SourcePosition:
        raise NotImplementedError()

    # get line that robot with given offset should start on this edge
    def get_line(self, offset: int) -> LineToMiddle:
        raise NotImplementedError()

    def get_next_line(self) -> LineToMiddle:

        raise NotImplementedError()

    def is_finished(self) -> bool:
        return self.finished

    # TODO: decide if this method is needed or can be done other way to decide if edge is finished
    def set_line_finished(self, line: LineToMiddle):
        raise NotImplementedError()