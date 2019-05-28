from swarm_bots.tiles.tile import Tile, TileType
from swarm_bots.utils.direction import Direction


class Robot(Tile):
    def __init__(self, rotation: Direction):
        super().__init__(TileType.ROBOT)
        self.rotation = rotation

    def __eq__(self, other):
        if not isinstance(other, Robot):
            return NotImplemented
        return super().__eq__(other) and self.rotation == other.rotation
