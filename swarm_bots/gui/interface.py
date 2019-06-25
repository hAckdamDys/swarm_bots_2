import os
import tkinter as tk
from tkinter import font as tkfont
from tkinter import filedialog
from tkinter import Label
from PIL import Image, ImageTk

from swarm_bots.gui.grid_actions import create_grid_from_file
from swarm_bots.gui.grid_actions import calculate_procentage_difference

from multiprocessing import Manager

from swarm_bots.tiles.robot import Robot
from swarm_bots.utils.direction import Direction
from swarm_bots.tiles.tile import Tile, TileType
from swarm_bots.grid.base_grid import BaseGrid
from swarm_bots.utils.coordinates import Coordinates
from swarm_bots.grid.shared_grid_access import SharedGridAccess
from swarm_bots.robot_executors.robot_executor import RobotExecutor


SIZE = 400
MENU_OPTION_PICTURE_PATH = os.path.dirname(os.path.realpath(__file__))+r'\images\menu.png'

class Window(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")
        self.title('Swarm-bots')
        self.geometry('%dx%d' % (SIZE,SIZE))

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
        local_goal_building = convert_global_grid_to_local(goal_building)
        grid_window = [[None for x in range(goal_building.height)] for y in range(goal_building.width)]

        for row_index in range(goal_building.height):
            self.rowconfigure(row_index, weight=1)
            for col_index in range(goal_building.width):
                self.columnconfigure(col_index, weight=1)
                btn = tk.Button(self, bg='grey76',command=lambda i=col_index, j=row_index: change_tile_type(i, j))
                btn.grid(row=row_index, column=col_index, sticky="nsew")
                grid_window[col_index][row_index] = btn

        button = tk.Button(self, text="START", state ='disabled', command=lambda: create_simulation(parent, controller, goal_building))
        button.grid(columnspan=50)

        basewidth = 50

        goal_img = Image.open(file)
        wpercent = (basewidth/float(goal_img.size[0]))
        hsize = int((float(goal_img.size[1]) * float(wpercent)))
        goal_img = goal_img.resize((basewidth, hsize), Image.ANTIALIAS)
        tkimage = ImageTk.PhotoImage(goal_img)
        myvar_goal = Label(self, image=tkimage)
        myvar_goal.image = tkimage
        myvar_goal.grid(column=goal_building.width+1, row = 0, columnspan=50, rowspan=50)

        img = ImageTk.PhotoImage(Image.open(MENU_OPTION_PICTURE_PATH))
        myvar = Label(self, image=img)
        myvar.image = img
        myvar.grid(column=goal_building.width+1, row = 10, columnspan=50, rowspan=50)

        def create_simulation(parent, controller, goal_building):
            # robots = []
            # for i in range(len(grid_window)):
            #     for j in range(len(grid_window[i])):
            #         if grid_window[i][j].cget('bg') == 'yellow':
            #             robots.append((i, j))
            # for single_robot_coordinates in robots:
            #     i, j = single_robot_coordinates
            #     robot = Robot(Direction.DOWN)
            #     robot_source = Tile(TileType.SOURCE)
            #     robot_coordinates = Coordinates(i, j)
            #     base_grid = BaseGrid(goal_building.width, goal_building.height)
            #     base_grid.add_tile_to_grid(robot, robot_coordinates)
            #     base_grid.add_tile_to_grid(robot_source, robot_coordinates.create_neighbour_coordinate(Direction.UP))
            #     # line_start_coordinates = Coordinates(0, 0)
            #     shared_grid_access = SharedGridAccess(base_grid, manager=Manager())
            #     robot_executor = RobotExecutor(robot, shared_grid_access, goal_building)
            #     robot_executor.start_working()
            #     robot_executor.wait_for_finish()
            #     grid = shared_grid_access.get_private_copy()
            #     # print(grid)
            controller.show_frame(GridWindow(parent, controller, goal_building))

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


class GridWindow(tk.Frame):

    def __init__(self, parent, controller, goal_building):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.goal_building = goal_building

        result_building = goal_building

        button1 = tk.Button(self, text=" > ", state = 'disabled' ,command=lambda: controller.show_frame(GridWindow(parent, controller, goal_building)))
        button2 = tk.Button(self, text=">>", command=lambda: controller.show_frame(FinalGridWindow(parent, controller, goal_building, result_building)))
        button1.grid(row = goal_building.height+1, columnspan=50)
        button2.grid(row = goal_building.height+1, column = 1, columnspan=50)
        print_grid(self, convert_global_grid_to_local(goal_building), goal_building.height, goal_building.width)


class FinalGridWindow(tk.Frame):

    def __init__(self, parent, controller, goal_building, result_building):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.controller = controller
        self.goal_building = goal_building
        self.result_building = result_building

        label = tk.Label(self, text="Result", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        tk.Label(self, text=calculate_procentage_difference(goal_building, result_building),font=tkfont.Font(family='Helvetica', size=60, weight="bold", slant="italic")).pack()
        tk.Label(self, text='Similarity', font = tkfont.Font(family='Helvetica', size=10, weight="bold", slant="italic")).pack()
        result_building_window = tk.Toplevel()
        result_building_window.title('Result Building')
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = ws - 25 - SIZE
        y = (hs / 2) - (SIZE / 2)
        result_building_window.geometry('%dx%d+%d+%d' % (SIZE,SIZE,x,y))
        print_grid(result_building_window, convert_global_grid_to_local(result_building), result_building.height, result_building.width)

        goal_building_window = tk.Toplevel()
        goal_building_window.title('Goal Building')
        goal_building_window.geometry('%dx%d+%d+%d' % (SIZE,SIZE,x-25-SIZE,y))
        print_grid(goal_building_window, convert_global_grid_to_local(goal_building), goal_building.height, goal_building.width)

        button1 = tk.Button(self, text="Go to the start page", command=lambda: self.go_to_start_page(goal_building_window, result_building_window))
        button2 = tk.Button(self, text="Exit", command=controller.quit)
        button1.pack(pady=50)
        button2.pack(side = 'bottom')

    def go_to_start_page(self, win1, win2):
        win1.destroy()
        win2.destroy()
        self.controller.show_frame(WelcomeWindow(self.parent, self.controller))


def convert_global_grid_to_local(grid):
    return grid.grid[...,::-1]


def print_grid(self, grid, height, width, robots=None):
    grid_window = [[None for x in range(height)] for y in range(width)]
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