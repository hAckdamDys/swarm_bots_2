import copy
from typing import Union, Dict

import numpy as np

from swarm_bots.grid.errors.add_duplicate_tile_error import AddDuplicateTileError
from swarm_bots.grid.errors.out_of_bound_coordinates_error import OutOfBoundCoordinatesError
from swarm_bots.grid.errors.tile_already_added_exception import TileAlreadyAddedException
from swarm_bots.grid.errors.tile_not_source_error import TileNotSourceError
from swarm_bots.grid.errors.tile_taken_exception import TileTakenException
from swarm_bots.grid.errors.tile_not_exists_exception import TileNotExistsException
from swarm_bots.tiles.tile import Tile, TileType
from swarm_bots.utils.coordinates import Coordinates


class BaseGrid:
    empty_tile_id = 0

    def __init__(self, width: int, height: int):
        self.height = height
        self.width = width
        # we need grid with indexes of objects we will store in some dict
        # 0 means there is no object
        self.tile_grid = np.zeros((self.width, self.height), np.longlong)
        self.tiles_from_index: Dict[int, Tile] = dict()
        self.coordinates_from_index: Dict[int, Coordinates] = dict()
        # block tile grid for checking goal building
        self.block_tile_grid = np.zeros((self.width, self.height), bool)

    def add_new_tile(self, tile: Tile):
        if self.tiles_from_index.get(tile.get_id()) is not None:
            raise TileAlreadyAddedException("tile "+str(tile)+" already exists")
        self.tiles_from_index[tile.get_id()] = tile

    def get_tile_from_grid(self, coordinates: Coordinates) -> Tile:
        try:
            tile_index = self.tile_grid[coordinates.get_array_index()]
        except IndexError as e:
            raise OutOfBoundCoordinatesError(e.args)
        return self._get_tile_from_index(tile_index)

    def get_coord_from_tile(self, tile: Tile) -> Coordinates:
        coordinates = self.coordinates_from_index.get(tile.get_id())
        if coordinates is None:
            raise TileNotExistsException("tile: (" + str(tile) + ") was not added")
        # print("coord from tile: ", tile, "was", coordinates)
        return coordinates.copy()

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
        if tile.get_type() == TileType.BLOCK:
            self.block_tile_grid[coordinates.get_array_index()] = True

    def update_tile(self, tile: Tile):
        self.tiles_from_index[tile.get_id()] = tile

    def move_tile_on_grid(self, tile: Tile, coordinates: Coordinates):
        if self.tiles_from_index.get(tile.get_id()) is None:
            raise TileNotExistsException("tile: (" + str(tile) + ") was not added")
        tile_on_coordinates = self.get_tile_from_grid(coordinates)
        if tile_on_coordinates is not None:
            if tile_on_coordinates.id != tile.id:
                raise TileTakenException(tile_on_coordinates,
                                         f"there is already tile: ({str(tile)}) on {str(coordinates)}")
            # else it means we move to same tile we were on
        previous_coordinates = self.coordinates_from_index.get(tile.get_id())
        if previous_coordinates is None:
            raise TileNotExistsException("tile: (" + str(tile) + ") did not have coordinates")
        self.coordinates_from_index[tile.get_id()] = coordinates.copy()
        self.tile_grid[previous_coordinates.get_array_index()] = BaseGrid.empty_tile_id
        self.tile_grid[coordinates.get_array_index()] = tile.get_id()
        self.tiles_from_index[tile.get_id()] = tile
        if tile.get_type() == TileType.BLOCK:
            self.block_tile_grid[previous_coordinates.get_array_index()] = False
            self.block_tile_grid[coordinates.get_array_index()] = True

    def remove_tile_from_grid(self, coordinates: Coordinates):
        self.pop_tile_from_grid(coordinates)

    def pop_tile_from_grid(self, coordinates: Coordinates) -> Union[Tile, None]:
        tile_index = self.tile_grid[coordinates.get_array_index()]
        if tile_index is None:
            return None
        self.coordinates_from_index.pop(tile_index)
        self.tile_grid[coordinates.get_array_index()] = BaseGrid.empty_tile_id
        tile = self._get_tile_from_index(tile_index)
        if tile.get_type() == TileType.BLOCK:
            self.block_tile_grid[coordinates.get_array_index()] = False
        return tile

    def get_tile_from_source(self, coordinates: Coordinates) -> Tile:
        try:
            tile_index = self.tile_grid[coordinates.get_array_index()]
        except IndexError as e:
            raise OutOfBoundCoordinatesError(e.args)
        tile = self._get_tile_from_index(tile_index)
        if tile is None:
            raise TileNotExistsException("tile index: (" + str(tile_index) + ") did not have tile")
        if tile.get_type() != TileType.SOURCE:
            raise TileNotSourceError(tile, "tile: (" + str(tile) + ") is not source")
        return Tile(TileType.BLOCK)

    def get_block_grid(self):
        return self.block_tile_grid

    def _get_tile_from_index(self, tile_index: int) -> Tile:
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
