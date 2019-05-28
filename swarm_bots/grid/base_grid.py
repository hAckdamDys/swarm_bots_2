import copy

import numpy as np

from grid.tile_already_added_exception import TileAlreadyAddedException
from swarm_bots.grid.tile_exists_exception import TileExistsException
from swarm_bots.tiles.tile import Tile
from swarm_bots.utils.coordinates import Coordinates


class BaseGrid:
    def __init__(self, width: int, height: int):
        self.height = height
        self.width = width
        # we need grid with indexes of objects we will store in some dict
        # 0 means there is no object
        self.tile_grid = np.zeros((self.width, self.height), np.longlong)
        self.tiles_from_index = dict()

    def add_new_tile(self, tile: Tile):
        if self.tiles_from_index.get(tile.get_id()) is not None:
            raise TileAlreadyAddedException("tile "+str(tile)+" already exists")
        self.tiles_from_index[tile.get_id()] = tile

    def get_tile_from_grid(self, coordinates: Coordinates) -> Tile:
        tile_index = self.tile_grid[coordinates.get_array_index()]
        return self.tiles_from_index.get(tile_index)

    def add_tile_to_grid(self, tile: Tile, coordinates: Coordinates):
        if self.tiles_from_index.get(tile.get_id()) is None:
            self.add_new_tile(tile)
        if self.get_tile_from_grid(coordinates) is not None:
            raise TileExistsException("there is already tile: (" + str(tile) + ") on "+str(coordinates))
        self.tile_grid[coordinates.get_array_index()] = tile.get_id()

    def __copy__(self):
        return copy.deepcopy(self)

    def copy(self):
        return self.__copy__()
