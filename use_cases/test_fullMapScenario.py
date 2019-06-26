from multiprocessing import Manager
from typing import List
from unittest import TestCase

from swarm_bots.goal.goal_building_2d import GoalBuilding2D
from swarm_bots.grid.base_grid import BaseGrid
from swarm_bots.grid.shared_grid_access import SharedGridAccess
from swarm_bots.robot_executors.robot_executor import RobotExecutor
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
        robot_1_coordinates = Coordinates(0, 1)
        robot_2_coordinates = Coordinates(23, 16)

        base_grid = BaseGrid(goal_building.width, goal_building.height)
        base_grid.add_tile_to_grid(Tile(TileType.SOURCE), Coordinates(0, 0))
        base_grid.add_tile_to_grid(Tile(TileType.SOURCE), Coordinates(goal_building.width-1, 0))
        base_grid.add_tile_to_grid(Tile(TileType.SOURCE), Coordinates(goal_building.width-1, goal_building.height-1))
        base_grid.add_tile_to_grid(Tile(TileType.SOURCE), Coordinates(0, goal_building.height-1))

        shared_grid_access = SharedGridAccess(base_grid, manager=Manager())
        spin = Spin.ANTI_CLOCKWISE
        goal_to_edges_splitter = GoalToEdgesXSplitter(goal_building, spin)

        robot_1_executor = SpiralRobotExecutor(
            robot=robot_1,
            shared_grid_access=shared_grid_access,
            goal_building=goal_building,
            goal_to_edges_splitter=goal_to_edges_splitter,
            spin=spin,
            start_offset=0,
            start_edge_index=0,
            robot_coordinates=robot_1_coordinates,
            sleep_tick_seconds=0.000001
        )

        robot_2_executor = SpiralRobotExecutor(
            robot=robot_2,
            shared_grid_access=shared_grid_access,
            goal_building=goal_building,
            goal_to_edges_splitter=goal_to_edges_splitter,
            spin=spin,
            start_offset=0,
            start_edge_index=2,
            robot_coordinates=robot_2_coordinates,
            sleep_tick_seconds=0.000001
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

    def test_multi_robot(self):
        text_grid = """
               0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
               0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
               0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0
               0 0 0 0 0 0 0 0 1 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 1 0 0 0 0 0 0 1 0 0 0 0
               0 0 0 0 0 0 0 0 1 0 0 1 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 1 1 0 0 0 1 0 0 0 1 0 0 1 0 0 0 1 0 0 0 0
               0 0 0 0 0 1 0 0 1 0 1 1 1 0 0 1 0 0 1 0 0 0 1 1 1 1 1 1 1 1 1 1 1 0 0 1 0 0 0 1 0 0 1 0 0 0 1 0 1 0 0
               0 0 0 0 0 1 0 0 1 0 1 1 1 1 0 0 0 0 1 0 0 0 1 1 1 1 1 1 1 1 1 1 1 0 0 1 0 1 0 1 0 0 1 0 0 0 1 0 1 0 0
               0 0 0 0 0 1 0 0 1 0 1 1 1 1 0 0 0 0 1 0 0 0 1 1 1 1 1 1 1 1 1 1 1 0 0 1 0 1 0 1 0 0 1 0 0 0 1 0 1 0 0
               0 0 0 0 0 1 0 0 0 0 1 1 1 1 0 1 0 0 1 0 0 0 1 1 1 1 1 1 1 1 1 1 1 0 0 1 0 1 0 1 0 0 1 0 0 0 1 0 1 0 0
               0 0 0 0 0 1 0 0 0 0 1 1 1 1 0 0 0 0 1 0 0 0 1 1 1 1 1 1 1 1 1 1 1 0 0 1 0 1 0 1 0 0 1 0 0 0 1 0 1 0 0
               0 0 0 0 0 1 0 0 0 0 0 1 1 1 1 0 0 0 1 0 0 0 1 1 1 1 1 1 1 1 1 1 1 0 0 1 0 1 0 1 0 0 1 0 0 0 1 0 1 0 0
               0 0 0 0 0 1 0 0 1 0 0 0 1 1 1 0 0 0 1 0 0 0 1 1 1 1 1 1 1 1 1 1 1 0 0 1 0 1 0 1 0 0 1 0 0 0 0 0 1 0 0
               0 0 0 0 0 1 0 0 1 0 0 0 1 1 1 0 0 0 1 0 0 0 1 1 1 1 1 1 1 1 1 0 1 0 0 1 0 1 0 0 0 0 1 0 0 0 0 0 1 0 0
               0 0 0 0 0 0 0 0 1 0 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 1 0 0
               0 0 0 0 0 0 0 0 1 0 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0
               0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
               0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
               0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
               """
        goal_building = GoalBuilding2D(text_grid=text_grid)
        robots: List[Robot] = list()
        robots_pos: List[Coordinates] = list()
        how_many_robots = 4

        for i in range(how_many_robots):
            robots.append(Robot(Direction.UP))
            robots_pos.append(Coordinates(i+1, 0))

        base_grid = BaseGrid(goal_building.width, goal_building.height)
        base_grid.add_tile_to_grid(Tile(TileType.SOURCE), Coordinates(0, 0))
        base_grid.add_tile_to_grid(Tile(TileType.SOURCE), Coordinates(goal_building.width-1, 0))
        base_grid.add_tile_to_grid(Tile(TileType.SOURCE), Coordinates(goal_building.width-1, goal_building.height-1))
        base_grid.add_tile_to_grid(Tile(TileType.SOURCE), Coordinates(0, goal_building.height-1))

        shared_grid_access = SharedGridAccess(base_grid, manager=Manager())
        spin = Spin.ANTI_CLOCKWISE
        goal_to_edges_splitter = GoalToEdgesXSplitter(goal_building, spin)

        robot_executors: List[RobotExecutor] = list()
        for i in range(how_many_robots):
            robot_executors.append(SpiralRobotExecutor(
                robot=robots[i],
                shared_grid_access=shared_grid_access,
                goal_building=goal_building,
                goal_to_edges_splitter=goal_to_edges_splitter,
                spin=spin,
                start_offset=i,
                start_edge_index=i % 4,
                robot_coordinates=robots_pos[i],
                sleep_tick_seconds=0
            ))

        with shared_grid_access.grid_lock_sync as grid:
            for i in range(how_many_robots):
                grid.add_tile_to_grid(robots[i], robots_pos[i])

        for i in range(how_many_robots):
            robot_executors[i].start_working()

        for i in range(how_many_robots):
            robot_executors[i].wait_for_finish()

        grid = shared_grid_access.get_private_copy()
        assert goal_building.validate_grid(grid)
