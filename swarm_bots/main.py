from swarm_bots.goal.goal_building import GoalBuilding


def main():
    goal_building = GoalBuilding("""
        0 0 0 0 0 0
        1 0 0 0 0 0
        0 0 0 0 0 0
        0 0 0 0 0 0
        0 0 0 0 0 0
        """)
    print(goal_building)


if __name__ == '__main__':
    main()
