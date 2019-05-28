import abc

from swarm_bots.grid.shared_grid_access import SharedGridAccess
from swarm_bots.tiles.robot import Robot

class RobotExecutor(metaclass=abc.ABCMeta):
    def __init__(self, robot: Robot, shared_grid_access: SharedGridAccess):
        self.robot = robot
        self.shared_grid_access = shared_grid_access
        self.private_grid = self.shared_grid_access.get_private_copy()

    def start_working(self):
        raise NotImplementedError()

    def wait_for_finish(self):
        raise NotImplementedError()
