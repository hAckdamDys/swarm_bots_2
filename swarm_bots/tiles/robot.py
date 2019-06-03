from typing import Union

from swarm_bots.tiles.impossible_robot_movement_error import ImpossibleRobotMovementError
from swarm_bots.tiles.no_inner_block_error import NoInnerBlockError
from swarm_bots.tiles.tile import Tile, TileType
from swarm_bots.tiles.wrong_block_type_error import WrongBlockTypeError
from swarm_bots.utils.direction import Direction


class Robot(Tile):
    def __init__(self, rotation: Direction):
        super().__init__(TileType.ROBOT)
        self.rotation = rotation
        self.inner_block: Union[Tile, None] = None

    def validate_movement_direction(self, direction: Direction):
        # robot can move forward or backwards so needs same axis
        if self.rotation.is_x_axis() != direction.is_x_axis():
            raise ImpossibleRobotMovementError(f"cannot move robot: {self} to direction {direction}")

    def rotate_to_direction(self, direction: Direction):
        self.rotation = direction

    def take_block(self, tile: Tile):
        if tile.get_type() != TileType.BLOCK:
            raise WrongBlockTypeError("robot can only take block type tiles")
        self.inner_block = tile

    def pop_block(self) -> Tile:
        if self.inner_block is None:
            raise NoInnerBlockError("cannot get block from nothing")
        block = self.inner_block
        self.inner_block = None
        return block

    def __eq__(self, other) -> bool:
        if not isinstance(other, Robot):
            return NotImplemented
        return super().__eq__(other) and self.rotation == other.rotation and self.inner_block == other.inner_block

    def __str__(self) -> str:
        super_str = super().__str__()
        super_str_end = super_str[-2:]
        super_str = super_str[:-2]
        super_str += f", rotation: {self.rotation}"
        super_str += f", inner_block: {self.inner_block}"
        return super_str + super_str_end
