import numpy as np
import os


# static grid where there are only goal
from swarm_bots.goal.goal_building import GoalBuilding


class GoalBuilding2D(GoalBuilding):
    def parse_text_grid(self, text_grid: str):
        row_sep = ';'
        text_grid_tmp = text_grid.replace(os.linesep, row_sep)
        text_grid_tmp = text_grid_tmp.replace('\n', row_sep)
        text_grid_tmp = text_grid_tmp.lstrip(row_sep).rstrip(row_sep)
        self.height = text_grid_tmp.count(row_sep)
        first_row = np.fromstring(text_grid_tmp.split(row_sep)[0], dtype=int,
                                  sep=' ')
        self.width = first_row.shape[0]
        self.grid = np.fromstring(text_grid, dtype=bool, sep=' ').reshape(
            self.height, self.width)


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
