from multiprocessing import Manager
from time import sleep
from unittest import TestCase

from swarm_bots.goal.goal_building import GoalBuilding
from swarm_bots.grid.base_grid import BaseGrid
from swarm_bots.grid.shared_grid_access import SharedGridAccess
from swarm_bots.robot_executors.robot_executor import RobotExecutor
from swarm_bots.tiles.robot import Robot
from swarm_bots.utils.coordinates import Coordinates
from swarm_bots.utils.direction import Direction


class RobotExecutorMockRotate(RobotExecutor):
    robot1_coordinates = Coordinates(2, 3)
    robot1_future_rotate = Direction.LEFT
    robot1_sleep = 1
    robot2_coordinates = Coordinates(1, 3)
    robot2_future_rotate = Direction.DOWN
    robot2_sleep = 3

    def __init__(self, where_rotate: Direction, how_long_sleep: int,
                 robot: Robot, shared_grid_access: SharedGridAccess, goal_building: GoalBuilding):
        super().__init__(robot, shared_grid_access, goal_building)
        self.how_long_sleep = how_long_sleep
        self.where_rotate = where_rotate

    def start_process(self):
        sleep(self.how_long_sleep)
        self.try_rotate_robot(self.where_rotate)
        with self.shared_grid_access.grid_lock_sync as grid:
            if self.how_long_sleep == RobotExecutorMockRotate.robot1_sleep:
                robot1 = grid.get_tile_from_grid(RobotExecutorMockRotate.robot1_coordinates)
                assert robot1.rotation == RobotExecutorMockRotate.robot1_future_rotate
            if self.how_long_sleep == RobotExecutorMockRotate.robot2_sleep:
                robot1 = grid.get_tile_from_grid(RobotExecutorMockRotate.robot1_coordinates)
                assert robot1.rotation == RobotExecutorMockRotate.robot1_future_rotate
                robot2 = grid.get_tile_from_grid(RobotExecutorMockRotate.robot2_coordinates)
                assert robot2.rotation == RobotExecutorMockRotate.robot2_future_rotate


class RobotExecutorMockMove(RobotExecutor):
    robot1_coordinates = Coordinates(4, 4)
    robot1_move_direction = Direction.LEFT
    robot1_sleep = 1
    robot2_coordinates = Coordinates(1, 3)
    robot2_move_direction = Direction.DOWN
    robot2_sleep = 3

    def __init__(self, move_direction: Direction, how_long_sleep: int,
                 robot: Robot, shared_grid_access: SharedGridAccess, goal_building: GoalBuilding):
        super().__init__(robot, shared_grid_access, goal_building)
        self.how_long_sleep = how_long_sleep
        self.move_direction = move_direction
        self.r1_c = RobotExecutorMockMove.robot1_coordinates.create_neighbour_coordinate(
            RobotExecutorMockMove.robot1_move_direction
        )
        self.r2_c = RobotExecutorMockMove.robot2_coordinates.create_neighbour_coordinate(
            RobotExecutorMockMove.robot2_move_direction
        )

    def start_process(self):
        sleep(self.how_long_sleep)
        self.try_move_robot(self.move_direction)
        with self.shared_grid_access.grid_lock_sync as grid:
            
            if self.how_long_sleep == RobotExecutorMockMove.robot1_sleep:
                robot1 = grid.get_tile_from_grid(self.r1_c)
                assert robot1.id == self.robot.id
            if self.how_long_sleep == RobotExecutorMockMove.robot2_sleep:
                robot1 = grid.get_tile_from_grid(self.r1_c)
                assert robot1 is not None
                robot1 = grid.get_tile_from_grid(RobotExecutorMockMove.robot1_coordinates)
                assert robot1 is None

                robot2 = grid.get_tile_from_grid(self.r2_c)
                assert robot2.id == self.robot.id
                robot2 = grid.get_tile_from_grid(RobotExecutorMockMove.robot2_coordinates)
                assert robot2 is None


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
        robot2 = Robot(Direction.RIGHT)

        base_grid.add_tile_to_grid(robot1, RobotExecutorMockRotate.robot1_coordinates)
        base_grid.add_tile_to_grid(robot2, RobotExecutorMockRotate.robot2_coordinates)

        shared_grid_access = SharedGridAccess(base_grid, Manager())

        robot1_executor = RobotExecutorMockRotate(
            where_rotate=RobotExecutorMockRotate.robot1_future_rotate,
            how_long_sleep=RobotExecutorMockRotate.robot1_sleep,
            robot=robot1,
            shared_grid_access=shared_grid_access,
            goal_building=goal_building
        )

        robot2_executor = RobotExecutorMockRotate(
            where_rotate=RobotExecutorMockRotate.robot2_future_rotate,
            how_long_sleep=RobotExecutorMockRotate.robot2_sleep,
            robot=robot2,
            shared_grid_access=shared_grid_access,
            goal_building=goal_building
        )

        robot1_executor.start_working()
        robot2_executor.start_working()

        robot1_executor.wait_for_finish()
        robot2_executor.wait_for_finish()

        with shared_grid_access.grid_lock_sync as grid:
            robot1 = grid.get_tile_from_grid(RobotExecutorMockRotate.robot1_coordinates)
            assert robot1.rotation == RobotExecutorMockRotate.robot1_future_rotate
            robot2 = grid.get_tile_from_grid(RobotExecutorMockRotate.robot2_coordinates)
            assert robot2.rotation == RobotExecutorMockRotate.robot2_future_rotate
            print(grid)

    def test_small_move_scenario(self):
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

        robot1 = Robot(RobotExecutorMockMove.robot1_move_direction)
        robot2 = Robot(RobotExecutorMockMove.robot2_move_direction)

        base_grid.add_tile_to_grid(robot1, RobotExecutorMockMove.robot1_coordinates)
        base_grid.add_tile_to_grid(robot2, RobotExecutorMockMove.robot2_coordinates)

        shared_grid_access = SharedGridAccess(base_grid, Manager())

        robot1_executor = RobotExecutorMockMove(
            move_direction=RobotExecutorMockMove.robot1_move_direction,
            how_long_sleep=RobotExecutorMockMove.robot1_sleep,
            robot=robot1,
            shared_grid_access=shared_grid_access,
            goal_building=goal_building
        )

        robot2_executor = RobotExecutorMockMove(
            move_direction=RobotExecutorMockMove.robot2_move_direction,
            how_long_sleep=RobotExecutorMockMove.robot2_sleep,
            robot=robot2,
            shared_grid_access=shared_grid_access,
            goal_building=goal_building
        )

        robot1_executor.start_working()
        robot2_executor.start_working()

        robot1_executor.wait_for_finish()
        robot2_executor.wait_for_finish()

        with shared_grid_access.grid_lock_sync as grid:
            robot1_new = grid.get_tile_from_grid(robot2_executor.r1_c)
            assert robot1.id == robot1_new.id
            robot2_new = grid.get_tile_from_grid(robot2_executor.r2_c)
            assert robot2.id == robot2_new.id
            print(grid)
