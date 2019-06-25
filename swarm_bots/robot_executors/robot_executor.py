import abc
from multiprocessing import Process

from swarm_bots.goal.goal_building import GoalBuilding
from swarm_bots.grid.shared_grid_access import SharedGridAccess
from swarm_bots.robot_executors.robot_shared_actions_executor import RobotSharedActionsExecutor
from swarm_bots.robot_executors.robot_shared_actions_executor_with_sleep import RobotSharedActionsExecutorWithSleep
from swarm_bots.tiles.robot import Robot
from swarm_bots.utils.coordinates import Coordinates


class RobotExecutor(metaclass=abc.ABCMeta):
    def __init__(self, robot: Robot, shared_grid_access: SharedGridAccess, goal_building: GoalBuilding,
                 sleep_tick_seconds: float = None, robot_coordinates: Coordinates = None):
        self.robot = robot
        self.goal_building = goal_building
        self.shared_grid_access = shared_grid_access
        self.private_grid = self.shared_grid_access.get_private_copy()
        self.process = Process(target=self.start_process)
        if robot_coordinates is None:
            self.robot_coordinates = self.private_grid.get_coord_from_tile(self.robot)
        else:
            self.robot_coordinates = robot_coordinates.copy()
        if sleep_tick_seconds is None:
            self.shared_actions_executor = RobotSharedActionsExecutor(
                robot=robot,
                shared_grid_access=shared_grid_access,
                private_grid=self.private_grid,
                robot_coordinates=self.robot_coordinates
            )
        else:
            self.shared_actions_executor = RobotSharedActionsExecutorWithSleep(
                robot=robot,
                shared_grid_access=shared_grid_access,
                private_grid=self.private_grid,
                robot_coordinates=self.robot_coordinates,
                sleep_tick_seconds=sleep_tick_seconds
            )

    def start_working(self):
        self.process.start()

    def wait_for_finish(self):
        self.process.join()

    def start_process(self):
        raise NotImplementedError()
