import tkinter as tk
from tkinter import font  as tkfont
from tkinter import filedialog


class Window(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")
        self.title('Swarm-bots')
        self.geometry('400x400')

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (SelectWindow, GridWindow, FinalGridWindow):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("SelectWindow")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()


class SelectWindow(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Welcome to swarm-bots", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        button1 = tk.Button(controller, text="Select file")
        button2 = tk.Button(self, text="Start", command=lambda: controller.show_frame("GridWindow"))
        button1.pack()
        button2.pack()


    def fileopen(self):
        file = filedialog.askopenfilename()
        print(file)


class GridWindow(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Grid", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        button1 = tk.Button(self, text=">", command=lambda: controller.show_frame("GridWindow"))
        button2 = tk.Button(self, text=">>", command=lambda: controller.show_frame("FinalGridWindow"))
        button1.pack()
        button2.pack()


class FinalGridWindow(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Result", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        button1 = tk.Button(self, text="Go to the start page", command=lambda: controller.show_frame("SelectWindow"))
        button2 = tk.Button(self, text="Exit", command=controller.quit)
        button1.pack()
        button2.pack()


