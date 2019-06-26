from typing import List

from swarm_bots.goal.goal_building import GoalBuilding
from swarm_bots.grid.shared_grid_access import SharedGridAccess
from swarm_bots.robot_executors.robot_executor import RobotExecutor
from swarm_bots.robot_executors.spiral.goal_to_edges_splitters.goal_to_edges_splitter import GoalToEdgesSplitter
from swarm_bots.robot_executors.spiral.grid_edge import GridEdge
from swarm_bots.robot_executors.spiral.highway_executor import HighwayExecutor
from swarm_bots.robot_executors.spiral.line_scanners.line_scanner_executor import LineScannerExecutor
from swarm_bots.tiles.robot import Robot
from swarm_bots.utils.coordinates import Coordinates
from swarm_bots.utils.spin import Spin


class SpiralRobotExecutor(RobotExecutor):
    loop_timeout = 100000

    def __init__(self,
                 robot: Robot,
                 shared_grid_access: SharedGridAccess,
                 goal_building: GoalBuilding,
                 goal_to_edges_splitter: GoalToEdgesSplitter,
                 spin: Spin,
                 sleep_tick_seconds: float = None,
                 robot_coordinates: Coordinates = None,
                 start_offset: int = 0,
                 start_edge_index: int = None):
        super().__init__(robot, shared_grid_access, goal_building, robot_coordinates=robot_coordinates,
                         sleep_tick_seconds=sleep_tick_seconds)
        self.private_grid.add_tile_to_grid(self.robot, self.robot_coordinates.copy())
        self.start_offset = start_offset
        self.robot_coordinates = self.private_grid.get_coord_from_tile(robot)
        self.spin = spin
        self.highway_executor = HighwayExecutor(
            shared_actions_executor=self.shared_actions_executor,
            spin=spin
        )
        self.line_scanner_executor = LineScannerExecutor(
            shared_actions_executor=self.shared_actions_executor
        )
        self.edges: List[GridEdge] = goal_to_edges_splitter.get_edges()
        if start_edge_index is None:
            edge_side = robot_coordinates.get_edge_side(width=goal_building.width, height=goal_building.height)
            next_side = spin.get_edge_move_direction(edge_side)
            for i in range(0, 4):
                self.edge_index = i
                self.edge = self.edges[self.edge_index]
                if next_side == self.edge.edge_side:
                    print(f"robot: {robot} got side {next_side}")
                    break
        else:
            self.edge_index = start_edge_index
            self.edge = self.edges[self.edge_index % 4]

    def _all_edges_finished(self) -> bool:
        all_finished = True
        for i in range(4):
            if not self.edges[i].is_finished():
                all_finished = False
        return all_finished

    def _go_get_source(self):
        source_position = self.edge.get_closest_source()
        self.highway_executor.go_get_source(source_position)

    def _update_to_next_edge(self):
        for i in range(4):
            self.edge_index = (self.edge_index + 1) % 4
            edge = self.edges[self.edge_index]
            if not edge.is_finished():
                self.edge = edge
                return
        raise ValueError("all edges finished cannot update to next")

    def _go_around(self):
        source_position = self.edge.get_closest_source()
        pre_source_position = self.spin.get_pre_corner_coordinates(source_position.coordinates)
        print("ROBOT: " + str(self.robot) + "start go around to " + str(pre_source_position))
        self.highway_executor.go_to_goal(pre_source_position)

    def start_process(self):
        # TODO: make sure logic is fine and test scenarios
        offset = self.start_offset
        self._go_get_source()
        line = self.edge.get_line(offset)
        last_line = line
        line_repeated = 0
        for i in range(SpiralRobotExecutor.loop_timeout):
            if last_line == line:
                line_repeated += 1
            else:
                line_repeated = 0
            if line_repeated > 1:
                self._go_around()
                line_repeated = 0
            last_line = line
            offset = self.edge.get_next_offset()
            self.highway_executor.go_to_line_start(line)
            self.line_scanner_executor.scan_line(line)
            if line.is_finished():
                self.edge.set_line_finished(line)
            if not self.edge.is_finished():
                if self.robot.has_block():
                    line = self.edge.get_next_line()
                    if line is not None:
                        continue
                self._update_to_next_edge()
                self._go_get_source()
                line = self.edge.get_line(offset)
                continue
            if self._all_edges_finished():
                print("ROBOT: "+str(self.robot)+"finished and thinks all good")
                self.shared_actions_executor.finish_robot()
                return
            self._update_to_next_edge()
            if not self.robot.has_block():
                self._go_get_source()
            line = self.edge.get_line(offset)
        print("ROBOT: "+str(self.robot)+", failed with timeout: "+str(self.loop_timeout))
        self.shared_actions_executor.finish_robot()
        return
