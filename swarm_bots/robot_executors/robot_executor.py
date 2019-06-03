import abc
from multiprocessing import Process

from swarm_bots.goal.goal_building import GoalBuilding
from swarm_bots.grid.shared_grid_access import SharedGridAccess
from swarm_bots.robot_executors.hit_information import HitInformation, HitType
from swarm_bots.tiles.robot import Robot
from swarm_bots.utils.direction import Direction


class RobotExecutor(metaclass=abc.ABCMeta):
    def __init__(self, robot: Robot, shared_grid_access: SharedGridAccess, goal_building: GoalBuilding):
        self.robot = robot
        self.goal_building = goal_building
        self.shared_grid_access = shared_grid_access
        self.private_grid = self.shared_grid_access.get_private_copy()
        self.process = Process(target=self.start_process)

    def start_working(self):
        self.process.start()

    def try_rotate_robot(self, direction: Direction) -> HitInformation:
        hit_information = self.shared_grid_access.try_rotate_robot(self.robot, direction)
        if hit_information.hit_type == HitType.ERROR:
            if hit_information.inner_error is not None:
                raise hit_information.inner_error
            raise RuntimeError("try move robot failed")
        return hit_information

    def try_move_robot(self, direction: Direction) -> HitInformation:
        hit_information = self.shared_grid_access.try_move_robot(self.robot, direction)
        if hit_information.hit_type == HitType.ERROR:
            if hit_information.inner_error is not None:
                raise hit_information.inner_error
            raise RuntimeError("try move robot failed")
        elif hit_information.hit_type == HitType.NO_HIT:
            previous_coordinates = self.private_grid.get_coord_from_tile(self.robot)
            new_coordinates = previous_coordinates.create_neighbour_coordinate(direction)
            self.private_grid.move_tile_on_grid(self.robot, new_coordinates)
        return hit_information

    def wait_for_finish(self):
        self.process.join()

    def start_process(self):
        raise NotImplementedError()
