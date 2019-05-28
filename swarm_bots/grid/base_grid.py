import copy

import numpy as np

from swarm_bots.grid.add_duplicate_tile_error import AddDuplicateTileError
from swarm_bots.grid.tile_already_added_exception import TileAlreadyAddedException
from swarm_bots.grid.tile_exists_exception import TileTakenException
from swarm_bots.grid.tile_not_exists_exception import TileNotExistsException
from swarm_bots.tiles.tile import Tile
from swarm_bots.utils.coordinates import Coordinates


class BaseGrid:
    empty_tile_id = 0

    def __init__(self, width: int, height: int):
        self.height = height
        self.width = width
        # we need grid with indexes of objects we will store in some dict
        # 0 means there is no object
        self.tile_grid = np.zeros((self.width, self.height), np.longlong)
        self.tiles_from_index = dict()
        self.coordinates_from_index = dict()

    def add_new_tile(self, tile: Tile):
        if self.tiles_from_index.get(tile.get_id()) is not None:
            raise TileAlreadyAddedException("tile "+str(tile)+" already exists")
        self.tiles_from_index[tile.get_id()] = tile

    def get_tile_from_grid(self, coordinates: Coordinates) -> Tile:
        tile_index = self.tile_grid[coordinates.get_array_index()]
        tile = self.tiles_from_index.get(tile_index)
        print("tile on coord: ", coordinates, "was", tile)
        return self.tiles_from_index.get(tile_index)

    def add_tile_to_grid(self, tile: Tile, coordinates: Coordinates):
        if self.tiles_from_index.get(tile.get_id()) is None:
            self.add_new_tile(tile)
        else:
            tile_coordinates = self.coordinates_from_index.get(tile.get_id())
            if tile_coordinates is not None:
                raise AddDuplicateTileError("tile "+str(tile)+" already exists on "+str(tile_coordinates))
        if self.get_tile_from_grid(coordinates) is not None:
            raise TileTakenException("there is already tile: (" + str(tile) + ") on " + str(coordinates))
        self.tile_grid[coordinates.get_array_index()] = tile.get_id()
        self.coordinates_from_index[tile.get_id()] = coordinates

    def move_tile_on_grid(self, tile: Tile, coordinates: Coordinates):
        if self.tiles_from_index.get(tile.get_id()) is None:
            raise TileNotExistsException("tile: (" + str(tile) + ") was not added")
        if self.get_tile_from_grid(coordinates) is not None:
            raise TileTakenException("there is already tile: (" + str(tile) + ") on " + str(coordinates))
        previous_coordinates = self.coordinates_from_index.get(tile.get_id())
        if previous_coordinates is None:
            raise TileNotExistsException("tile: (" + str(tile) + ") did not have coordinates")
        self.coordinates_from_index[tile.get_id()] = coordinates
        self.tile_grid[previous_coordinates.get_array_index()] = BaseGrid.empty_tile_id
        self.tile_grid[coordinates.get_array_index()] = tile.get_id()

    def __copy__(self):
        return copy.deepcopy(self)

    def copy(self):
        return self.__copy__()
