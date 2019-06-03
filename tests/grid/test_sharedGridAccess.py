from multiprocessing import Manager
from unittest import TestCase

from swarm_bots.goal.goal_building import GoalBuilding
from swarm_bots.grid.base_grid import BaseGrid
from swarm_bots.grid.shared_grid_access import SharedGridAccess
from swarm_bots.tiles.robot import Robot
from swarm_bots.utils.coordinates import Coordinates
from swarm_bots.utils.direction import Direction


class TestSharedGridAccess(TestCase):
    def test_shared_sync(self):
        base_grid = BaseGrid(5, 5)

        robot1 = Robot(Direction.UP)
        robot1_coordinates = Coordinates(2, 2)
        robot1_coordinates_2 = Coordinates(2, 3)

        robot2 = Robot(Direction.RIGHT)
        robot2_coordinates = Coordinates(1, 3)

        base_grid.add_tile_to_grid(robot1, robot1_coordinates)
        base_grid.add_tile_to_grid(robot2, robot2_coordinates)
        shared_grid_access = SharedGridAccess(base_grid, Manager())
        shared_grid_access.try_rotate_robot(robot2, Direction.LEFT)
        shared_grid_access.try_move_robot(robot1, Direction.UP)
        with shared_grid_access.grid_lock_sync as grid:
            print(grid)

