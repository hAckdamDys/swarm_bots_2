import copy
from typing import Union

from swarm_bots.tiles.errors.has_inner_block_error import HasInnerBlockError
from swarm_bots.tiles.errors.impossible_robot_movement_error import ImpossibleRobotMovementError
from swarm_bots.tiles.errors.no_inner_block_error import NoInnerBlockError
from swarm_bots.tiles.tile import Tile, TileType
from swarm_bots.tiles.errors.wrong_block_get_direction import WrongBlockGetDirection
from swarm_bots.tiles.errors.wrong_block_put_direction import WrongBlockPutDirection
from swarm_bots.tiles.errors.wrong_block_type_error import WrongBlockTypeError
from swarm_bots.utils.direction import Direction


class Robot(Tile):
    def __init__(self, rotation: Direction):
        super().__init__(TileType.ROBOT)
        self.rotation = rotation
        self.inner_block: Union[Tile, None] = None

    def update_from_robot(self, robot: 'Robot'):
        self.rotation = robot.rotation
        self.inner_block = robot.inner_block

    def validate_movement_direction(self, direction: Direction):
        # robot can move forward or backwards so needs same axis
        if self.rotation.is_x_axis() != direction.is_x_axis():
            raise ImpossibleRobotMovementError(f"cannot move robot: {self} to direction {direction}")

    def validate_put_block_direction(self, direction: Direction):
        if self.inner_block is None:
            raise NoInnerBlockError("cannot get block from nothing")
        if self.rotation != direction:
            raise WrongBlockPutDirection("cannot put block not in front")

    def validate_get_block_direction(self, direction: Direction):
        if self.inner_block is not None:
            raise HasInnerBlockError("cannot get block if already has")
        if self.rotation != direction:
            raise WrongBlockGetDirection("cannot get block not in front")

    def rotate_to_direction(self, direction: Direction):
        self.rotation = direction

    def take_block(self, tile: Tile):
        if self.inner_block is not None:
            raise HasInnerBlockError("cannot get block if already has")
        if tile.get_type() != TileType.BLOCK:
            raise WrongBlockTypeError("robot can only take block type tiles")
        self.inner_block = tile

    def pop_block(self) -> Tile:
        if self.inner_block is None:
            raise NoInnerBlockError("cannot get block from nothing")
        block = self.inner_block
        self.inner_block = None
        return block

    def has_block(self) -> bool:
        if self.inner_block is None:
            return False
        return True

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

    def __copy__(self):
        return copy.deepcopy(self)

    def copy(self):
        return self.__copy__()
