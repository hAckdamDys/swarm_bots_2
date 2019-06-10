from typing import List

import numpy as np

from swarm_bots.goal.goal_building import GoalBuilding
from swarm_bots.grid.base_grid import BaseGrid
from swarm_bots.robot_executors.spiral.goal_to_edges_splitters.goal_to_edges_splitter import GoalToEdgesSplitter
from swarm_bots.robot_executors.spiral.grid_edge import GridEdge


class GoalToEdgesXSplitter(GoalToEdgesSplitter):
    def __init__(self, goal_building: GoalBuilding):
        super().__init__(goal_building)
        self.is_splitted = False

    def get_edges(self) -> List[GridEdge]:
        if not self.is_splitted:
            self._split_goal()
        return self.edges

    def _split_goal(self):
        if self.is_splitted:
            return
        width = self.goal_building.width
        height = self.goal_building.height
        # first add elements that are not on diagonals
        # test_array = np.zeros((width, height), dtype=int)
        counts = np.zeros(4, dtype=int)  # how many blocks each edge have assigned
        is_raising_diag = np.zeros((width, height), dtype=bool) # True if diag on field
        is_decreasing_diag = np.zeros((width, height), dtype=bool)
        if width == 1 or height == 1:
            raise ValueError("goal_building should be at least 3x3")
        if (width % 2 == 1) and (height % 2 == 1):
            mid_block_x = width//2
            mid_block_y = height//2
            mid_block_pos = (mid_block_x, mid_block_y)
            is_decreasing_diag[mid_block_pos] = True
            is_raising_diag[mid_block_pos] = True
            # D  0 R
            # 0 RD 0
            # R  0 D
            is_decreasing_diag[mid_block_x - 1, mid_block_y + 1] = True
            is_decreasing_diag[mid_block_x + 1, mid_block_y - 1] = True
            is_raising_diag[mid_block_x + 1, mid_block_y + 1] = True
            is_raising_diag[mid_block_x - 1, mid_block_y - 1] = True


class GoalBuildingMock(GoalBuilding):
    def __init__(self):
        self.width = 13
        self.height = 19

    def validate_grid(self, base_grid: BaseGrid):
        pass


if __name__ == '__main__':
    goal_building_mock = GoalBuildingMock()
    splitter = GoalToEdgesXSplitter(goal_building_mock)
    splitter._split_goal()
