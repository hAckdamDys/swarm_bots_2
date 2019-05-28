from unittest import TestCase

from grid.base_grid import BaseGrid
from grid.tile_already_added_exception import TileAlreadyAddedException
from grid.tile_exists_exception import TileExistsException
from tiles.tile import Tile, TileType
from utils.coordinates import Coordinates


class TestBaseGrid(TestCase):
    def setUp(self):
        self.example_width = 5
        self.example_height = 5
        self.base_grid_example = BaseGrid(
            width=self.example_width,
            height=self.example_height
        )
        print("setup")

    def test_add_new_tile_when_it_exists(self):
        block_tile = Tile(TileType.BLOCK)
        self.base_grid_example.add_new_tile(block_tile)
        with self.assertRaises(TileAlreadyAddedException):
            self.base_grid_example.add_new_tile(block_tile)

    def test_add_get_tile_from_grid(self):
        block_tile = Tile(TileType.BLOCK)
        obstacle_tile = Tile(TileType.OBSTACLE)
        self.base_grid_example.add_new_tile(block_tile)
        self.base_grid_example.add_new_tile(obstacle_tile)
        block_tile_coordinates = Coordinates(1, 1)
        self.base_grid_example.add_tile_to_grid(
            tile=block_tile,
            coordinates=block_tile_coordinates
        )
        tile_from_block_tile_coordinates = self.base_grid_example.get_tile_from_grid(
            coordinates=block_tile_coordinates
        )
        assert tile_from_block_tile_coordinates == block_tile
        with self.assertRaises(TileExistsException):
            self.base_grid_example.add_tile_to_grid(
                tile=obstacle_tile,
                coordinates=block_tile_coordinates
            )
        obstacle_tile_coordinates = Coordinates(1, 2)
        self.base_grid_example.add_tile_to_grid(
            tile=obstacle_tile,
            coordinates=obstacle_tile_coordinates
        )
        tile_from_obstacle_tile_coordinates = self.base_grid_example.get_tile_from_grid(
            coordinates=obstacle_tile_coordinates
        )
        assert tile_from_obstacle_tile_coordinates == obstacle_tile

    def test_copy(self):
        self.fail()
