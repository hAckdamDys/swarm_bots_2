from swarm_bots.grid.base_grid import BaseGrid
from swarm_bots.grid.shared_grid_access import SharedGridAccess
from swarm_bots.robot_executors.spiral.line_to_middle import LineToMiddle
from swarm_bots.robot_executors.spiral.source_position import SourcePosition
from swarm_bots.tiles.robot import Robot
from swarm_bots.utils.coordinates import Coordinates


class HighwayExecutor:
    def __init__(self,
                 robot: Robot,
                 robot_coordinates: Coordinates,
                 private_grid: BaseGrid,
                 shared_grid_access: SharedGridAccess):
        self.shared_grid_access = shared_grid_access
        self.private_grid = private_grid
        self.robot_coordinates = robot_coordinates
        self.robot = robot
        # TODO: implement highway around grid and logic how to get into places

    # makes robot go to line start using highway
    def go_to_line_start(self, line: LineToMiddle):
        raise NotImplementedError()

    def go_get_source(self, source: SourcePosition):
        raise NotImplementedError()
