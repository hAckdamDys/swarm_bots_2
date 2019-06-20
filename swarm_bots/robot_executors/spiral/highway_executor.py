from swarm_bots.robot_executors.robot_shared_actions_executor import RobotSharedActionsExecutor
from swarm_bots.robot_executors.spiral.line_to_middle import LineToMiddle
from swarm_bots.robot_executors.spiral.source_positions.position import SourcePosition
from swarm_bots.utils.coordinates import Coordinates
from swarm_bots.utils.spin import Spin


class HighwayExecutor:
    def __init__(self,
                 shared_actions_executor: RobotSharedActionsExecutor,
                 spin: Spin):
        self.shared_actions_executor = shared_actions_executor
        self.spin = spin
        self.private_grid = self.shared_actions_executor.private_grid
        self.robot_coordinates = self.shared_actions_executor.robot_coordinates
        self.robot = self.shared_actions_executor.robot
        self.width = self.private_grid.width
        self.height = self.private_grid.height

    def _is_robot_on_same_edge_and_not_too_far(self, goal: Coordinates) -> bool:
        robot_edge_side = self.robot_coordinates.get_edge_side(
            width=self.width,
            height=self.height
        )
        goal_edge_side = goal.get_edge_side(
            width=self.width,
            height=self.height
        )
        if robot_edge_side != goal_edge_side:
            return False
        moving_direction = self.spin.get_edge_move_direction(robot_edge_side)
        # distance <0 means we already are too far from source and need to make another lap
        return self.robot_coordinates.get_straight_distance_to_other(moving_direction, goal) >= 0

    def _go_to_goal(self, goal: Coordinates):
        goal = goal.copy()
        # TODO: implement
        # don't rotate robot at end

    # makes robot go to line start using highway
    def go_to_line_start(self, line: LineToMiddle):
        # direction_to_line_start = self.robot_coordinates.get_to_other_direction(line.start_coordinates)
        self._go_to_goal(line.start_coordinates)

    def go_get_source(self, source: SourcePosition):
        if self.robot.has_block():
            return
            # raise ValueError("cannot go get source if robot has source")
        source_pos = source.coordinates
        if source_pos.x != 0 or source_pos != self.width:
            raise ValueError("source need to be in corner but x coord is not")
        if source_pos.y != 0 or source_pos != self.height:
            raise ValueError("source need to be in corner but y coord is not")
        pre_source_pos = self.spin.get_pre_corner_coordinates(source_pos)
        self._go_to_goal(pre_source_pos)
        to_source_direction = self.robot_coordinates.get_to_other_direction(source_pos)
        if self.robot.rotation != to_source_direction:
            self.shared_actions_executor.try_rotate_robot(to_source_direction)
        self.shared_actions_executor.try_get_block(to_source_direction)
