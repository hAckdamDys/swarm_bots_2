import time
from random import random

from swarm_bots.grid.base_grid import BaseGrid
from swarm_bots.grid.shared_grid_access import SharedGridAccess
from swarm_bots.robot_executors.hit_information import HitInformation, HitType
from swarm_bots.robot_executors.robot_shared_actions_executor import RobotSharedActionsExecutor
from swarm_bots.tiles.robot import Robot
from swarm_bots.utils.coordinates import Coordinates
from swarm_bots.utils.direction import Direction


class RobotSharedActionsExecutorWithSleep(RobotSharedActionsExecutor):
    # _wait_time_ticks = 10
    # _rotate_time_ticks = 2
    # _move_time_ticks = 4
    # _put_block_time_ticks = 3
    # _get_block_time_ticks = 3

    _wait_time_ticks = 1
    _rotate_time_ticks = 1
    _move_time_ticks = 1
    _put_block_time_ticks = 1
    _get_block_time_ticks = 1

    def __init__(self, robot: Robot, shared_grid_access: SharedGridAccess, private_grid: BaseGrid,
                 robot_coordinates: Coordinates, sleep_tick_seconds: float = 0.1):
        super().__init__(robot, shared_grid_access, private_grid, robot_coordinates)
        self.sleep_tick_seconds = sleep_tick_seconds
        self.total_ticks = 0

    def try_rotate_robot(self, direction: Direction) -> HitInformation:
        if self.robot.rotation == direction:
            return HitInformation(HitType.ROTATED, updated_robot=self.robot)
        hit_information = super().try_rotate_robot(direction)
        time.sleep(self._rotate_time_ticks * self.sleep_tick_seconds)
        self.total_ticks += self._rotate_time_ticks
        return hit_information

    def try_move_robot(self, direction: Direction) -> HitInformation:
        hit_information = super().try_move_robot(direction)
        time.sleep(self._move_time_ticks * self.sleep_tick_seconds)
        self.total_ticks += self._move_time_ticks
        return hit_information

    def try_put_block(self, direction: Direction) -> HitInformation:
        hit_information = super().try_put_block(direction)
        time.sleep(self._put_block_time_ticks * self.sleep_tick_seconds)
        self.total_ticks += self._put_block_time_ticks
        return hit_information

    def try_get_block(self, direction: Direction) -> HitInformation:
        hit_information = super().try_get_block(direction)
        time.sleep(self._get_block_time_ticks * self.sleep_tick_seconds)
        self.total_ticks += self._get_block_time_ticks
        return hit_information

    def wait_action(self):
        ticks = self._wait_time_ticks #* (0.9 + random() / 5)
        time.sleep(self.sleep_tick_seconds * ticks)
        self.total_ticks += ticks

    def finish_robot(self):
        print("ROBOT " + str(self.robot) + " finished in: " + str(self.total_ticks) + " ticks")
        super().finish_robot()
