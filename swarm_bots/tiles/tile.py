import uuid
import enum


class TileType(enum.Enum):
    BLOCK = 0
    ROBOT = 1
    OBSTACLE = 2
    SOURCE = 3


class Tile:
    def __init__(self, tile_type: TileType):
        self.tile_type = tile_type
        self.id = hash(uuid.uuid4())

    def get_id(self) -> int:
        return self.id

    def get_type(self) -> TileType:
        return self.tile_type

    def __eq__(self, other):
        if not isinstance(other, Tile):
            return NotImplemented
        return self.id == other.id and self.tile_type == other.tile_type

    def __str__(self):
        return "{Tile: {id: "+str(self.id)+", tile_type: "+str(self.tile_type)+"}}"
