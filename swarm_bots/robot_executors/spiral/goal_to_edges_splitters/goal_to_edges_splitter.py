import abc
from typing import List, Union

from swarm_bots.goal.goal_building import GoalBuilding
from swarm_bots.robot_executors.spiral.grid_edge import GridEdge


class GoalToEdgesSplitter(metaclass=abc.ABCMeta):
    def __init__(self, goal_building: GoalBuilding):
        self.goal_building = goal_building
        self.edges: Union[List[GridEdge], None] = None

    @abc.abstractmethod
    def get_edges(self) -> List[GridEdge]:
        raise NotImplementedError()
