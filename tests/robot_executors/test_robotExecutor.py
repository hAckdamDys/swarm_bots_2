from multiprocessing import Manager
from time import sleep
from typing import Union
from unittest import TestCase

from swarm_bots.goal.goal_building import GoalBuilding
from swarm_bots.grid.base_grid import BaseGrid
from swarm_bots.grid.shared_grid_access import SharedGridAccess
from swarm_bots.robot_executors.robot_executor import RobotExecutor
from swarm_bots.tiles.robot import Robot
from swarm_bots.tiles.tile import Tile
from swarm_bots.utils.coordinates import Coordinates
from swarm_bots.utils.direction import Direction


class RobotExecutorMockRotate(RobotExecutor):
    def __init__(self, where_rotate: Direction, how_long_sleep: int, robot: Robot, shared_grid_access: SharedGridAccess, goal_building: GoalBuilding):
        super().__init__(robot, shared_grid_access, goal_building)
        self.how_long_sleep = how_long_sleep
        self.where_rotate = where_rotate

    def start_process(self):
        sleep(self.how_long_sleep)
        print("before", self.how_long_sleep, self.robot)
        self.try_rotate_robot(self.where_rotate)
        robot_from_shared = self.shared_grid_access.grid.get_tile_from_grid(self.private_grid.get_coord_from_tile(self.robot))
        print("after", self.how_long_sleep, self.robot, "f", robot_from_shared, "\n")


class TestRobotExecutor(TestCase):
    def test_small_rotate_scenario(self):
        base_grid = BaseGrid(5, 5)
        goal_building = GoalBuilding(
            """
            0 0 0 0 0
            0 0 1 0 0
            0 1 2 1 0
            0 0 1 2 0
            0 0 0 0 0
            """
        )

        robot1 = Robot(Direction.DOWN)
        robot1_coordinates = Coordinates(2, 3)
        robot1_future_rotate = Direction.RIGHT
        robot1_sleep = 1
        robot2 = Robot(Direction.RIGHT)
        robot2_coordinates = Coordinates(1, 3)
        robot2_future_rotate = Direction.DOWN
        robot2_sleep = 3

        base_grid.add_tile_to_grid(robot1, robot1_coordinates)
        base_grid.add_tile_to_grid(robot2, robot2_coordinates)
        shared_grid_access = SharedGridAccess(base_grid, Manager())

        robot1_executor = RobotExecutorMockRotate(
            where_rotate=robot1_future_rotate,
            how_long_sleep=robot1_sleep,
            robot=robot1,
            shared_grid_access=shared_grid_access,
            goal_building=goal_building
        )

        robot2_executor = RobotExecutorMockRotate(
            where_rotate=robot2_future_rotate,
            how_long_sleep=robot2_sleep,
            robot=robot2,
            shared_grid_access=shared_grid_access,
            goal_building=goal_building
        )

        robot1_executor.start_working()
        robot2_executor.start_working()

        robot1_executor.wait_for_finish()
        robot1: Union[Robot, Tile] = shared_grid_access.grid.get_tile_from_grid(robot1_coordinates)
        print("test", robot1)
        robot2_executor.wait_for_finish()
        assert robot1.rotation == robot1_future_rotate
