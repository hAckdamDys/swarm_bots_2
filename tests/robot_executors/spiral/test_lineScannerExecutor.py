import os
from multiprocessing import Manager
from unittest import TestCase

from swarm_bots.goal.goal_building import GoalBuilding
from swarm_bots.goal.goal_building_2d import GoalBuilding2D
from swarm_bots.grid.base_grid import BaseGrid
from swarm_bots.grid.shared_grid_access import SharedGridAccess
from swarm_bots.robot_executors.hit_information import HitType
from swarm_bots.robot_executors.robot_executor import RobotExecutor
from swarm_bots.robot_executors.robot_shared_actions_executor import RobotSharedActionsExecutor
from swarm_bots.robot_executors.spiral.line_scanner_executor import LineScannerExecutor
from swarm_bots.robot_executors.spiral.line_to_middle import LineToMiddle
from swarm_bots.tiles.robot import Robot
from swarm_bots.tiles.tile import Tile, TileType
from swarm_bots.utils.coordinates import Coordinates
from swarm_bots.utils.direction import Direction


class LineScannerWrapperExecutor(RobotExecutor):
    def __init__(self, line: LineToMiddle, robot: Robot, shared_grid_access: SharedGridAccess,
                 goal_building: GoalBuilding):
        super().__init__(robot, shared_grid_access, goal_building)
        self.line = line.copy()
        self.line_scanner = LineScannerExecutor(self.shared_actions_executor)

    def start_process(self):
        start_coordinates = self.robot_coordinates.copy()
        to_start_direction = start_coordinates.get_to_other_direction(self.line.start_coordinates)
        while self.robot.has_block():
            self.shared_actions_executor.try_rotate_robot(to_start_direction)
            while self.robot_coordinates != self.line.start_coordinates:
                hit_information = self.shared_actions_executor.try_move_robot(to_start_direction)
                if hit_information.hit_type == HitType.ROBOT:
                    self.shared_actions_executor.wait_action()
            self.line_scanner.scan_line(self.line)
            self.shared_actions_executor.try_rotate_robot(to_start_direction.get_opposite())
            while self.robot_coordinates != start_coordinates:
                hit_information = self.shared_actions_executor.try_move_robot(to_start_direction.get_opposite())
                if hit_information.hit_type == HitType.ROBOT:
                    self.shared_actions_executor.wait_action()
        print(f"robot: {self.robot} put {self.shared_actions_executor.put_blocks} blocks")


# executor that assumes sth like this in left column of grid
# source for robotX
# robotX
# ...
# line_to_middle
# ...
# robotY
# source for robotY

class LineScannerWithSourceWrapperExecutor(RobotExecutor):
    def __init__(self, line: LineToMiddle, robot: Robot, shared_grid_access: SharedGridAccess,
                 goal_building: GoalBuilding):
        super().__init__(robot, shared_grid_access, goal_building, 0.0001)
        self.line = line.copy()
        self.line_scanner = LineScannerExecutor(self.shared_actions_executor)

    def start_process(self):
        start_coordinates = self.robot_coordinates.copy()
        to_line_start_direction = start_coordinates.get_to_other_direction(self.line.start_coordinates)
        to_source_direction = to_line_start_direction.get_opposite()
        while not self.line.is_finished():
            self.shared_actions_executor.wait_action()
            self.shared_actions_executor.wait_action()
            self.shared_actions_executor.wait_action()
            if not self.robot.rotation == to_source_direction:
                self.shared_actions_executor.try_rotate_robot(to_source_direction)
            if not self.robot.has_block():
                self.shared_actions_executor.try_get_block(to_source_direction)
            if not self.robot.has_block():
                raise ValueError("robot could not take block")
            self.shared_actions_executor.try_rotate_robot(to_line_start_direction)
            while self.robot_coordinates != self.line.start_coordinates:
                hit_information = self.shared_actions_executor.try_move_robot(to_line_start_direction)
                if hit_information.hit_type == HitType.ROBOT:
                    self.shared_actions_executor.wait_action()
            self.line_scanner.scan_line(self.line)
            self.shared_actions_executor.try_rotate_robot(to_line_start_direction.get_opposite())
            while self.robot_coordinates != start_coordinates:
                hit_information = self.shared_actions_executor.try_move_robot(to_source_direction)
                if hit_information.hit_type == HitType.ROBOT:
                    self.shared_actions_executor.wait_action()
        print(f"robot: {self.robot} put {self.shared_actions_executor.put_blocks} blocks")


