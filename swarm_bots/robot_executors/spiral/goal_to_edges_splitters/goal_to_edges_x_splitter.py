from typing import List, Iterable

import numpy as np

from swarm_bots.goal.goal_building import GoalBuilding
from swarm_bots.goal.goal_building_2d import GoalBuilding2D
from swarm_bots.grid.base_grid import BaseGrid
from swarm_bots.robot_executors.spiral.goal_to_edges_splitters.goal_to_edges_splitter import GoalToEdgesSplitter
from swarm_bots.robot_executors.spiral.grid_edge import GridEdge
from swarm_bots.robot_executors.spiral.line_to_middle import LineToMiddle
from swarm_bots.robot_executors.spiral.source_position import SourcePosition
from swarm_bots.utils.coordinates import Coordinates
from swarm_bots.utils.direction import Direction


class GoalToEdgesXSplitter(GoalToEdgesSplitter):
    def __init__(self, goal_building: GoalBuilding, robot_coordinates: Coordinates):
        super().__init__(goal_building)
        width = self.goal_building.width
        height = self.goal_building.height
        self.source_positions = list()
        self.source_positions.append(SourcePosition(Coordinates(0, 0)))
        self.source_positions.append(SourcePosition(Coordinates(0, height - 1)))
        self.source_positions.append(SourcePosition(Coordinates(width - 1, height - 1)))
        self.source_positions.append(SourcePosition(Coordinates(width - 1, 0)))
        self.robot_coordinates = robot_coordinates
        self.is_splitted = False

    def get_edges(self) -> List[GridEdge]:
        if not self.is_splitted:
            self._split_goal()
        return self.edges

    def _split_goal(self):
        if self.is_splitted:
            return
        self.edges: List[GridEdge] = list()
        width = self.goal_building.width
        height = self.goal_building.height
        # first add elements that are not on diagonals
        # test_array = np.zeros((width, height), dtype=int)
        edge_block_counts = np.zeros(4, dtype=int)  # how many blocks each edge have assigned
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
        down_left_corner_walker = ToCornerWalker(raising_diag_grid, x_direction=Direction.LEFT,
                                                 y_direction=Direction.DOWN, pos=raising_diag_left_pos,
                                                 width=width, height=height)
        down_left_corner_walker.update_diag_to_corner()
        top_left_corner_walker = ToCornerWalker(decreasing_diag_grid, x_direction=Direction.LEFT,
                                                y_direction=Direction.UP, pos=decreasing_diag_left_pos,
                                                width=width, height=height)
        top_left_corner_walker.update_diag_to_corner()

        both_diags = (raising_diag_grid + 2 * decreasing_diag_grid)
        # now we want to create lines for each edge:
        edge_builds: List[EdgeBuild] = [EdgeBuild(width, height, direction.get_opposite()) for direction in Direction]
        edge_num = -1
        for direction in Direction:
            edge_num += 1
            direction: Direction = direction
            if direction.is_x_axis():
                # for x axis we have y axis length amount of lines
                edge_len = height
                opposite_len = width
            else:
                edge_len = width
                opposite_len = height
            # for each line
            for i in range(edge_len):
                # if direction = UP
                # we would have something like this:
                # if rising then last index
                if direction == Direction.LEFT:
                    line_scan_coordinate = Coordinates(0, i)
                elif direction == Direction.UP:
                    line_scan_coordinate = Coordinates(i, opposite_len - 1)
                elif direction == Direction.RIGHT:
                    line_scan_coordinate = Coordinates(opposite_len - 1, i)
                else:  # DOWN
                    line_scan_coordinate = Coordinates(i, 0)
                edge_builds[edge_num].add_line_start(line_scan_coordinate)
                for j in range(opposite_len):
                    diag_tile = both_diags[line_scan_coordinate.get_array_index()]
                    if diag_tile:
                        if diag_tile != 10 and self.goal_building.grid[line_scan_coordinate.get_array_index()]:
                            both_diags[line_scan_coordinate.get_array_index()] = 10
                            # TODO: decide where this tile goes
                            # decide_later.append(block_line, coordinate, edge_set) something like this
                            # for now lets just add to first that got this
                            edge_builds[edge_num].block_lines[(i, j)] = True
                            edge_block_counts[edge_num] += 1
                        break
                    if self.goal_building.grid[line_scan_coordinate.get_array_index()]:
                        edge_builds[edge_num].block_lines[(i, j)] = True
                        edge_block_counts[edge_num] += 1
                    line_scan_coordinate = line_scan_coordinate.create_neighbour_coordinate(direction.get_opposite())

        edge_num = -1
        for direction in Direction:
            edge_num += 1
            edge_build = edge_builds[edge_num]
            lines: List[LineToMiddle] = list()
            for i in range(edge_build.length):
                line = LineToMiddle(edge_build.line_starts[i], direction.get_opposite(), edge_build.block_lines[i])
                lines.append(line)
            edge = GridEdge(self.robot_coordinates, self.source_positions, edge_build.length, lines)
            self.edges.append(edge)

        # # TODO: delete later this is just for debug:
        # diags = (raising_diag_grid + 2 * decreasing_diag_grid).T
        # diags = np.flip(diags, 0)
        # print(diags, "a")


class EdgeBuild:
    def __init__(self, width: int, height: int, line_direction: Direction):
        self.line_starts: List[Coordinates] = list()
        if line_direction.is_x_axis():
            self.length = width
            self.block_lines = np.zeros((width, height), dtype=bool)
        else:
            self.length = height
            self.block_lines = np.zeros((height, width), dtype=bool)
        self.line_direction = line_direction

    def add_line_start(self, coord: Coordinates):
        self.line_starts.append(coord)


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
            # diag_2 = self.diag_grid.copy()
            # diag_2 = diag_2.T
            # diag_2 = np.flip(diag_2, 0)
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
            # different approach
            # real_x = (-self.width//2+self.pos.x) * (self.x_direction.is_x_or_y_rising()*2-1)
            # real_y = (-self.height//2+self.pos.y) * (self.y_direction.is_x_or_y_rising()*2-1)
            # if real_y < self.height*real_x/self.width:
            if x_progress > y_progress:
                self._make_y_progress()
            else:
                self._make_x_progress()


class GoalBuildingMock(GoalBuilding):
    def __init__(self):
        self.width = 11
        self.height = 16
        self.grid = np.zeros((self.width, self.height), dtype=bool)
        self.grid[(7, 3)] = True
        self.grid[(7, 4)] = True
        self.grid[(8, 3)] = True
        self.grid[(8, 4)] = True

    def validate_grid(self, base_grid: BaseGrid):
        pass


if __name__ == '__main__':
    goal_building_mock = GoalBuildingMock()
    building = GoalBuilding2D(
        """
        0 0 0 0 0
        0 0 1 0 0
        0 1 1 1 0
        0 0 1 0 0
        0 0 0 0 0
        """
    )
    splitter = GoalToEdgesXSplitter(building, Coordinates(1, 0))
    splitter._split_goal()
