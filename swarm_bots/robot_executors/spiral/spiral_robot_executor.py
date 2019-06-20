from typing import List

from swarm_bots.goal.goal_building import GoalBuilding
from swarm_bots.grid.shared_grid_access import SharedGridAccess
from swarm_bots.robot_executors.robot_executor import RobotExecutor
from swarm_bots.robot_executors.spiral.goal_to_edges_splitters.goal_to_edges_splitter import GoalToEdgesSplitter
from swarm_bots.robot_executors.spiral.grid_edge import GridEdge
from swarm_bots.robot_executors.spiral.highway_executor import HighwayExecutor
from swarm_bots.robot_executors.spiral.line_scanners.line_scanner_executor import LineScannerExecutor
from swarm_bots.tiles.robot import Robot
from swarm_bots.utils.spin import Spin


class SpiralRobotExecutor(RobotExecutor):
    # TODO: add timeout to init maybe
    loop_timeout = 1000

    def __init__(self,
                 robot: Robot,
                 shared_grid_access: SharedGridAccess,
                 goal_building: GoalBuilding,
                 goal_to_edges_splitter: GoalToEdgesSplitter,
                 spin: Spin,
                 start_offset: int = 0):
        super().__init__(robot, shared_grid_access, goal_building)
        self.start_offset = start_offset
        self.robot_coordinates = self.private_grid.get_coord_from_tile(robot)
        self.highway_executor = HighwayExecutor(
            shared_actions_executor=self.shared_actions_executor,
            spin=spin
        )
        self.edges: List[GridEdge] = goal_to_edges_splitter.get_edges()
        self.edge = self.edges[0]
        self.line_scanner_executor = LineScannerExecutor(
            shared_actions_executor=self.shared_actions_executor
        )

    def _set_finished_edge(self, edge: GridEdge):
        raise NotImplementedError()

    def _all_edges_finished(self) -> bool:
        raise NotImplementedError()

    def _setup_into_next_edge(self):
        raise NotImplementedError()

    def _go_get_source(self):
        source_position = self.edge.get_closest_source()
        self.highway_executor.go_get_source(source_position)

    def start_process(self):
        # TODO: make sure logic is fine and test scenarios
        offset = self.start_offset
        self._go_get_source()
        line = self.edge.get_line(offset)
        for i in range(SpiralRobotExecutor.loop_timeout):
            offset = line.get_offset()
            self.highway_executor.go_to_line_start(line)
            self.line_scanner_executor.scan_line(line)
            if line.is_finished():
                self.edge.set_line_finished(line)
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
