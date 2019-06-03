from enum import Enum

from swarm_bots.tiles.tile import TileType
from swarm_bots.utils.coordinates import Coordinates


class HitType(Enum):
    OUT_OF_BOUND = 0
    ROBOT = 1
    BLOCK = 2
    OBSTACLE = 3
    NO_HIT = 4
    ERROR = 5

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
