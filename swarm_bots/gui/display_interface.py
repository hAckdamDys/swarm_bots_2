import tkinter as tk
from tkinter import font  as tkfont
from tkinter import filedialog


class Window(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")
        self.title('Swarm-bots')
        self.geometry('400x400')

        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.show_frame(SelectWindow(parent=self.container, controller=self))

    def show_frame(self, frame):
        # frame = page_class(parent=self.container, controller=self)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()


class SelectWindow(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.parent = parent
        label = tk.Label(self, text="Welcome to swarm-bots", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        button1 = tk.Button(self, text="Run step-by-step simulation", command=self.fileopen)
        button2 = tk.Button(self, text="Run graph-statistic", command=lambda: controller.show_frame(Statistic(parent, controller)))
        button1.pack()
        button2.pack(side='top', padx=60, pady=60)


    def fileopen(self):
        file = filedialog.askopenfilename(filetypes=[('image files', '.png'), ('image files', '.jpg')])
        if file:
            self.controller.show_frame(GridWindow(self.parent, self.controller, file))
        else:
            self.controller.show_frame(SelectWindow(self.parent, self.controller))


class GridWindow(tk.Frame):

    def __init__(self, parent, controller, file=None):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.file = file
        label = tk.Label(self, text="Grid", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        button1 = tk.Button(self, text=">", command=lambda: controller.show_frame(GridWindow(parent, controller, file)))
        button2 = tk.Button(self, text=">>", command=lambda: controller.show_frame(FinalGridWindow(parent, controller)))
        button1.pack(side='right')
        button2.pack(side='right')
        tk.Label(self, text=file).pack()


class FinalGridWindow(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Result", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        button1 = tk.Button(self, text="Go to the start page", command=lambda: controller.show_frame(SelectWindow(parent, controller)))
        button2 = tk.Button(self, text="Exit", command=controller.quit)
        button1.pack()
        button2.pack()


class Statistic(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Graph", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Go to the start page", command=lambda: controller.show_frame(SelectWindow(parent, controller)))
        button.pack()

