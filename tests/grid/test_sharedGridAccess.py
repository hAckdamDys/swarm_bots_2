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

        robot1 = Robot(Direction.DOWN)
        robot1_coordinates = Coordinates(2, 3)
        robot1_future_rotate = Direction.RIGHT

        robot2 = Robot(Direction.DOWN)
        robot2_coordinates = Coordinates(1, 3)
        # robot2_future_rotate = Direction.DOWN

        base_grid.add_tile_to_grid(robot1, robot1_coordinates)
        base_grid.add_tile_to_grid(robot2, robot2_coordinates)
        shared_grid_access = SharedGridAccess(base_grid, Manager())
        shared_grid_access.try_rotate_robot(robot1, robot1_future_rotate)
        print(shared_grid_access.manager_list[0])
