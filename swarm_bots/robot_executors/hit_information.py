from enum import Enum

from swarm_bots.tiles.tile import TileType


class HitType(Enum):
    ROBOT = 0
    BLOCK = 1
    OBSTACLE = 2
    NO_HIT = 3
    ERROR = 4

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
    def __init__(self, hit_type: HitType, inner_error: RuntimeError = None):
        self.inner_error = inner_error
        self.hit_type = hit_type
        self.new_coordinates = None