class TestLineScannerExecutor(TestCase):
    def test_single_robot_finish_single_block_goal(self):
        goal_building = GoalBuilding2D("""
        0 0 0 0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0 0 0
        0 0 0 0 1 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0 0 0
        """)
        robot = Robot(Direction.UP)
        robot.take_block(Tile(TileType.BLOCK))
        line_start_coordinates = Coordinates(0, 3)
        base_grid = BaseGrid(goal_building.width, goal_building.height)
        base_grid.add_tile_to_grid(robot, line_start_coordinates)
        shared_grid_access = SharedGridAccess(base_grid, manager=Manager())
        shared_actions_executor = RobotSharedActionsExecutor(
            robot=robot,
            shared_grid_access=shared_grid_access,
            private_grid=shared_grid_access.get_private_copy(),
            robot_coordinates=line_start_coordinates.copy()
        )
        line_scanner_executor = LineScannerExecutor(shared_actions_executor=shared_actions_executor)
        line_to_middle = LineToMiddle(
            start_coordinates=line_start_coordinates.copy(),
            direction=Direction.RIGHT,
            block_line=map(bool, [0, 0, 0, 0, 1])
        )
        line_scanner_executor.scan_line(line=line_to_middle)
        grid = shared_grid_access.get_private_copy()
        assert line_to_middle.is_finished()
        assert goal_building.validate_grid(grid)
        assert grid.get_coord_from_tile(robot) == line_start_coordinates

    def test_single_robot_finish_single_line_goal(self):
        goal_building = GoalBuilding2D("""
        0 0 0 0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0 0 0
        0 1 1 0 1 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0 0 0
        """)
        robot = Robot(Direction.UP)
        robot.take_block(Tile(TileType.BLOCK))
        line_start_coordinates = Coordinates(0, 3)
        base_grid = BaseGrid(goal_building.width, goal_building.height)
        base_grid.add_tile_to_grid(robot, line_start_coordinates)
        base_grid.add_tile_to_grid(Tile(TileType.SOURCE),
                                   line_start_coordinates.create_neighbour_coordinate(Direction.UP))
        shared_grid_access = SharedGridAccess(base_grid, manager=Manager())
        shared_actions_executor = RobotSharedActionsExecutor(
            robot=robot,
            shared_grid_access=shared_grid_access,
            private_grid=shared_grid_access.get_private_copy(),
            robot_coordinates=line_start_coordinates.copy()
        )
        line_scanner_executor = LineScannerExecutor(shared_actions_executor=shared_actions_executor)
        line_to_middle = LineToMiddle(
            start_coordinates=line_start_coordinates.copy(),
            direction=Direction.RIGHT,
            block_line=map(bool, [0, 1, 1, 0, 1])
        )
        for i in range(3):
            line_scanner_executor.scan_line(line=line_to_middle)
            grid = shared_grid_access.get_private_copy()
            assert grid.get_coord_from_tile(robot) == line_start_coordinates
            # we rotate take block from source and do another block
            shared_actions_executor.try_rotate_robot(Direction.UP)
            shared_actions_executor.try_get_block(Direction.UP)
            grid = shared_grid_access.get_private_copy()
            assert grid.get_tile_from_grid(line_start_coordinates) == robot
        grid = shared_grid_access.get_private_copy()
        assert line_to_middle.is_finished()
        assert goal_building.validate_grid(grid)
        assert grid.get_coord_from_tile(robot) == line_start_coordinates

    def test_another_robot_update_private_grid(self):
        goal_building = GoalBuilding2D("""
        0 0 0 0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0 0 0
        0 0 1 0 1 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0 0 0
        """)
        robot_1 = Robot(Direction.DOWN)
        robot_1.take_block(Tile(TileType.BLOCK))
        robot_2 = Robot(Direction.UP)
        robot_2.take_block(Tile(TileType.BLOCK))
        line_start_coordinates = Coordinates(0, 3)
        robot_1_coordinates = Coordinates(0, 4)
        robot_2_coordinates = Coordinates(0, 2)
        base_grid = BaseGrid(goal_building.width, goal_building.height)
        base_grid.add_tile_to_grid(robot_1, robot_1_coordinates)
        base_grid.add_tile_to_grid(robot_2, robot_2_coordinates)
        shared_grid_access = SharedGridAccess(base_grid, manager=Manager())
        line_to_middle = LineToMiddle(
            start_coordinates=line_start_coordinates,
            direction=Direction.RIGHT,
            block_line=list(map(bool, [0, 0, 1, 0, 1]))
        )
        robot_1_executor = LineScannerWrapperExecutor(
            line=line_to_middle,
            robot=robot_1,
            shared_grid_access=shared_grid_access,
            goal_building=goal_building
        )
        robot_2_executor = LineScannerWrapperExecutor(
            line=line_to_middle,
            robot=robot_2,
            shared_grid_access=shared_grid_access,
            goal_building=goal_building
        )
        robot_1_executor.start_working()
        robot_2_executor.start_working()

        robot_1_executor.wait_for_finish()
        robot_2_executor.wait_for_finish()

        grid = shared_grid_access.get_private_copy()
        assert goal_building.validate_grid(grid)

    def test_build_line_with_robots_crash(self):

        text_grid = """
        0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 1 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 0 0 1 1 1 0 1 0 0 0 0 0 0 1 1 1 0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 1
        0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
        """
        goal_building = GoalBuilding2D(text_grid=text_grid)
        robot_1 = Robot(Direction.DOWN)
        robot_1_source = Tile(TileType.SOURCE)
        robot_2 = Robot(Direction.UP)
        robot_2_source = Tile(TileType.SOURCE)
        line_start_coordinates = Coordinates(0, 9)
        base_grid = BaseGrid(goal_building.width, goal_building.height)
        robot_1_coordinates = Coordinates(0, 16)
        base_grid.add_tile_to_grid(robot_1, robot_1_coordinates)
        base_grid.add_tile_to_grid(robot_1_source, robot_1_coordinates.create_neighbour_coordinate(Direction.UP))
        robot_2_coordinates = Coordinates(0, 1)
        base_grid.add_tile_to_grid(robot_2, robot_2_coordinates)
        base_grid.add_tile_to_grid(robot_2_source, robot_2_coordinates.create_neighbour_coordinate(Direction.DOWN))

        shared_grid_access = SharedGridAccess(base_grid, manager=Manager())
        line_to_middle = LineToMiddle(
            start_coordinates=line_start_coordinates,
            direction=Direction.RIGHT,
            block_line=list(map(bool, map(int, text_grid.split("\n")[9].split())))
        )
        robot_1_executor = LineScannerWithSourceWrapperExecutor(
            line=line_to_middle,
            robot=robot_1,
            shared_grid_access=shared_grid_access,
            goal_building=goal_building
        )
        robot_2_executor = LineScannerWithSourceWrapperExecutor(
            line=line_to_middle,
            robot=robot_2,
            shared_grid_access=shared_grid_access,
            goal_building=goal_building
        )
        robot_1_executor.start_working()
        robot_2_executor.start_working()

        robot_1_executor.wait_for_finish()
        robot_2_executor.wait_for_finish()

        grid = shared_grid_access.get_private_copy()
        assert goal_building.validate_grid(grid)
