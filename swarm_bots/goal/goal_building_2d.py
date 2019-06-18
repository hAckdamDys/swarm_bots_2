import numpy as np


# static grid where there are only goal
from swarm_bots.goal.goal_building import GoalBuilding
from swarm_bots.grid.base_grid import BaseGrid


class GoalBuilding2D(GoalBuilding):
    def parse_text_grid(self, text_grid: str):
        self.dtype = bool
        super().parse_text_grid(text_grid)

    def validate_grid(self, base_grid: BaseGrid):
        base_block_grid = base_grid.get_block_grid()
        return np.array_equal(base_block_grid, self.grid)


if __name__ == '__main__':
    building = GoalBuilding2D(
        """
        0 0 0 0 0
        0 0 1 0 0
        0 1 1 1 0
        0 0 1 0 0
        0 0 0 0 0
        """
    )
    print(building)
