import time

from swarm_bots.grid.base_grid import BaseGrid
from swarm_bots.grid.shared_grid_access import SharedGridAccess
from swarm_bots.robot_executors.hit_information import HitInformation, HitType
from swarm_bots.robot_executors.robot_shared_actions_executor import RobotSharedActionsExecutor
from swarm_bots.tiles.robot import Robot
from swarm_bots.utils.coordinates import Coordinates
from swarm_bots.utils.direction import Direction


class RobotSharedActionsExecutorWithSleep(RobotSharedActionsExecutor):
    _wait_time_ticks = 10
    _rotate_time_ticks = 2
    _move_time_ticks = 4
    _put_block_time_ticks = 3
    _get_block_time_ticks = 3

    def __init__(self, robot: Robot, shared_grid_access: SharedGridAccess, private_grid: BaseGrid,
                 robot_coordinates: Coordinates, sleep_tick_seconds: float = 0.1):
        super().__init__(robot, shared_grid_access, private_grid, robot_coordinates)
        self.sleep_tick_seconds = sleep_tick_seconds

    def try_rotate_robot(self, direction: Direction) -> HitInformation:
        if self.robot.rotation == direction:
            return HitInformation(HitType.ROTATED, updated_robot=self.robot)
        hit_information = super().try_rotate_robot(direction)
        time.sleep(self._rotate_time_ticks * self.sleep_tick_seconds)
        return hit_information

    def try_move_robot(self, direction: Direction) -> HitInformation:
        hit_information = super().try_move_robot(direction)
        time.sleep(self._move_time_ticks * self.sleep_tick_seconds)
        return hit_information

    def try_put_block(self, direction: Direction) -> HitInformation:
        hit_information = super().try_put_block(direction)
        time.sleep(self._put_block_time_ticks * self.sleep_tick_seconds)
        return hit_information

    def try_get_block(self, direction: Direction) -> HitInformation:
        hit_information = super().try_get_block(direction)
        time.sleep(self._get_block_time_ticks * self.sleep_tick_seconds)
        return hit_information

    def wait_action(self):
        time.sleep(self._wait_time_ticks * self.sleep_tick_seconds)
