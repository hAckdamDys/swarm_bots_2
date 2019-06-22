from swarm_bots.goal.goal_building import GoalBuilding
from swarm_bots.gui.display_interface import Window


def main():
    goal_building = GoalBuilding("""
        0 0 0 0 0 0
        0 0 0 0 0 0
        0 0 0 0 0 0
        0 0 0 0 0 0
        0 0 0 0 0 0
        """)
    app = Window()
    app.mainloop()


if __name__ == '__main__':
    main()
