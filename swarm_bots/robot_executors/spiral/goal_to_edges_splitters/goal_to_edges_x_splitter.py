from typing import List, Iterable

import numpy as np

from swarm_bots.goal.goal_building import GoalBuilding
from swarm_bots.grid.base_grid import BaseGrid
from swarm_bots.robot_executors.spiral.goal_to_edges_splitters.goal_to_edges_splitter import GoalToEdgesSplitter
from swarm_bots.robot_executors.spiral.grid_edge import GridEdge
from swarm_bots.utils.coordinates import Coordinates
from swarm_bots.utils.direction import Direction


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
        raising_diag_grid = np.zeros((width, height), dtype=bool)  # True if diag on field
        decreasing_diag_grid = np.zeros((width, height), dtype=bool)
        if width == 1 or height == 1:
            raise ValueError("goal_building should be at least 3x3")
        if (width % 2 == 1) and (height % 2 == 1):
            mid_block_x = width // 2
            mid_block_y = height // 2
            mid_block_pos = (mid_block_x, mid_block_y)
            decreasing_diag_grid[mid_block_pos] = True
            raising_diag_grid[mid_block_pos] = True
            # D  0 R
            # 0 RD 0
            # R  0 D
            decreasing_diag_left_pos = Coordinates(mid_block_x - 1, mid_block_y + 1)
            decreasing_diag_grid[decreasing_diag_left_pos.get_array_index()] = True
            decreasing_diag_right_pos = Coordinates(mid_block_x + 1, mid_block_y - 1)
            decreasing_diag_grid[decreasing_diag_right_pos.get_array_index()] = True

            raising_diag_left_pos = Coordinates(mid_block_x - 1, mid_block_y - 1)
            raising_diag_grid[raising_diag_left_pos.get_array_index()] = True
            raising_diag_right_pos = Coordinates(mid_block_x + 1, mid_block_y + 1)
            raising_diag_grid[raising_diag_right_pos.get_array_index()] = True
        else:
            # D R
            # R D
            left_x = width // 2 - 1
            if height % 2 == 0:
                down_y = height // 2 - 1
            else:
                down_y = height // 2
            decreasing_diag_left_pos = Coordinates(left_x, down_y + 1)
            decreasing_diag_grid[decreasing_diag_left_pos.get_array_index()] = True
            decreasing_diag_right_pos = Coordinates(left_x + 1, down_y)
            decreasing_diag_grid[decreasing_diag_right_pos.get_array_index()] = True

            raising_diag_left_pos = Coordinates(left_x, down_y)
            raising_diag_grid[raising_diag_left_pos.get_array_index()] = True
            raising_diag_right_pos = Coordinates(left_x + 1, down_y + 1)
            raising_diag_grid[raising_diag_right_pos.get_array_index()] = True

        top_right_corner_walker = ToCornerWalker(raising_diag_grid, x_direction=Direction.RIGHT,
                                                 y_direction=Direction.UP, pos=raising_diag_right_pos,
                                                 width=width, height=height)
        top_right_corner_walker.update_diag_to_corner()
        down_right_corner_walker = ToCornerWalker(decreasing_diag_grid, x_direction=Direction.RIGHT,
                                                  y_direction=Direction.DOWN, pos=decreasing_diag_right_pos,
                                                  width=width, height=height)
        down_right_corner_walker.update_diag_to_corner()

        # TODO: delete later this is just for debug:
        # diags = np.flip(raising_diag_grid + 2 * decreasing_diag_grid, 0)
        diags = (raising_diag_grid + 2 * decreasing_diag_grid).T
        diags = np.flip(diags, 0)
        print(diags, "a")


class ToCornerWalker:
    def __init__(self, diag_grid: np.ndarray, x_direction: Direction, y_direction: Direction, pos: Coordinates,
                 width: int, height: int):
        self.height = height
        self.width = width
        self.pos: Coordinates = pos
        self.diag_grid = diag_grid
        self.x_direction = x_direction
        self.y_direction = y_direction
        self.last_x_pos = self.x_direction.is_x_or_y_rising() * (self.width - 1)
        self.last_y_pos = self.y_direction.is_x_or_y_rising() * (self.height - 1)
        self.last_pos = Coordinates(self.last_x_pos, self.last_y_pos)
        self.was_last_x = False
        self.was_last_y = False

    def _get_x_progress(self):
        if self.x_direction == Direction.RIGHT:
            return (1000 * self.pos.x + 1) // self.width
        return 1000 - ((1000 * self.pos.x + 1) // self.width)

    def _get_y_progress(self):
        if self.y_direction == Direction.UP:
            return (1000 * self.pos.y + 1) // self.height
        return 1000 - ((1000 * self.pos.y + 1) // self.height)

    def _make_x_progress(self):
        if self.pos.x == self.last_x_pos:
            raise ValueError("this cannot happen, fix update diag alg")
        if self.was_last_y:
            self.diag_grid[self.pos.get_array_index()] = False
            self.was_last_y = False
        else:
            self.was_last_x = True
        self.pos = self.pos.create_neighbour_coordinate(self.x_direction)
        self.diag_grid[self.pos.get_array_index()] = True

    def _make_y_progress(self):
        if self.pos.y == self.last_y_pos:
            raise ValueError("this cannot happen, fix update diag alg")
        if self.was_last_x:
            self.diag_grid[self.pos.get_array_index()] = False
            self.was_last_x = False
        else:
            self.was_last_y = True
        self.pos = self.pos.create_neighbour_coordinate(self.y_direction)
        self.diag_grid[self.pos.get_array_index()] = True

    def update_diag_to_corner(self):
        while True:
            diag_2 = self.diag_grid.copy()
            diag_2 = diag_2.T
            diag_2 = np.flip(diag_2, 0)
            if self.pos.x == self.last_x_pos:
                if self.pos.y == self.last_y_pos:
                    break
                self._make_y_progress()
                self.update_diag_to_corner()
                break
            if self.pos.y == self.last_y_pos:
                self._make_x_progress()
                self.update_diag_to_corner()
                break
            x_progress = self._get_x_progress()
            y_progress = self._get_y_progress()
            if x_progress == y_progress:
                if self.was_last_y:
                    self._make_x_progress()
                else:
                    self._make_y_progress()
            elif x_progress > y_progress:
                self._make_y_progress()
            else:
                self._make_x_progress()


class GoalBuildingMock(GoalBuilding):
    def __init__(self):
        self.width = 12
        self.height = 19

    def validate_grid(self, base_grid: BaseGrid):
        pass


if __name__ == '__main__':
    goal_building_mock = GoalBuildingMock()
    splitter = GoalToEdgesXSplitter(goal_building_mock)
    splitter._split_goal()
