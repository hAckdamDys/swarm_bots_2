from swarm_bots.robot_executors.hit_information import HitType
from swarm_bots.robot_executors.robot_shared_actions_executor import RobotSharedActionsExecutor
from swarm_bots.robot_executors.spiral.line_to_middle import LineToMiddle
from swarm_bots.robot_executors.spiral.source_positions.position import SourcePosition
from swarm_bots.utils.coordinates import Coordinates
from swarm_bots.utils.direction import Direction
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

    def _go_around_corner(self, moving_direction: Direction):
        next_direction = self.spin.get_edge_move_direction(moving_direction)
        # rotate, go next_direction,
        if self.robot.rotation != next_direction:
            self.shared_actions_executor.try_rotate_robot(next_direction)
        hit_type = HitType.ROBOT
        while hit_type != HitType.NO_HIT:
            hit_information = self.shared_actions_executor.try_move_robot(next_direction)
            hit_type = hit_information.hit_type
        # rotate, go prev_direction
        self.shared_actions_executor.try_rotate_robot(moving_direction)
        hit_type = HitType.ROBOT
        while hit_type != HitType.NO_HIT:
            hit_information = self.shared_actions_executor.try_move_robot(moving_direction)
            hit_type = hit_information.hit_type
        print(f"robot: {self.robot.id} went around corner {moving_direction}:{next_direction}")

    def go_to_goal(self, goal: Coordinates):
        goal = goal.copy()
        while not self._is_robot_on_same_edge_and_not_too_far(goal):
            robot_edge_side = self.robot_coordinates.get_edge_side(
                width=self.width,
                height=self.height
            )
            next_corner = self.spin.get_edge_next_corner(
                robot_edge_side,
                width=self.width,
                height=self.height
            )
            pre_corner_pos = self.spin.get_pre_corner_coordinates(next_corner)
            moving_direction = self.spin.get_edge_move_direction(robot_edge_side)
            if self.robot_coordinates != pre_corner_pos:
                self.shared_actions_executor.try_rotate_robot(moving_direction)
            while self.robot_coordinates != pre_corner_pos:
                hit_information = self.shared_actions_executor.try_move_robot(moving_direction)
                if hit_information.hit_type != HitType.NO_HIT:
                    self.shared_actions_executor.wait_action()
            # robot is on pre_corner_coordinates
            self._go_around_corner(moving_direction)
        # here robot is on same edge as goal
        moving_direction = self.robot_coordinates.get_to_other_direction(goal)
        if self.robot.rotation != moving_direction:
            self.shared_actions_executor.try_rotate_robot(moving_direction)
        while self.robot_coordinates != goal:
            hit_information = self.shared_actions_executor.try_move_robot(moving_direction)
            if hit_information.hit_type != HitType.NO_HIT:
                self.shared_actions_executor.wait_action()

    # makes robot go to line start using highway
    def go_to_line_start(self, line: LineToMiddle):
        # direction_to_line_start = self.robot_coordinates.get_to_other_direction(line.start_coordinates)
        self.go_to_goal(line.start_coordinates)

    def go_get_source(self, source: SourcePosition):
        if self.robot.has_block():
            print("WARNING GO_GET_SOURCE:"+str("cannot go get source if robot has source"))
            return
            # raise ValueError("cannot go get source if robot has source")
        source_pos = source.coordinates
        if source_pos.x != 0 and source_pos.x != self.width - 1:
            raise ValueError("source need to be in corner but x coord is not")
        if source_pos.y != 0 and source_pos.y != self.height - 1:
            raise ValueError("source need to be in corner but y coord is not")
        pre_source_pos = self.spin.get_pre_corner_coordinates(source_pos)
        self.go_to_goal(pre_source_pos)
        to_source_direction = self.robot_coordinates.get_to_other_direction(source_pos)
        if self.robot.rotation != to_source_direction:
            self.shared_actions_executor.try_rotate_robot(to_source_direction)
        self.shared_actions_executor.try_get_block(to_source_direction)
