from multiprocessing import Manager

from swarm_bots.grid.base_grid import BaseGrid


class SharedGridAccess:
    def __init__(self, grid: BaseGrid, manager: Manager):
        self.manager_list = manager.list()
        self.manager_list.append(grid)

    @property
    def grid(self) -> BaseGrid:
        return self.manager_list[0]

    def get_private_copy(self):
        return self.grid.copy()
