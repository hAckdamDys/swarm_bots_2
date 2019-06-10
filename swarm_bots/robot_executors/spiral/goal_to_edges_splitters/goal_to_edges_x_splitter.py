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
        test_array = np.zeros((width, height), dtype=int)
        counts = np.zeros(4, dtype=int)
        for x in range(width):
            for y in range(height):
                # if self
                if (y <= abs(height - (x * height / width))) and (y <= abs((x * height / width))):
                    test_array[(x, y)] += 1
                    counts[0] += 1
                    # left triangle
                if (y >= abs((x * height / width))) and (y >= abs(height - (x * height / width))):
                    test_array[(x, y)] += 10
                    counts[1] += 1
                    # right triangle
                if (y <= abs(height - (x * height / width))) and (y >= abs((x * height / width))):
                    test_array[(x, y)] += 100
                    counts[2] += 1
                    # up triangle
                if (y >= abs(height - (x * height / width))) and (y <= abs((x * height / width))):
                    test_array[(x, y)] += 1000
                    counts[3] += 1
                    # down triangle
                # if y >= abs(height-np.floor(x*height/width))-1:
                #     test_array[(x, y)] += 10
                # if -y <= height-abs(np.ceil(x*height/width))-1:
                #     test_array[(x, y)] += 100
                # if -y >= height-abs(np.floor(x*height/width))-1:
                #     test_array[(x, y)] += 1000
        # TODO: delete later
        test_array = np.flip(test_array, 0)
        print(test_array, counts)


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
