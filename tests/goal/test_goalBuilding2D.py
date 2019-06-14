import unittest
import numpy as np

from swarm_bots.goal.goal_building_2d import GoalBuilding2D
from swarm_bots.grid.base_grid import BaseGrid
from swarm_bots.tiles.tile import TileType, Tile
from swarm_bots.utils.coordinates import Coordinates


class TestGoalBuilding2D(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.text_grid = """
        0 0 0 0 0
        0 0 1 0 0
        0 1 0 1 0
        0 0 0 0 1
        """
        self.result_grid = np.zeros((5, 4), dtype=bool)
        self.result_grid[1, 1] = True
        self.result_grid[2, 2] = True
        self.result_grid[3, 1] = True
        self.result_grid[4, 0] = True

    def test_goalBuildingInitialization(self):
        text_grid = self.text_grid
        goal_building = GoalBuilding2D(text_grid)
        assert goal_building

    def test_simple_grid(self):
        text_grid = self.text_grid
        result_grid = self.result_grid
        goal_building = GoalBuilding2D(text_grid)
        assert goal_building
        assert np.array_equal(goal_building.grid, result_grid)

    def test_validate(self):
        base_grid = BaseGrid(5, 4)
        base_grid.add_tile_to_grid(Tile(TileType.BLOCK), Coordinates(1, 1))
        base_grid.add_tile_to_grid(Tile(TileType.BLOCK), Coordinates(2, 2))
        base_grid.add_tile_to_grid(Tile(TileType.BLOCK), Coordinates(3, 1))
        base_grid.add_tile_to_grid(Tile(TileType.BLOCK), Coordinates(4, 0))
        goal_building = GoalBuilding2D(self.text_grid)
        assert goal_building.validate_grid(base_grid)
        base_grid.add_tile_to_grid(Tile(TileType.BLOCK), Coordinates(3, 3))
        assert not goal_building.validate_grid(base_grid)
        base_grid.pop_tile_from_grid(Coordinates(3, 3))
        assert goal_building.validate_grid(base_grid)
        base_grid.remove_tile_from_grid(Coordinates(2, 2))
        assert not goal_building.validate_grid(base_grid)
        print(str(goal_building))


if __name__ == '__main__':
    unittest.main()
