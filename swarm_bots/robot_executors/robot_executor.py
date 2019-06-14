import abc
from multiprocessing import Process

from swarm_bots.goal.goal_building import GoalBuilding
from swarm_bots.grid.shared_grid_access import SharedGridAccess
from swarm_bots.robot_executors.robot_shared_actions_executor import RobotSharedActionsExecutor
from swarm_bots.tiles.robot import Robot


class RobotExecutor(metaclass=abc.ABCMeta):
    def __init__(self, robot: Robot, shared_grid_access: SharedGridAccess, goal_building: GoalBuilding):
        self.robot = robot
        self.goal_building = goal_building
        self.shared_grid_access = shared_grid_access
        self.private_grid = self.shared_grid_access.get_private_copy()
        self.process = Process(target=self.start_process)
        self.robot_coordinates = self.private_grid.get_coord_from_tile(self.robot)
        self.shared_actions_executor = RobotSharedActionsExecutor(
            robot=robot,
            shared_grid_access=shared_grid_access,
            private_grid=self.private_grid,
            robot_coordinates=self.robot_coordinates
        )

    def start_working(self):
        self.process.start()

    def wait_for_finish(self):
        self.process.join()

    def start_process(self):
        raise NotImplementedError()
