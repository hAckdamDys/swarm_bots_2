from multiprocessing import Manager

from swarm_bots.grid.base_grid import BaseGrid
from swarm_bots.grid.errors.out_of_bound_coordinates_error import OutOfBoundCoordinatesError
from swarm_bots.grid.errors.tile_not_exists_exception import TileNotExistsException
from swarm_bots.grid.errors.tile_not_source_error import TileNotSourceError
from swarm_bots.grid.errors.tile_taken_exception import TileTakenException
from swarm_bots.robot_executors.hit_information import HitInformation, HitType
from swarm_bots.robot_executors.wrong_tile_error import WrongTileError
from swarm_bots.tiles.errors.has_inner_block_error import HasInnerBlockError
from swarm_bots.tiles.errors.impossible_robot_movement_error import ImpossibleRobotMovementError
from swarm_bots.tiles.errors.no_inner_block_error import NoInnerBlockError
from swarm_bots.tiles.robot import Robot
from swarm_bots.tiles.tile import TileType
from swarm_bots.tiles.errors.wrong_block_get_direction import WrongBlockGetDirection
from swarm_bots.tiles.errors.wrong_block_put_direction import WrongBlockPutDirection
from swarm_bots.utils.coordinates import Coordinates
from swarm_bots.utils.direction import Direction


class GridLockSync:
    def __init__(self, grid: BaseGrid, manager: Manager):
        self.lock = manager.Lock()
        self.grid = grid
        # self.q = manager.Queue()
        # self.q.put(self.grid)
        self.manager_list = manager.list()
        self.manager_list.append(grid)

    def sync_grid(self):
        # print("syncing")
        self.grid = self.manager_list[0]
        # self.grid = self.q.get()
        # print("synced")

    def update_grid(self):
        # print("updating")
        self.manager_list[0] = self.grid
        # self.q.put(self.grid)
        # print("updated")

    def __enter__(self):
        self.lock.acquire()
        self.sync_grid()
        return self.grid

    # noinspection PyShadowingBuiltins
    def __exit__(self, type, value, traceback):
        self.update_grid()
        self.lock.release()


class SharedGridAccess:
    def __init__(self, grid: BaseGrid, manager: Manager):
        self.grid_lock_sync = GridLockSync(grid, manager)

    def get_private_copy(self):
        with self.grid_lock_sync as grid:
            return grid.copy()

    @staticmethod
    def _get_robot_coordinates(grid: BaseGrid, robot: Robot) -> Coordinates:
        try:
            coordinates = grid.get_coord_from_tile(robot)
            robot_grid_instance = grid.get_tile_from_grid(coordinates)
        except RuntimeError as e:
            raise WrongTileError(f"difference between robot: {robot}, tile on grid with error: {e}")
        if robot != robot_grid_instance:
            raise WrongTileError(f"difference between robot: {robot}, and tile on grid: {robot_grid_instance}")
        return coordinates

    # method to validate robot is the same as in shared grid
    @staticmethod
    def _validate_robot(grid: BaseGrid, robot: Robot):
        SharedGridAccess._get_robot_coordinates(grid, robot)

    def try_rotate_robot(self, robot: Robot, direction: Direction) -> HitInformation:
        # we need to make copy to not mess with input robot
        robot = robot.copy()
        with self.grid_lock_sync as grid:
            try:
                SharedGridAccess._validate_robot(grid, robot)
            except WrongTileError as e:
                return HitInformation(HitType.ERROR, e)
            robot.rotate_to_direction(direction)
            grid.update_tile(robot)
            return HitInformation(HitType.ROTATED, updated_robot=robot)

    def try_move_robot(self, robot: Robot, direction: Direction) -> HitInformation:
        robot = robot.copy()
        with self.grid_lock_sync as grid:
            try:
                coordinates = SharedGridAccess._get_robot_coordinates(grid, robot)
            except WrongTileError as e:
                return HitInformation(HitType.ERROR, e)
            try:
                robot.validate_movement_direction(direction)
            except ImpossibleRobotMovementError as e:
                return HitInformation(HitType.ERROR, e)
            new_coordinates = coordinates.create_neighbour_coordinate(direction)
            try:
                grid.move_tile_on_grid(robot, new_coordinates)
            except TileTakenException as e:
                tile = e.get_tile()
                return HitInformation(HitType.from_tile_type(tile.get_type()), e)
            except OutOfBoundCoordinatesError as e:
                return HitInformation(HitType.ERROR, e)
            # no need to update robot cause inner state is the same
            # print("robot: ", robot, "moved to ", new_coordinates)
            return HitInformation(HitType.NO_HIT, updated_robot=robot)

    # returns HitType.PLACED_BLOCK if placed block correctly
    def try_put_block(self, robot: Robot, direction: Direction) -> HitInformation:
        # we need to make copy to not mess with input robot
        robot = robot.copy()
        with self.grid_lock_sync as grid:
            try:
                coordinates = SharedGridAccess._get_robot_coordinates(grid, robot)
                robot.validate_put_block_direction(direction)
                block_coordinates = coordinates.create_neighbour_coordinate(direction)
                grid.add_tile_to_grid(robot.pop_block(), block_coordinates)
            except (OutOfBoundCoordinatesError, WrongTileError, NoInnerBlockError, WrongBlockPutDirection) as e:
                return HitInformation(HitType.ERROR, e)
            except TileTakenException as e:
                tile = e.get_tile()
                return HitInformation(HitType.from_tile_type(tile.get_type()), e)
            grid.update_tile(robot)
            print(f"robot: {robot.id} placed to {block_coordinates}")
            return HitInformation(HitType.PLACED_BLOCK, updated_robot=robot)

    def try_get_block(self, robot: Robot, direction: Direction):
        robot = robot.copy()
        with self.grid_lock_sync as grid:
            try:
                coordinates = SharedGridAccess._get_robot_coordinates(grid, robot)
                source_coordinates = coordinates.create_neighbour_coordinate(direction)
                robot.validate_get_block_direction(direction)
                if grid.get_tile_from_grid(source_coordinates).get_type() == TileType.BLOCK:
                    block = grid.pop_tile_from_grid(source_coordinates)
                else:
                    block = grid.get_tile_from_source(source_coordinates)
                robot.take_block(block)
            except (OutOfBoundCoordinatesError, TileNotExistsException, TileNotSourceError,
                    WrongTileError, HasInnerBlockError, WrongBlockGetDirection) as e:
                return HitInformation(HitType.ERROR, e)
            grid.update_tile(robot)
            return HitInformation(HitType.GOT_BLOCK, updated_robot=robot)

    def finish_robot(self, robot: Robot):
        robot = robot.copy()
        with self.grid_lock_sync as grid:
            try:
                coordinates = SharedGridAccess._get_robot_coordinates(grid, robot)
            except WrongTileError as e:
                return HitInformation(HitType.ERROR, e)
            grid.remove_tile_from_grid(coordinates)
            return HitInformation(HitType.ROTATED, updated_robot=robot)
