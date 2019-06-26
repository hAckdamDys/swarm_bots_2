import os
import tkinter as tk
from multiprocessing import Manager
from tkinter import font as tkfont
from tkinter import filedialog
from tkinter import Label
from typing import List

from PIL import Image, ImageTk

from swarm_bots.goal.goal_building_2d import GoalBuilding2D
from swarm_bots.grid.errors.tile_not_exists_exception import TileNotExistsException
from swarm_bots.grid.shared_grid_access import SharedGridAccess
from swarm_bots.gui.grid_actions import create_grid_from_file
from swarm_bots.gui.grid_actions import calculate_procentage_difference
from swarm_bots.robot_executors.robot_executor import RobotExecutor
from swarm_bots.robot_executors.spiral.goal_to_edges_splitters.goal_to_edges_x_splitter import GoalToEdgesXSplitter
from swarm_bots.robot_executors.spiral.spiral_robot_executor import SpiralRobotExecutor
from swarm_bots.tiles.robot import Robot

from swarm_bots.tiles.tile import TileType, Tile
from swarm_bots.grid.base_grid import BaseGrid
from swarm_bots.utils.coordinates import Coordinates
from swarm_bots.utils.direction import Direction
from swarm_bots.utils.spin import Spin

SIZE = 400
MENU_OPTION_PICTURE_PATH = os.path.dirname(os.path.realpath(__file__)) + r'\images\menu.png'


