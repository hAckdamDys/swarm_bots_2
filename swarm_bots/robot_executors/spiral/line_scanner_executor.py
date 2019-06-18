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
        try:
            self.private_grid.add_tile_to_grid(Tile(TileType.BLOCK), placed_block_position)
        except Exception as e:
            print(f"WARNING: {e}")
        return placed_block_position

    def _move_to_block_from_inside(self,
                                   from_block_direction: Direction,
                                   before_block_coordinates: Coordinates):
        print(f"robot: {self.robot}, move_to_block_from_inside {before_block_coordinates}")
        hit_information = self.shared_actions_executor.try_move_robot(from_block_direction)
        while self.robot_coordinates != before_block_coordinates:
            if hit_information.hit_type == HitType.OBSTACLE:
                raise ValueError("scanner cannot work with obstacles")
            elif hit_information.hit_type == HitType.BLOCK:
                raise ValueError("scanner should always visit previously placed block " +
                                 "so we cannot hit block while go back")
            elif hit_information.hit_type == HitType.ROBOT:
                # the other robot will leave job to us
                self.shared_actions_executor.wait_action()

    def _move_to_block_towards_inside(self, line: LineToMiddle) -> bool:
        to_block_direction = line.get_to_block_direction()
        from_block_direction = line.get_from_block_direction()
        before_block_coordinates = line.get_next_block_position().create_neighbour_coordinate(from_block_direction)
        before_last_coordinates = line.get_last_position().create_neighbour_coordinate(from_block_direction)
        print(f"robot: {self.robot}, start move_to_block_towards_inside, " +
              f"before: {before_block_coordinates}, last: {before_last_coordinates}")
        # returns True when finished but False when still need to add block
        while self.robot_coordinates != before_last_coordinates:
            hit_information = self.shared_actions_executor.try_move_robot(to_block_direction)
            if hit_information.hit_type == HitType.OBSTACLE:
                raise ValueError("scanner cannot work with obstacles")
            elif hit_information.hit_type == HitType.BLOCK:
                placed_block_position: Coordinates = before_block_coordinates
                discovered_block_position = self.robot_coordinates.create_neighbour_coordinate(to_block_direction)
                print(f"robot: {self.robot}, hit block at {discovered_block_position}")
                if before_block_coordinates == discovered_block_position:
                    self._put_block_on_map(line)
                while placed_block_position != discovered_block_position:
                    placed_block_position = self._put_block_on_map(line)
                if line.is_finished():
                    self._go_back_to_start_line(from_block_direction, line.start_coordinates)
                    return True
                self.shared_actions_executor.try_rotate_robot(from_block_direction)
                before_block_coordinates = line.get_next_block_position(). \
                    create_neighbour_coordinate(from_block_direction)
                self._move_to_block_from_inside(from_block_direction, before_block_coordinates)
                return False
            elif hit_information.hit_type == HitType.ROBOT:
                # if we hit robot then he already put at least one new block and we continue with block elsewhere
                self._go_back_to_start_line(from_block_direction, line.start_coordinates)
                return True
        self.shared_actions_executor.try_rotate_robot(from_block_direction)
        before_block_coordinates = line.get_next_block_position(). \
            create_neighbour_coordinate(from_block_direction)
        self._move_to_block_from_inside(from_block_direction, before_block_coordinates)
        return False

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
        # we scan line to the very end, not to the block we want to put
        if self.robot.rotation != to_block_direction:
            self.shared_actions_executor.try_rotate_robot(to_block_direction)
        if self._move_to_block_towards_inside(line):
            return
        while True:
            # we need to rotate in case we were not
            if self.robot.rotation != to_block_direction:
                self.shared_actions_executor.try_rotate_robot(to_block_direction)
            # if we are just before position to put block and correctly rotated
            hit_information = self.shared_actions_executor.try_put_block(to_block_direction)
            if hit_information.hit_type == HitType.PLACED_BLOCK:
                line.place_block()
                break
            elif hit_information.hit_type == HitType.BLOCK:
                # when another robot already put this block
                line.place_block()
                if line.is_finished():
                    break
                before_block_coordinates = line.get_next_block_position(). \
                    create_neighbour_coordinate(from_block_direction)
                self._move_to_block_from_inside(from_block_direction, before_block_coordinates)
                continue
            else:
                raise ValueError("different tile type cannot be on position where block will be added")
        self._go_back_to_start_line(from_block_direction, line_start_coordinates)
