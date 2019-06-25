from multiprocessing import Manager
from unittest import TestCase

from swarm_bots.grid.base_grid import BaseGrid
from swarm_bots.grid.errors.out_of_bound_coordinates_error import OutOfBoundCoordinatesError
from swarm_bots.grid.shared_grid_access import SharedGridAccess
from swarm_bots.grid.errors.tile_taken_exception import TileTakenException
from swarm_bots.robot_executors.hit_information import HitType
from swarm_bots.tiles.robot import Robot
from swarm_bots.tiles.tile import Tile, TileType
from swarm_bots.tiles.errors.wrong_block_put_direction import WrongBlockPutDirection
from swarm_bots.utils.coordinates import Coordinates
from swarm_bots.utils.direction import Direction


class TestSharedGridAccess(TestCase):
    def test_shared_sync(self):
        base_grid = BaseGrid(5, 5)

        robot1 = Robot(Direction.RIGHT)
        robot1_coordinates = Coordinates(2, 2)

        robot2 = Robot(Direction.UP)
        robot2_coordinates = Coordinates(1, 3)

        base_grid.add_tile_to_grid(robot1, robot1_coordinates)
        base_grid.add_tile_to_grid(robot2, robot2_coordinates)
        shared_grid_access = SharedGridAccess(base_grid, Manager())

        shared_grid_access.try_rotate_robot(robot1, Direction.LEFT)
        robot1.rotate_to_direction(Direction.LEFT)

        shared_grid_access.try_move_robot(robot2, Direction.UP)
        robot2_coordinates = robot2_coordinates.create_neighbour_coordinate(Direction.UP)
        with shared_grid_access.grid_lock_sync as grid:
            assert grid.get_tile_from_grid(robot1_coordinates) == robot1
            assert grid.get_tile_from_grid(robot2_coordinates) == robot2
            print(grid)

    def test_out_of_bound(self):
        base_grid = BaseGrid(5, 5)

        robot = Robot(Direction.UP)
        robot_coordinates = Coordinates(4, 4)

        base_grid.add_tile_to_grid(robot, robot_coordinates)
        shared_grid_access = SharedGridAccess(base_grid, Manager())
        h_info = shared_grid_access.try_move_robot(robot, Direction.UP)
        assert h_info.hit_type == HitType.ERROR
        assert isinstance(h_info.inner_error, OutOfBoundCoordinatesError)
        with shared_grid_access.grid_lock_sync as grid:
            assert grid.get_tile_from_grid(robot_coordinates) == robot
            print(grid)

    def test_put_block(self):
        base_grid = BaseGrid(5, 5)

        robot = Robot(Direction.UP)
        robot_coordinates = Coordinates(4, 4)
        inner_block = Tile(TileType.BLOCK)
        robot.take_block(inner_block)

        base_grid.add_tile_to_grid(robot, robot_coordinates)
        shared_grid_access = SharedGridAccess(base_grid, Manager())
        h_info = shared_grid_access.try_put_block(robot, Direction.UP)
        assert h_info.hit_type == HitType.ERROR
        assert isinstance(h_info.inner_error, OutOfBoundCoordinatesError)
        h_info = shared_grid_access.try_put_block(robot, Direction.LEFT)
        assert h_info.hit_type == HitType.ERROR
        assert isinstance(h_info.inner_error, WrongBlockPutDirection)
        h_info = shared_grid_access.try_rotate_robot(robot, Direction.LEFT)
        assert h_info.hit_type == HitType.ROTATED
        robot.rotate_to_direction(Direction.LEFT)
        h_info = shared_grid_access.try_put_block(robot, Direction.LEFT)
        assert h_info.hit_type == HitType.PLACED_BLOCK
        inner_block = robot.pop_block()
        h_info = shared_grid_access.try_move_robot(robot, Direction.LEFT)
        assert h_info.hit_type == HitType.BLOCK
        assert isinstance(h_info.inner_error, TileTakenException)
        assert inner_block == h_info.inner_error.get_tile()
