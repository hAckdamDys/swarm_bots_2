from enum import Enum

from swarm_bots.tiles.robot import Robot
from swarm_bots.tiles.tile import TileType


class HitType(Enum):
    ROBOT = 0
    BLOCK = 1
    OBSTACLE = 2
    NO_HIT = 3
    ROTATED = 4
    PLACED_BLOCK = 5
    GOT_BLOCK = 6
    ERROR = 7

    @staticmethod
    def from_tile_type(tile_type: TileType) -> 'HitType':
        if tile_type == TileType.BLOCK:
            return HitType.BLOCK
        elif tile_type == TileType.ROBOT:
            return HitType.ROBOT
        elif tile_type == TileType.OBSTACLE:
            return HitType.OBSTACLE
        return HitType.ERROR


class HitInformation:
    def __init__(self, hit_type: HitType, inner_error: RuntimeError = None, updated_robot: Robot = None):
        self.inner_error = inner_error
        self.hit_type = hit_type
        self.updated_robot = updated_robot
