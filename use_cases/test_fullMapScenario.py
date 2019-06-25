from multiprocessing import Manager
from unittest import TestCase

from swarm_bots.goal.goal_building_2d import GoalBuilding2D
from swarm_bots.grid.base_grid import BaseGrid
from swarm_bots.grid.shared_grid_access import SharedGridAccess
from swarm_bots.robot_executors.spiral.goal_to_edges_splitters.goal_to_edges_x_splitter import GoalToEdgesXSplitter
from swarm_bots.robot_executors.spiral.spiral_robot_executor import SpiralRobotExecutor
from swarm_bots.tiles.robot import Robot
from swarm_bots.tiles.tile import Tile, TileType
from swarm_bots.utils.coordinates import Coordinates
from swarm_bots.utils.direction import Direction
from swarm_bots.utils.spin import Spin


class TestFullMapScenario(TestCase):
    def test_simple_map(self):
        text_grid = """
               0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
               0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
               0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0
               0 0 0 0 0 0 0 0 1 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0
               0 0 0 0 0 0 0 0 1 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0
               0 0 0 0 0 1 0 0 1 0 1 1 1 0 0 1 0 0 1 0 0 0 0 0
               0 0 0 0 0 1 0 0 1 0 1 1 1 0 0 0 0 0 1 0 0 0 0 0
               0 0 0 0 0 1 0 0 1 0 1 1 1 0 0 0 0 0 1 0 0 0 0 0
               0 0 0 0 0 1 0 0 0 0 1 1 1 0 0 1 0 0 1 0 0 0 0 0
               0 0 0 0 0 1 0 0 0 0 1 1 1 0 0 0 0 0 1 0 0 0 0 0
               0 0 0 0 0 1 0 0 0 0 0 1 1 0 1 0 0 0 1 0 0 0 0 0
               0 0 0 0 0 1 0 0 1 0 0 0 1 0 1 0 0 0 1 0 0 0 0 0
               0 0 0 0 0 1 0 0 1 0 0 0 1 0 1 0 0 0 1 0 0 0 0 0
               0 0 0 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0
               0 0 0 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0
               0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
               0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
               0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
               """
        goal_building = GoalBuilding2D(text_grid=text_grid)
        robot_1 = Robot(Direction.DOWN)
        robot_1.id = 1000000001
        robot_2 = Robot(Direction.UP)
        robot_2.id = 1000000002
        robot_1_coordinates = Coordinates(0, 3)
        robot_2_coordinates = Coordinates(5, 0)

        base_grid = BaseGrid(goal_building.width, goal_building.height)
        base_grid.add_tile_to_grid(Tile(TileType.SOURCE), Coordinates(0, 0))
        base_grid.add_tile_to_grid(Tile(TileType.SOURCE), Coordinates(goal_building.width-1, 0))
        base_grid.add_tile_to_grid(Tile(TileType.SOURCE), Coordinates(goal_building.width-1, goal_building.height-1))
        base_grid.add_tile_to_grid(Tile(TileType.SOURCE), Coordinates(0, goal_building.height-1))

        shared_grid_access = SharedGridAccess(base_grid, manager=Manager())
        spin = Spin.CLOCKWISE
        goal_to_edges_splitter = GoalToEdgesXSplitter(goal_building, spin)

        robot_1_executor = SpiralRobotExecutor(
            robot=robot_1,
            shared_grid_access=shared_grid_access,
            goal_building=goal_building,
            goal_to_edges_splitter=goal_to_edges_splitter,
            spin=spin,
            start_offset=3,
            start_edge_index=0,
            robot_coordinates=robot_1_coordinates,
            sleep_tick_seconds=0.0001
        )

        robot_2_executor = SpiralRobotExecutor(
            robot=robot_2,
            shared_grid_access=shared_grid_access,
            goal_building=goal_building,
            goal_to_edges_splitter=goal_to_edges_splitter,
            spin=spin,
            start_offset=6,
            start_edge_index=0,
            robot_coordinates=robot_2_coordinates,
            sleep_tick_seconds=0.0001
        )

        with shared_grid_access.grid_lock_sync as grid:
            grid.add_tile_to_grid(robot_1, robot_1_coordinates)
            grid.add_tile_to_grid(robot_2, robot_2_coordinates)

        robot_1_executor.start_working()
        robot_2_executor.start_working()

        robot_1_executor.wait_for_finish()
        robot_2_executor.wait_for_finish()

        grid = shared_grid_access.get_private_copy()
        assert goal_building.validate_grid(grid)
