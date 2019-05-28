import unittest
import numpy as np

from goal.goal_building import GoalBuilding


class TestGoalBuilding(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.textGrid = """
        0 0 0 0 0 0 0
        0 0 0 1 0 0 0
        0 0 1 2 1 0 0
        0 1 2 3 2 1 0
        0 0 1 2 1 0 0
        0 0 0 1 0 0 0
        0 0 0 0 0 0 0
        """
        self.resultGrid = np.array([
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 1, 2, 1, 0, 0],
            [0, 1, 2, 3, 2, 1, 0],
            [0, 0, 1, 2, 1, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0]
        ])

    def test_goalBuildingInitialization(self):
        text_grid = self.textGrid
        goal_building = GoalBuilding(text_grid)
        assert goal_building

    def test_simple_grid(self):
        text_grid = self.textGrid
        result_grid = self.resultGrid
        goal_building = GoalBuilding(text_grid)
        assert goal_building
        assert np.array_equal(goal_building.grid, result_grid)

    def test_wrong_grid(self):
        text_grid = """
        0 0 0 0 0 0 0
        0 0 0 1 0 0 0
        0 0 1 2 1 0 0
        0 1 2 3 2 1 0
        0 0 1 2 1 0 0
        0 0 0 1 0 0 0
        0 0 0 0 0 0
        """
        self.assertRaises(ValueError, GoalBuilding, text_grid)


if __name__ == '__main__':
    unittest.main()
