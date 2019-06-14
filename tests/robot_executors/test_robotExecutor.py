from multiprocessing import Manager
from time import sleep
from unittest import TestCase

from swarm_bots.goal.goal_building import GoalBuilding
from swarm_bots.grid.base_grid import BaseGrid
from swarm_bots.grid.shared_grid_access import SharedGridAccess
from swarm_bots.robot_executors.hit_information import HitType
from swarm_bots.robot_executors.robot_executor import RobotExecutor
from swarm_bots.tiles.robot import Robot
from swarm_bots.utils.coordinates import Coordinates
from swarm_bots.utils.direction import Direction


class RobotRotateMoveMockExecutor(RobotExecutor):
    def __init__(self, rotate: Direction, move: Direction, robot: Robot,
                 shared_grid_access: SharedGridAccess, goal_building: GoalBuilding):
        super().__init__(robot, shared_grid_access, goal_building)
        self.move = move
        self.rotate = rotate

    def start_process(self):
        if self.rotate is not None:
            h_info = self.shared_actions_executor.try_rotate_robot(self.rotate)
            assert h_info.hit_type == HitType.ROTATED
        if self.move is not None:
            h_info = self.shared_actions_executor.try_move_robot(self.move)
            assert h_info.hit_type == HitType.NO_HIT


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
        self.shared_actions_executor.try_rotate_robot(self.where_rotate)
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
        self.shared_actions_executor.try_move_robot(self.move_direction)
        with self.shared_grid_access.grid_lock_sync as grid:
            
            if self.how_long_sleep == RobotExecutorMockMove.robot1_sleep:
                robot1 = grid.get_tile_from_grid(self.r1_c)
                assert robot1 == self.robot
            if self.how_long_sleep == RobotExecutorMockMove.robot2_sleep:
                robot1 = grid.get_tile_from_grid(self.r1_c)
                assert robot1 is not None
                robot1 = grid.get_tile_from_grid(RobotExecutorMockMove.robot1_coordinates)
                assert robot1 is None

                robot2 = grid.get_tile_from_grid(self.r2_c)
                assert robot2 == self.robot
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
            assert robot1 == robot1_new
            robot2_new = grid.get_tile_from_grid(robot2_executor.r2_c)
            assert robot2 == robot2_new
            print(grid)

    def test_move_far_scenario(self):
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
        # rotate, move, end coordinates:
        # if move or rotate is None then don't do it
        robot_states = [(Direction.UP, None, Coordinates(0, 0)),
                        (None, Direction.UP, Coordinates(0, 1)),
                        (Direction.DOWN, Direction.UP, Coordinates(0, 2)),
                        (Direction.RIGHT, Direction.RIGHT, Coordinates(1, 2)),
                        (None, Direction.RIGHT, Coordinates(2, 2)),
                        (None, Direction.LEFT, Coordinates(1, 2))
                        ]
        rotate_directions = [state[0] for state in robot_states]
        moving_directions = [state[1] for state in robot_states]
        robot_coordinates = [state[2] for state in robot_states]

        robot = Robot(rotate_directions[0])
        base_grid.add_tile_to_grid(robot, robot_coordinates[0])

        shared_grid_access = SharedGridAccess(base_grid, Manager())

        for i in range(1, len(robot_states)):
            rotate = rotate_directions[i]
            move = moving_directions[i]

            robot_executor = RobotRotateMoveMockExecutor(rotate, move, robot, shared_grid_access, goal_building)
            robot_executor.start_working()
            robot_executor.wait_for_finish()
            if rotate is not None:
                robot.rotate_to_direction(rotate)
            grid_copy = shared_grid_access.get_private_copy()
            # robot from grid has wrong direction
            robot_grid = grid_copy.get_tile_from_grid(robot_coordinates[i])
            assert robot_grid == robot