class Window(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")
        self.title('Swarm-bots')
        self.geometry('%dx%d' % (SIZE, SIZE))
        self.base_grid = BaseGrid(5, 5)
        self.goal_building = None

        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.show_frame(WelcomeWindow(parent=self.container, controller=self))

    def show_frame(self, frame):
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()


class WelcomeWindow(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.parent = parent

        label = tk.Label(self, text="Welcome to swarm-bots!", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        button = tk.Button(self, text="Select file", command=self.fileopen)
        button.pack(pady=100)

    def fileopen(self):
        file = filedialog.askopenfilename(filetypes=[('image files', '.png')])
        if file:
            self.controller.show_frame(CreateGridWindow(self.parent, self.controller, file))
        else:
            self.controller.show_frame(WelcomeWindow(self.parent, self.controller))


class CreateGridWindow(tk.Frame):

    def __init__(self, parent, controller, file):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.file = file
        self.number_of_robots = 0
        self.number_of_sources = 0

        goal_building = create_grid_from_file(file)
        controller.goal_building = goal_building
        grid_window = [[None for y in range(goal_building.height)] for x in range(goal_building.width)]

        for row_index in range(goal_building.height):
            self.rowconfigure(row_index, weight=1)
            for col_index in range(goal_building.width):
                self.columnconfigure(col_index, weight=1)
                btn = tk.Button(self, bg='grey76', command=lambda i=col_index, j=row_index: change_tile_type(i, j))
                btn.grid(row=row_index, column=col_index, sticky="nsew")
                grid_window[col_index][row_index] = btn

        button = tk.Button(self, text="START", state='disabled', command=lambda: create_simulation(parent, controller))
        button.grid(columnspan=50)

        basewidth = 50

        goal_img = Image.open(file)
        wpercent = (basewidth / float(goal_img.size[0]))
        hsize = int((float(goal_img.size[1]) * float(wpercent)))
        goal_img = goal_img.resize((basewidth, hsize), Image.ANTIALIAS)
        tkimage = ImageTk.PhotoImage(goal_img)
        myvar_goal = Label(self, image=tkimage)
        myvar_goal.image = tkimage
        myvar_goal.grid(column=goal_building.width + 1, row=0, columnspan=50, rowspan=50)

        img = ImageTk.PhotoImage(Image.open(MENU_OPTION_PICTURE_PATH))
        myvar = Label(self, image=img)
        myvar.image = img
        myvar.grid(column=goal_building.width + 1, row=10, columnspan=50, rowspan=50)

        def change_tile_type(col, row):
            if grid_window[col][row].cget('bg') == 'grey76':
                grid_window[col][row].configure(bg='yellow')
                self.number_of_robots += 1
            elif grid_window[col][row].cget('bg') == 'yellow':
                grid_window[col][row].configure(bg='grey76')
                self.number_of_robots -= 1
            if self.number_of_robots == 0:
                button.configure(state='disabled')
            else:
                button.configure(state='normal')

        def create_simulation(parent, controller):
            # text_grid = """
            #        0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
            #        0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
            #        0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0
            #        0 0 0 0 0 0 0 0 1 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 1 0 0 0 0 0 0 1 0 0 0 0
            #        0 0 0 0 0 0 0 0 1 0 0 1 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 1 1 0 0 0 1 0 0 0 1 0 0 1 0 0 0 1 0 0 0 0
            #        0 0 0 0 0 1 0 0 1 0 1 1 1 0 0 1 0 1 0 0 0 1 1 1 1 1 1 1 1 1 1 1 0 0 1 0 0 0 1 0 0 1 0 0 0 1 0 1 0 0
            #        0 0 0 0 0 1 0 0 1 0 1 1 1 1 0 0 0 1 0 0 0 1 1 1 1 1 1 1 1 1 1 1 0 0 1 0 1 0 1 0 0 1 0 0 0 1 0 1 0 0
            #        0 0 0 0 0 1 0 0 1 0 1 1 1 1 0 0 0 1 0 0 0 1 1 1 1 1 1 1 1 1 1 1 0 0 1 0 1 0 1 0 0 1 0 0 0 1 0 1 0 0
            #        0 0 0 0 0 1 0 0 0 0 1 1 1 1 0 1 0 1 0 0 0 1 1 1 1 1 1 1 1 1 1 1 0 0 1 0 1 0 1 0 0 1 0 0 0 1 0 1 0 0
            #        0 0 0 0 0 1 0 0 0 0 1 1 1 1 0 0 0 1 0 0 0 1 1 1 1 1 1 1 1 1 1 1 0 0 1 0 1 0 1 0 0 1 0 0 0 1 0 1 0 0
            #        0 0 0 0 0 1 0 0 0 0 0 1 1 1 1 0 0 1 0 0 0 1 1 1 1 1 1 1 1 1 1 1 0 0 1 0 1 0 1 0 0 1 0 0 0 1 0 1 0 0
            #        0 0 0 0 0 1 0 0 1 0 0 0 1 1 1 0 0 1 0 0 0 1 1 1 1 1 1 1 1 1 1 1 0 0 1 0 1 0 1 0 0 1 0 0 0 0 0 1 0 0
            #        0 0 0 0 0 1 0 0 1 0 0 0 1 1 1 0 0 0 1 0 0 0 1 1 1 1 1 1 1 1 1 0 1 0 0 1 0 1 0 0 0 0 1 0 0 0 0 0 0 0
            #        0 0 0 0 0 0 0 0 1 0 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 1 0 0
            #        0 0 0 0 0 0 0 0 1 0 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0
            #        0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
            #        0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
            #        """
            robots: List[Robot] = list()
            robots_pos: List[Coordinates] = list()
            how_many_robots = 8

            for i in range(how_many_robots):
                robots.append(Robot(Direction.UP))
                robots_pos.append(Coordinates(i + 1, 0))

            base_grid = BaseGrid(goal_building.width, goal_building.height)
            base_grid.add_tile_to_grid(Tile(TileType.SOURCE), Coordinates(0, 0))
            base_grid.add_tile_to_grid(Tile(TileType.SOURCE), Coordinates(goal_building.width - 1, 0))
            base_grid.add_tile_to_grid(Tile(TileType.SOURCE),
                                       Coordinates(goal_building.width - 1, goal_building.height - 1))
            base_grid.add_tile_to_grid(Tile(TileType.SOURCE), Coordinates(0, goal_building.height - 1))

            shared_grid_access = SharedGridAccess(base_grid, manager=Manager())
            spin = Spin.ANTI_CLOCKWISE
            goal_to_edges_splitter = GoalToEdgesXSplitter(goal_building, spin)

            robot_executors: List[RobotExecutor] = list()
            for i in range(how_many_robots):
                robot_executors.append(SpiralRobotExecutor(
                    robot=robots[i],
                    shared_grid_access=shared_grid_access,
                    goal_building=goal_building,
                    goal_to_edges_splitter=goal_to_edges_splitter,
                    spin=spin,
                    start_offset=i,
                    start_edge_index=i % 4,
                    robot_coordinates=robots_pos[i],
                    sleep_tick_seconds=0.001
                ))

            with shared_grid_access.grid_lock_sync as grid:
                for i in range(how_many_robots):
                    grid.add_tile_to_grid(robots[i], robots_pos[i])

            controller.robot_executors = robot_executors
            controller.shared_grid_access = shared_grid_access
            controller.goal_building = goal_building

            for robot_executor in controller.robot_executors:
                robot_executor.start_working()

            controller.show_frame(
                GridWindow(
                    parent,
                    controller
                ))


class GridWindow(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.robot_executors: List[RobotExecutor] = controller.robot_executors
        self.goal_building = controller.goal_building
        self.shared_grid_access = controller.shared_grid_access
        self.controller = controller
        self.parent = parent
        button1 = tk.Button(self, text=" > ", command=lambda: self.just_update())
        button2 = tk.Button(self, text=">>", command=lambda: controller.show_frame(FinalGridWindow(parent, controller)))
        grid_inside = self.shared_grid_access.get_private_copy()
        button1.grid(row=grid_inside.height + 1, columnspan=50)
        button2.grid(row=grid_inside.height + 1, column=1, columnspan=50)
        self.height = grid_inside.height
        self.width = grid_inside.width
        self.grid_window = [[None for y in range(self.height)] for x in range(self.width)]
        for row in range(self.height):
            self.rowconfigure(row, weight=1)
            for col in range(self.width):
                self.columnconfigure(col, weight=1)
                btn = tk.Button(self, state='disabled', bg='grey76')
                btn.grid(row=row, column=col, sticky="nsew")
                self.grid_window[col][row] = btn
        self.parent.after(0, self.just_update)

    def just_update(self):
        for x in range(self.width):
            for y in range(self.height):
                self.grid_window[x][y].configure(bg='grey76')
        grid_inside = self.shared_grid_access.get_private_copy()
        for tile_index, tile in grid_inside.tiles_from_index.items():
            try:
                coordinate = grid_inside.get_coord_from_tile(tile)
                if tile.tile_type == TileType.ROBOT:
                    self.grid_window[coordinate.x][coordinate.y].configure(bg='yellow')
                if tile.tile_type == TileType.OBSTACLE:
                    self.grid_window[coordinate.x][coordinate.y].configure(bg='grey')
                if tile.tile_type == TileType.SOURCE:
                    self.grid_window[coordinate.x][coordinate.y].configure(bg='red')
                if tile.tile_type == TileType.BLOCK:
                    self.grid_window[coordinate.x][coordinate.y].configure(bg='blue')
            except TileNotExistsException:
                pass
                # print(f"WARNING: {t}")
        if not self.goal_building.validate_grid(grid_inside):
            self.parent.after(300, self.just_update)
        else:
            for robot_executor in self.robot_executors:
                robot_executor.wait_for_finish()


class FinalGridWindow(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.controller = controller
        self.goal_building = controller.goal_building
        # TODO: result building is not goal building it is controller.shared_grid.get private copy
        # self.result_building = controller.goal_building
        self.result_building = controller.shared_grid_access.get_private_copy().block_tile_grid

        label = tk.Label(self, text="Result", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        tk.Label(self, text=calculate_procentage_difference(self.goal_building, self.result_building),
                 font=tkfont.Font(family='Helvetica', size=60, weight="bold", slant="italic")).pack()
        tk.Label(self, text='Similarity',
                 font=tkfont.Font(family='Helvetica', size=10, weight="bold", slant="italic")).pack()
        result_building_window = tk.Toplevel()
        result_building_window.title('Result Building')
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = ws - 25 - SIZE
        y = (hs / 2) - (SIZE / 2)
        result_building_window.geometry('%dx%d+%d+%d' % (SIZE, SIZE, x, y))
        print_grid(result_building_window, self.result_building[..., ::-1],
                   self.goal_building.height, self.goal_building.width)

        goal_building_window = tk.Toplevel()
        goal_building_window.title('Goal Building')
        goal_building_window.geometry('%dx%d+%d+%d' % (SIZE, SIZE, x - 25 - SIZE, y))
        print_grid(goal_building_window, convert_global_grid_to_local(self.goal_building), self.goal_building.height,
                   self.goal_building.width)

        button1 = tk.Button(self, text="Go to the start page",
                            command=lambda: self.go_to_start_page(goal_building_window, result_building_window))
        button2 = tk.Button(self, text="Exit", command=controller.quit)
        button1.pack(pady=50)
        button2.pack(side='bottom')

    def go_to_start_page(self, win1, win2):
        win1.destroy()
        win2.destroy()
        self.controller.show_frame(WelcomeWindow(self.parent, self.controller))


def convert_global_grid_to_local(grid):
    return grid.grid[..., ::-1]


def print_grid(self, grid, height, width):
    grid_window = [[None for y in range(height)] for x in range(width)]
    for row in range(height):
        self.rowconfigure(row, weight=1)
        for col in range(width):
            self.columnconfigure(col, weight=1)
            if grid[col][row] == 1:
                btn = tk.Button(self, state='disabled', bg='black')
            elif grid[col][row] == 2:
                btn = tk.Button(self, state='disabled', bg='yellow')
            else:
                btn = tk.Button(self, state='disabled', bg='grey76')
            btn.grid(row=row, column=col, sticky="nsew")
            grid_window[col][row] = btn
