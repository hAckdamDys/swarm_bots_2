from swarm_bots.tiles.tile import Tile


class TileTakenException(RuntimeError):
    def __init__(self, tile: Tile, *args):
        super().__init__(*args)
        self.tile = tile

    def get_tile(self) -> Tile:
        return self.tile
