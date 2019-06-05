from typing import List

from swarm_bots.goal.goal_building import GoalBuilding
from swarm_bots.grid.base_grid import BaseGrid
from swarm_bots.grid.shared_grid_access import SharedGridAccess
from swarm_bots.robot_executors.robot_executor import RobotExecutor
from swarm_bots.tiles.robot import Robot
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


class SourcePosition:
    def __init__(self, coordinates: Coordinates):
        self.coordinates = coordinates


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


class LineScannerExecutor:
    def __init__(self,
                 robot: Robot,
                 robot_coordinates: Coordinates,
                 private_grid: BaseGrid,
                 shared_grid_access: SharedGridAccess):
        self.shared_grid_access = shared_grid_access
        self.private_grid = private_grid
        self.robot_coordinates = robot_coordinates
        self.robot = robot
        # TODO: implement line scanner logic

    # scan line while changing line and all inner variables
    def scan_line(self, line: LineToMiddle):
        raise NotImplementedError()


class HighwayExecutor:
    def __init__(self,
                 robot: Robot,
                 robot_coordinates: Coordinates,
                 private_grid: BaseGrid,
                 shared_grid_access: SharedGridAccess):
        self.shared_grid_access = shared_grid_access
        self.private_grid = private_grid
        self.robot_coordinates = robot_coordinates
        self.robot = robot
        # TODO: implement highway around grid and logic how to get into places

    # makes robot go to line start using highway
    def go_to_line_start(self, line: LineToMiddle):
        raise NotImplementedError()

    def go_get_source(self, source: SourcePosition):
        raise NotImplementedError()


class SpiralRobotExecutor(RobotExecutor):
    # TODO: add timeout to init maybe
    loop_timeout = 1000

    def __init__(self, robot: Robot, shared_grid_access: SharedGridAccess, goal_building: GoalBuilding,
                 start_offset: int = 0):
        super().__init__(robot, shared_grid_access, goal_building)
        self.start_offset = start_offset
        self.robot_coordinates = self.private_grid.get_coord_from_tile(robot)
        self.highway_executor = HighwayExecutor(
            robot=self.robot,
            robot_coordinates=self.robot_coordinates,
            private_grid=self.private_grid,
            shared_grid_access=self.shared_grid_access
        )
        self.edges: List[GridEdge] = self._cut_goal_to_edges()
        self.edge = self.edges[0]
        self.line_scanner_executor = LineScannerExecutor(
            robot=self.robot,
            robot_coordinates=self.robot_coordinates,
            private_grid=self.private_grid,
            shared_grid_access=self.shared_grid_access
        )

    def _set_finished_edge(self, edge: GridEdge):
        raise NotImplementedError()

    def _all_edges_finished(self) -> bool:
        raise NotImplementedError()

    def _cut_goal_to_edges(self) -> List[GridEdge]:
        raise NotImplementedError()

    def _setup_into_next_edge(self):
        raise NotImplementedError()

    def _go_get_source(self):
        source_position = self.edge.get_closest_source()
        self.highway_executor.go_get_source(source_position)

    def start_process(self):
        offset = self.start_offset
        self._go_get_source()
        line = self.edge.get_line(offset)
        for i in range(SpiralRobotExecutor.loop_timeout):
            offset = line.get_offset()
            self.highway_executor.go_to_line_start(line)
            self.line_scanner_executor.scan_line(line)
            # TODO: check if needed {
            if line.is_finished():
                self.edge.set_line_finished(line)
            # }
            if not self.edge.is_finished():
                if self.robot.has_block():
                    line = self.edge.get_next_line()
                    continue
                self._setup_into_next_edge()
                self._go_get_source()
                line = self.edge.get_line(offset)
                continue
            self._set_finished_edge(self.edge)
            if self._all_edges_finished():
                # TODO: do end successful action maybe validate private grid and goal
                return
            self._setup_into_next_edge()
            if not self.robot.has_block():
                self._go_get_source()
            line = self.edge.get_line(offset)
        # TODO: do end not successful action
        return
