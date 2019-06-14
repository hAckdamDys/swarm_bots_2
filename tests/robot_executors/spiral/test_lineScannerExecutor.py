from multiprocessing import Manager
from unittest import TestCase

from swarm_bots.goal.goal_building_2d import GoalBuilding2D
from swarm_bots.grid.base_grid import BaseGrid
from swarm_bots.grid.shared_grid_access import SharedGridAccess
from swarm_bots.robot_executors.robot_shared_actions_executor import RobotSharedActionsExecutor
from swarm_bots.robot_executors.spiral.line_scanner_executor import LineScannerExecutor
from swarm_bots.robot_executors.spiral.line_to_middle import LineToMiddle
from swarm_bots.tiles.robot import Robot
from swarm_bots.tiles.tile import Tile, TileType
from swarm_bots.utils.coordinates import Coordinates
from swarm_bots.utils.direction import Direction


class TestLineScannerExecutor(TestCase):
    def test_single_robot_finish_single_line_goal(self):
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
            start_coordinates=line_start_coordinates,
            direction=Direction.RIGHT,
            block_line=map(bool, [0, 0, 0, 0, 1])
        )
        line_scanner_executor.scan_line(line=line_to_middle)
        grid = shared_grid_access.get_private_copy()
        assert goal_building.validate_grid(grid)
        assert grid.get_coord_from_tile(robot) == line_start_coordinates
