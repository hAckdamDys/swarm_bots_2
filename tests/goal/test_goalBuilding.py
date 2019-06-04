import unittest
import numpy as np

from swarm_bots.goal.goal_building import GoalBuilding


class TestGoalBuilding(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.text_grid = """
        0 0 0 0 0 0 0
        0 0 0 1 0 0 0
        0 0 1 2 1 0 0
        0 1 2 3 2 1 0
        0 0 1 2 1 0 0
        0 1 0 1 0 0 0
        0 0 0 0 0 0 0
        """
        self.result_grid = np.array([
            [0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 1, 0, 0, 0],
            [0, 0, 1, 2, 1, 0, 0],
            [0, 1, 2, 3, 2, 1, 0],
            [0, 0, 1, 2, 1, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0]
        ])

    def test_goalBuildingInitialization(self):
        text_grid = self.text_grid
        goal_building = GoalBuilding(text_grid)
        assert goal_building

    def test_simple_grid(self):
        text_grid = self.text_grid
        result_grid = self.result_grid
        goal_building = GoalBuilding(text_grid)
        assert goal_building
        assert np.array_equal(goal_building.grid, result_grid)

    def test_wrong_grid(self):
        text_grid = """
        0 0 0 0 0 0 0
        0 0 0 1 0 1 0
        0 0 1 2 1 0 0
        0 1 2 3 2 1 0
        0 0 1 2 1 0 0
        0 0 0 1 0 0 0
        0 0 0 0 0 0
        """
        self.assertRaises(ValueError, GoalBuilding, text_grid)


if __name__ == '__main__':
    unittest.main()
