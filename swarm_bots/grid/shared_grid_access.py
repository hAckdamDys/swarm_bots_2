from multiprocessing import Manager
from threading import Lock

from swarm_bots.grid.base_grid import BaseGrid
from swarm_bots.grid.tile_exists_exception import TileTakenException
from swarm_bots.robot_executors.hit_information import HitInformation, HitType
from swarm_bots.robot_executors.wrong_tile_error import WrongTileError
from swarm_bots.tiles.impossible_robot_movement_error import ImpossibleRobotMovementError
from swarm_bots.tiles.robot import Robot
from swarm_bots.utils.coordinates import Coordinates
from swarm_bots.utils.direction import Direction


class GridLockSync:
    def __init__(self, grid: BaseGrid, manager: Manager):
        self.lock = manager.Lock()
        self.grid = grid
        self.manager_list = manager.list()
        self.manager_list.append(grid)

    def sync_grid(self):
        self.grid = self.manager_list[0]

    def update_grid(self):
        self.manager_list[0] = self.grid

    def __enter__(self):
        self.lock.acquire()
        self.sync_grid()
        return self.grid

    # noinspection PyShadowingBuiltins
    def __exit__(self, type, value, traceback):
        self.update_grid()
        self.lock.release()


class SharedGridAccess:
    lock: Lock

    def __init__(self, grid: BaseGrid, manager: Manager):
        self.grid_lock_sync = GridLockSync(grid, manager)
        # when simulation is not started we can add elements and do more
        self.simulation_started = False

    def get_private_copy(self):
        with self.grid_lock_sync as grid:
            return grid.copy()

    # This should be done to BaseGrid added before access is even made
    # def add_tile(self, tile: Tile, coordinates: Coordinates):
    #     if self.simulation_started:
    #         raise SimulationStartedError("cannot add tile when simulation started")
    #     with self.lock:
    #         self.grid.add_tile_to_grid(tile=tile, coordinates=coordinates)
    #
    # def remove_tile(self, coordinates: Coordinates):
    #     if self.simulation_started:
    #         raise SimulationStartedError("cannot add tile when simulation started")
    #     with self.lock:
    #         self.grid.remove_tile_from_grid(coordinates)

    @staticmethod
    def _get_robot_coordinates(grid: BaseGrid, robot: Robot) -> Coordinates:
        coordinates = grid.get_coord_from_tile(robot)
        robot_grid_instance = grid.get_tile_from_grid(coordinates)
        if robot != robot_grid_instance:
            raise WrongTileError(f"difference between robot: {robot}, and tile on grid: {robot_grid_instance}")
        return coordinates

    def try_rotate_robot(self, robot: Robot, direction: Direction) -> HitInformation:
        with self.grid_lock_sync as grid:
            try:
                coordinates = self._get_robot_coordinates(grid, robot)
            except RuntimeError as e:
                return HitInformation(HitType.ERROR, e)
            robot.rotate_to_direction(direction)
            grid.move_tile_on_grid(robot, coordinates)
            return HitInformation(HitType.NO_HIT)

    def try_move_robot(self, robot: Robot, direction: Direction) -> HitInformation:
        with self.grid_lock_sync as grid:
            try:
                coordinates = self._get_robot_coordinates(grid, robot)
            except RuntimeError as e:
                return HitInformation(HitType.ERROR, e)
            try:
                robot.validate_movement_direction(direction)
            except ImpossibleRobotMovementError as e:
                return HitInformation(HitType.ERROR, e)
            new_coordinates = coordinates.create_neighbour_coordinate(direction)
            try:
                grid.move_tile_on_grid(robot, new_coordinates)
            except TileTakenException as t:
                tile = t.get_tile()
                return HitInformation(HitType.from_tile_type(tile.get_type()))
            # TODO: add out of bounds action
            return HitInformation(HitType.NO_HIT)
