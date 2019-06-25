from unittest import TestCase

from swarm_bots.grid.base_grid import BaseGrid
from swarm_bots.grid.errors.tile_already_added_exception import TileAlreadyAddedException
from swarm_bots.grid.errors.tile_taken_exception import TileTakenException
from swarm_bots.tiles.tile import Tile, TileType
from swarm_bots.utils.coordinates import Coordinates
from swarm_bots.utils.direction import Direction


class TestBaseGrid(TestCase):
    def setUp(self):
        self.example_width = 5
        self.example_height = 5
        self.base_grid_example = BaseGrid(
            width=self.example_width,
            height=self.example_height
        )
        print("setup")
        self.block_tile = Tile(TileType.BLOCK)
        self.obstacle_tile = Tile(TileType.OBSTACLE)
        self.block_tile_coordinates = Coordinates(1, 1)
        self.obstacle_tile_coordinates = Coordinates(3, 3)

    def test_add_new_tile_when_it_exists(self):
        self.base_grid_example.add_new_tile(self.block_tile)
        with self.assertRaises(TileAlreadyAddedException):
            self.base_grid_example.add_new_tile(self.block_tile)

    def test_add_get_tile_from_grid(self):
        self.base_grid_example.add_new_tile(self.block_tile)
        self.base_grid_example.add_new_tile(self.obstacle_tile)
        self.base_grid_example.add_tile_to_grid(
            tile=self.block_tile,
            coordinates=self.block_tile_coordinates
        )
        tile_from_block_tile_coordinates = self.base_grid_example.get_tile_from_grid(
            coordinates=self.block_tile_coordinates
        )
        assert tile_from_block_tile_coordinates == self.block_tile
        with self.assertRaises(TileTakenException):
            self.base_grid_example.add_tile_to_grid(
                tile=self.obstacle_tile,
                coordinates=self.block_tile_coordinates
            )
        self.base_grid_example.add_tile_to_grid(
            tile=self.obstacle_tile,
            coordinates=self.obstacle_tile_coordinates
        )
        tile_from_obstacle_tile_coordinates = self.base_grid_example.get_tile_from_grid(
            coordinates=self.obstacle_tile_coordinates
        )
        assert tile_from_obstacle_tile_coordinates == self.obstacle_tile

    def test_copy(self):
        self.test_add_get_tile_from_grid()
        grid_copy = self.base_grid_example.copy()
        tile_from_block_tile_coordinates = grid_copy.get_tile_from_grid(
            coordinates=self.block_tile_coordinates
        )
        print("copied", tile_from_block_tile_coordinates)
        print("not copied", self.block_tile)
        assert tile_from_block_tile_coordinates == self.block_tile
        new_block_coordinates = self.block_tile_coordinates.create_neighbour_coordinate(Direction.UP)
        print("new block coordinate", new_block_coordinates)
        grid_copy.move_tile_on_grid(self.block_tile, new_block_coordinates)
        assert grid_copy.get_tile_from_grid(new_block_coordinates) == self.block_tile
        assert grid_copy.get_tile_from_grid(self.block_tile_coordinates) is None
        assert self.base_grid_example.get_tile_from_grid(new_block_coordinates) != self.block_tile
        assert self.base_grid_example.get_tile_from_grid(self.block_tile_coordinates) == self.block_tile
