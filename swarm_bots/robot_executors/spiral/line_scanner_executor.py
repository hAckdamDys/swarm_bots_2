from swarm_bots.grid.base_grid import BaseGrid
from swarm_bots.grid.shared_grid_access import SharedGridAccess
from swarm_bots.robot_executors.spiral.line_to_middle import LineToMiddle
from swarm_bots.tiles.robot import Robot
from swarm_bots.utils.coordinates import Coordinates


class LineScannerExecutor:
    def __init__(self,
                 robot: Robot,
                 robot_coordinates: Coordinates,
                 private_grid: BaseGrid,
                 shared_grid_access: SharedGridAccess):
        self.shared_grid_access = shared_grid_access
        self.private_grid = private_grid
        self.robot_coordinates = robot_coordinates
        self.robot = robot
        # TODO: implement line scanner logic

    # scan line while changing line and all inner variables
    def scan_line(self, line: LineToMiddle):
        raise NotImplementedError()