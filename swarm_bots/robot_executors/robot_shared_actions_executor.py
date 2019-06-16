import time

from swarm_bots.grid.base_grid import BaseGrid
from swarm_bots.grid.shared_grid_access import SharedGridAccess
from swarm_bots.robot_executors.hit_information import HitInformation, HitType
from swarm_bots.tiles.robot import Robot
from swarm_bots.tiles.tile import Tile, TileType
from swarm_bots.utils.coordinates import Coordinates
from swarm_bots.utils.direction import Direction


class RobotSharedActionsExecutor:
    _wait_time_ticks = 1

    def __init__(self,
                 robot: Robot,
                 shared_grid_access: SharedGridAccess,
                 private_grid: BaseGrid,
                 robot_coordinates: Coordinates):
        self.put_blocks = 0
        self.robot_coordinates = robot_coordinates
        self.robot = robot
        self.shared_grid_access = shared_grid_access
        self.private_grid = private_grid

    @staticmethod
    def _hit_error_validator(hit_information: HitInformation):
        if hit_information.hit_type == HitType.ERROR:
            if hit_information.inner_error is not None:
                raise hit_information.inner_error
            raise RuntimeError("robot action failed with unknown error")

    def try_rotate_robot(self, direction: Direction) -> HitInformation:
        if self.robot.rotation == direction:
            return HitInformation(HitType.ROTATED, updated_robot=self.robot)
        hit_information = self.shared_grid_access.try_rotate_robot(self.robot, direction)
        RobotSharedActionsExecutor._hit_error_validator(hit_information)
        if hit_information.hit_type == HitType.ROTATED:
            self.private_grid.update_tile(self.robot)
            self.robot.update_from_robot(hit_information.updated_robot)
        return hit_information

    def _get_robot_neighbour_coordinates(self, direction: Direction) -> Coordinates:
        new_coordinates = self.robot_coordinates.create_neighbour_coordinate(direction)
        return new_coordinates

    def try_move_robot(self, direction: Direction) -> HitInformation:
        hit_information = self.shared_grid_access.try_move_robot(self.robot, direction)
        RobotSharedActionsExecutor._hit_error_validator(hit_information)
        if hit_information.hit_type == HitType.NO_HIT:
            self.robot_coordinates.move_to_neighbour(direction)
            self.private_grid.move_tile_on_grid(self.robot, self.robot_coordinates)
            self.robot.update_from_robot(hit_information.updated_robot)
        elif hit_information.hit_type == HitType.BLOCK:
            self.private_grid.add_tile_to_grid(
                Tile(TileType.BLOCK), self._get_robot_neighbour_coordinates(direction))
        elif hit_information.hit_type == HitType.OBSTACLE:
            self.private_grid.add_tile_to_grid(
                Tile(TileType.OBSTACLE), self._get_robot_neighbour_coordinates(direction))
        return hit_information

    def try_put_block(self, direction: Direction) -> HitInformation:
        hit_information = self.shared_grid_access.try_put_block(self.robot, direction)
        RobotSharedActionsExecutor._hit_error_validator(hit_information)
        if hit_information.hit_type == HitType.PLACED_BLOCK:
            self.private_grid.add_tile_to_grid(self.robot.pop_block(), self._get_robot_neighbour_coordinates(direction))
            self.put_blocks += 1
            # no need to update robot we already popped block
        elif hit_information.hit_type == HitType.BLOCK:
            try:
                self.private_grid.add_tile_to_grid(
                    Tile(TileType.BLOCK), self._get_robot_neighbour_coordinates(direction))
            except Exception as e:
                print(f"WARNING {e}")
        elif hit_information.hit_type == HitType.OBSTACLE:
            self.private_grid.add_tile_to_grid(
                Tile(TileType.OBSTACLE), self._get_robot_neighbour_coordinates(direction))
        return hit_information

    def try_get_block(self, direction: Direction) -> HitInformation:
        hit_information = self.shared_grid_access.try_get_block(self.robot, direction)
        RobotSharedActionsExecutor._hit_error_validator(hit_information)
        if hit_information.hit_type == HitType.GOT_BLOCK:
            self.robot.update_from_robot(hit_information.updated_robot)
            block_coordinates = self.robot_coordinates.create_neighbour_coordinate(direction)
            if self.private_grid.get_tile_from_grid(block_coordinates).get_type() != TileType.SOURCE:
                self.private_grid.pop_tile_from_grid(block_coordinates)
                # if robot took block then his total is -1
                self.put_blocks -= 1
        elif hit_information.hit_type == HitType.BLOCK:
            self.private_grid.add_tile_to_grid(
                Tile(TileType.BLOCK), self._get_robot_neighbour_coordinates(direction))
        elif hit_information.hit_type == HitType.OBSTACLE:
            self.private_grid.add_tile_to_grid(
                Tile(TileType.OBSTACLE), self._get_robot_neighbour_coordinates(direction))
        return hit_information

    @staticmethod
    def wait_action():
        # TODO: maybe implement maximum tries after which raise error
        time.sleep(RobotSharedActionsExecutor._wait_time_ticks)
