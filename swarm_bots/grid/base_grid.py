import copy

import numpy as np

from swarm_bots.grid.tile_exists_exception import TileExistsException
from swarm_bots.tiles.tile import Tile
from swarm_bots.utils.coordinates import Coordinates


class BaseGrid:
    def __init__(self, width: int, height: int):
        self.height = height
        self.width = width
        # we need grid with indexes of objects we will store in some dict
        # 0 means there is no object
        self.tile_grid = np.zeros((self.width, self.height), int)
        self.tiles_from_index = dict()
        self.index_from_tiles = dict()
        self.last_tile_index = 0

    def add_new_tile(self, tile: Tile):
        if self.index_from_tiles.get(tile.get_id()) is not None:
            raise ValueError("tile "+str(tile)+" already exists")
        self.last_tile_index += 1
        self.tiles_from_index[self.last_tile_index] = tile
        self.index_from_tiles[tile.get_id()] = self.last_tile_index

    def get_tile_from_grid(self, coordinates: Coordinates) -> Tile:
        tile_index = self.tile_grid[coordinates.get_array_index()]
        return self.tiles_from_index.get(tile_index)

    def add_tile_to_grid(self, tile: Tile, coordinates: Coordinates):
        if self.get_tile_from_grid(coordinates) is not None:
            raise TileExistsException("there is already tile: (" + str(tile) + ") on "+str(coordinates))
        self.tile_grid[coordinates.get_array_index()] = tile.get_id()

    def __copy__(self):
        return copy.deepcopy(self)

    def copy(self):
        return self.__copy__()
