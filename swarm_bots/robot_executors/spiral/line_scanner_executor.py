from typing import Union

from swarm_bots.robot_executors.hit_information import HitType
from swarm_bots.robot_executors.robot_shared_actions_executor import RobotSharedActionsExecutor
from swarm_bots.robot_executors.spiral.line_to_middle import LineToMiddle
from swarm_bots.tiles.tile import TileType, Tile
from swarm_bots.utils.coordinates import Coordinates
from swarm_bots.utils.direction import Direction


class LineScannerExecutor:
    def __init__(self, shared_actions_executor: RobotSharedActionsExecutor):
        self.shared_actions_executor = shared_actions_executor
        self.private_grid = shared_actions_executor.private_grid
        self.robot_coordinates = shared_actions_executor.robot_coordinates
        self.robot = shared_actions_executor.robot

    def _go_back_to_start_line(self, from_block_direction: Direction, line_start_position: Coordinates):
        if self.robot_coordinates == line_start_position:
            return
        if self.robot.rotation != from_block_direction:
            self.shared_actions_executor.try_rotate_robot(from_block_direction)
        while self.robot_coordinates != line_start_position:
            hit_information = self.shared_actions_executor.try_move_robot(from_block_direction)
            if hit_information.hit_type == HitType.OBSTACLE:
                raise ValueError("scanner cannot work with obstacles")
            elif hit_information.hit_type == HitType.BLOCK:
                raise ValueError("scanner should always visit previously placed block " +
                                 "so we cannot hit block while go back")
            elif hit_information.hit_type == HitType.ROBOT:
                # if we hit robot then he will know we put block
                self.shared_actions_executor.wait_action()

    def _put_block_on_map(self, line: LineToMiddle) -> Coordinates:
        placed_block_position = line.place_block()
        self.private_grid.add_tile_to_grid(Tile(TileType.BLOCK), placed_block_position)
        return placed_block_position

    def _move_to_block_from_inside(self,
                                   from_block_direction: Direction,
                                   before_block_coordinates: Coordinates):
        while self.robot_coordinates != before_block_coordinates:
            hit_information = self.shared_actions_executor.try_move_robot(from_block_direction)
            if hit_information.hit_type == HitType.OBSTACLE:
                raise ValueError("scanner cannot work with obstacles")
            elif hit_information.hit_type == HitType.BLOCK:
                raise ValueError("scanner should always visit previously placed block " +
                                 "so we cannot hit block while go back")
            elif hit_information.hit_type == HitType.ROBOT:
                # the other robot will leave job to us
                self.shared_actions_executor.wait_action()

    def _move_to_block_towards_inside(self,
                                      to_block_direction: Direction,
                                      from_block_direction: Direction,
                                      line: LineToMiddle,
                                      before_block_coordinates: Coordinates):
        # returns True when finished but False when still need to add block
        while self.robot_coordinates != before_block_coordinates:
            hit_information = self.shared_actions_executor.try_move_robot(to_block_direction)
            if hit_information.hit_type == HitType.OBSTACLE:
                raise ValueError("scanner cannot work with obstacles")
            elif hit_information.hit_type == HitType.BLOCK:
                placed_block_position: Union[None, Coordinates] = None
                discovered_block_position = self.robot_coordinates.create_neighbour_coordinate(to_block_direction)
                while placed_block_position != discovered_block_position:
                    placed_block_position = self._put_block_on_map(line)
                if line.is_finished():
                    self._go_back_to_start_line(from_block_direction, line.start_coordinates)
                    return
                self.shared_actions_executor.try_rotate_robot(from_block_direction)
                before_block_coordinates = line.get_next_block_position(). \
                    create_neighbour_coordinate(from_block_direction)
                self._move_to_block_from_inside(from_block_direction, before_block_coordinates)
                return
            elif hit_information.hit_type == HitType.ROBOT:
                # if we hit robot then he already put at least one new block and we continue with block elsewhere
                self._put_block_on_map(line)
                self._go_back_to_start_line(from_block_direction, line.start_coordinates)
                return
        return

    # scan line while changing line and all inner variables
    def scan_line(self, line: LineToMiddle):
        if line.is_finished():
            raise ValueError("cannot scan finished line")
        line_start_coordinates = line.start_coordinates.copy()
        if self.robot_coordinates != line_start_coordinates:
            raise ValueError("scanner assume that robot is at line start")
        if not self.robot.has_block():
            raise ValueError("scanner assume that robot has block")
        to_block_direction = line.get_to_block_direction()
        from_block_direction = line.get_from_block_direction()
        before_block_coordinates = line.get_next_block_position().create_neighbour_coordinate(from_block_direction)
        if self.robot.rotation != to_block_direction:
            self.shared_actions_executor.try_rotate_robot(to_block_direction)
        self._move_to_block_towards_inside(to_block_direction, from_block_direction, line, before_block_coordinates)
        # we need to rotate in case we were not
        if self.robot.rotation != to_block_direction:
            self.shared_actions_executor.try_rotate_robot(to_block_direction)
        # if we are just before position to put block and correctly rotated
        hit_information = self.shared_actions_executor.try_put_block(to_block_direction)
        line.place_block()
        if hit_information.hit_type == HitType.PLACED_BLOCK:
            self._go_back_to_start_line(from_block_direction, line_start_coordinates)
        elif hit_information.hit_type == HitType.BLOCK:
            # when another robot already put this block
            self._put_block_on_map(line)
            self._go_back_to_start_line(from_block_direction, line_start_coordinates)
        else:
            raise ValueError("different tile type cannot be on position where block will be added")
