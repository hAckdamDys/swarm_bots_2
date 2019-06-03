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
        # print("tile on coord: ", coordinates, "was", tile)
        return self.tiles_from_index.get(tile_index)

    def get_coord_from_tile(self, tile: Tile) -> Coordinates:
        coordinates = self.coordinates_from_index.get(tile.get_id())
        if coordinates is None:
            raise TileNotExistsException("tile: (" + str(tile) + ") was not added")
        # print("coord from tile: ", tile, "was", coordinates)
        return coordinates

    def add_tile_to_grid(self, tile: Tile, coordinates: Coordinates):
        if self.tiles_from_index.get(tile.get_id()) is None:
            self.add_new_tile(tile)
        else:
            tile_coordinates = self.coordinates_from_index.get(tile.get_id())
            if tile_coordinates is not None:
                raise AddDuplicateTileError("tile "+str(tile)+" already exists on "+str(tile_coordinates))
        tile_on_coordinates = self.get_tile_from_grid(coordinates)
        if tile_on_coordinates is not None:
            raise TileTakenException(tile_on_coordinates, f"there is already tile: ({str(tile)}) on {str(coordinates)}")
        self.tile_grid[coordinates.get_array_index()] = tile.get_id()
        self.coordinates_from_index[tile.get_id()] = coordinates

    def move_tile_on_grid(self, tile: Tile, coordinates: Coordinates):
        if self.tiles_from_index.get(tile.get_id()) is None:
            raise TileNotExistsException("tile: (" + str(tile) + ") was not added")
        tile_on_coordinates = self.get_tile_from_grid(coordinates)
        if tile_on_coordinates is not None:
            if tile_on_coordinates != tile:
                print("tile on coordinates", tile_on_coordinates)
                print("tile not on coordinates", tile)
                raise TileTakenException(tile_on_coordinates, f"there is already tile: ({str(tile)}) on {str(coordinates)}")
            # else it means we move to same tile we were on
        previous_coordinates = self.coordinates_from_index.get(tile.get_id())
        if previous_coordinates is None:
            raise TileNotExistsException("tile: (" + str(tile) + ") did not have coordinates")
        self.coordinates_from_index[tile.get_id()] = coordinates
        self.tile_grid[previous_coordinates.get_array_index()] = BaseGrid.empty_tile_id
        self.tile_grid[coordinates.get_array_index()] = tile.get_id()
        self.tiles_from_index[tile.get_id()] = tile
        print("aba", self)

    def remove_tile_from_grid(self, coordinates: Coordinates):
        tile_index = self.tile_grid[coordinates.get_array_index()]
        if tile_index is None:
            return
        self.coordinates_from_index.pop(tile_index)
        self.tile_grid[coordinates.get_array_index()] = BaseGrid.empty_tile_id

    def pop_tile_from_grid(self, coordinates: Coordinates):
        tile_index = self.tile_grid[coordinates.get_array_index()]
        if tile_index is None:
            return
        self.coordinates_from_index.pop(tile_index)
        self.tile_grid[coordinates.get_array_index()] = BaseGrid.empty_tile_id
        return self.tiles_from_index.get(tile_index)

    def __copy__(self):
        return copy.deepcopy(self)

    def copy(self):
        return self.__copy__()

    def __str__(self):
        full_str = "BaseGrid: {\n"
        for tile_index, tile in self.tiles_from_index.items():
            coordinate = self.get_coord_from_tile(tile)
            full_str += f"{coordinate}:{tile}\n"
        return full_str+"\n}"
