import abc
from multiprocessing import Process

from swarm_bots.goal.goal_building import GoalBuilding
from swarm_bots.grid.shared_grid_access import SharedGridAccess
from swarm_bots.robot_executors.hit_information import HitInformation, HitType
from swarm_bots.tiles.robot import Robot
from swarm_bots.tiles.tile import TileType, Tile
from swarm_bots.utils.coordinates import Coordinates
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

    @staticmethod
    def _hit_error_validator(hit_information: HitInformation):
        if hit_information.hit_type == HitType.ERROR:
            if hit_information.inner_error is not None:
                raise hit_information.inner_error
            raise RuntimeError("try move robot failed with unknown error")

    def try_rotate_robot(self, direction: Direction) -> HitInformation:
        hit_information = self.shared_grid_access.try_rotate_robot(self.robot, direction)
        RobotExecutor._hit_error_validator(hit_information)
        if hit_information.hit_type == HitType.NO_HIT:
            self.private_grid.update_tile(self.robot)
            self.robot = hit_information.updated_robot
        return hit_information

    def _get_robot_neighbour_coordinates(self, direction: Direction) -> Coordinates:
        previous_coordinates = self.private_grid.get_coord_from_tile(self.robot)
        new_coordinates = previous_coordinates.create_neighbour_coordinate(direction)
        return new_coordinates

    def try_move_robot(self, direction: Direction) -> HitInformation:
        hit_information = self.shared_grid_access.try_move_robot(self.robot, direction)
        RobotExecutor._hit_error_validator(hit_information)
        if hit_information.hit_type == HitType.NO_HIT:
            self.private_grid.move_tile_on_grid(self.robot, self._get_robot_neighbour_coordinates(direction))
            self.robot = hit_information.updated_robot
        elif hit_information.hit_type == HitType.BLOCK:
            self.private_grid.add_tile_to_grid(
                Tile(TileType.BLOCK), self._get_robot_neighbour_coordinates(direction))
        elif hit_information.hit_type == HitType.OBSTACLE:
            self.private_grid.add_tile_to_grid(
                Tile(TileType.OBSTACLE), self._get_robot_neighbour_coordinates(direction))
        return hit_information

    def try_put_block(self, direction: Direction) -> HitInformation:
        hit_information = self.shared_grid_access.try_put_block(self.robot, direction)
        RobotExecutor._hit_error_validator(hit_information)
        if hit_information.hit_type == HitType.PLACED_BLOCK:
            self.private_grid.add_tile_to_grid(self.robot.pop_block(), self._get_robot_neighbour_coordinates(direction))
            # no need to update robot we already popped block
        elif hit_information.hit_type == HitType.BLOCK:
            self.private_grid.add_tile_to_grid(
                Tile(TileType.BLOCK), self._get_robot_neighbour_coordinates(direction))
        elif hit_information.hit_type == HitType.OBSTACLE:
            self.private_grid.add_tile_to_grid(
                Tile(TileType.OBSTACLE), self._get_robot_neighbour_coordinates(direction))
        return hit_information

    def wait_for_finish(self):
        self.process.join()

    def start_process(self):
        raise NotImplementedError()
