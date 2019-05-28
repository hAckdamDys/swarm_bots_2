import uuid
import enum


class TileType(enum.Enum):
    BLOCK = 0
    ROBOT = 1
    OBSTACLE = 2


class Tile:
    def __init__(self, tile_type: TileType):
        self.tile_type = tile_type
        self.id = hash(uuid.uuid4())

    def get_id(self) -> int:
        return self.id

    def get_type(self) -> TileType:
        return self.tile_type
