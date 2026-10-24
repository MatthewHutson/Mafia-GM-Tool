# -- Imports -- #
from utils import *
import typing as tp
from menu.menu_classes import *
import tkinter as tk
import json

# -- Global Vars -- #
instances: list[tk.Toplevel] = []
frames: list[tk.Frame] = []

# -- Functions -- #
@enforce_types
def create_life_and_death_popup(bg: str) -> tk.Toplevel:
    global instances, frames
    remove_instances()
    root = tk.Toplevel()
    frames = []
    root.resizable(False, True)
    root.geometry("512x768")
    root.title("Life & Death")
    root.config(bg = bg)
    root.protocol("WM_DELETE_WINDOW", remove_instances())

    instances.append(root)

    return root

@enforce_types
def remove_instances() -> None:
    global instances, frames

    for i in range(len(instances)):
        instance: tk.Toplevel = instances.pop(0)
        remove_frames(instance)
        instance.destroy()


@enforce_types
def remove_frames(root: tk.Toplevel) -> None:
    global instances, frames

    for i in range(len(frames)):
        frame: tk.Frame = frames.pop(0)
        frame.destroy()

    children: list[tk.Widget] = root.winfo_children()

    for i in range(len(children)):
        widget: tk.Widget = children.pop(0)
        widget.destroy()

@enforce_types
def update_settings() -> None:
    # -- Updates All Settings When Called By Menu -- #
    global frames
    for setting in frames:
        setting.update()

@enforce_types
def life_and_death_popup(data: Game_Data, bg_1: str = "#F0F0F0", bg_2 = "#d3d3d3", text_colour = "#000000") -> None:
    # -- Initialisation -- #
    global instances, frames

    if len(instances) == 0: root = create_life_and_death_popup(bg_1)
    else: root = instances[0]
    remove_frames(root)

    root.update()

    rows: int = 1
    columns: int = 2

    max_width: int = root.winfo_width() // 2 - 4
    max_height: int = root.winfo_height() // 20

    for i in range(rows): root.rowconfigure(i, weight = 1)

    root.rowconfigure(rows, weight = 0, minsize = max_height)

    for i in range(columns): root.columnconfigure(i, weight = 1, minsize = max_width)
    
    root.columnconfigure(columns, weight = 0)
    root.update()

    alive_margin = tk.Frame(root, bg = bg_2)
    dead_margin = tk.Frame(root, bg = bg_2)
    
    tk.Label(alive_margin, text = "Alive Players", bg = bg_1, fg = text_colour).pack(side = tk.TOP, padx = 4, pady = 4, fill = "x", ipady = 4)
    tk.Label(dead_margin, text = "Dead Players", bg = bg_1, fg = text_colour).pack(side = tk.TOP, padx = 4, pady = 4, fill = "x", ipady = 4)
        
    alive_canvas = Vertical_Scroll_Frame(master = alive_margin, bg  = bg_1, bg_2 = bg_2, pack = False)
    dead_canvas = Vertical_Scroll_Frame(master = dead_margin, bg = bg_1, bg_2 = bg_2, pack = False)

    alive_margin.grid(column = 0, row = 0, padx = 4, sticky = [tk.NW, tk.SE])
    dead_margin.grid(column = 1, row = 0, padx = 4, sticky = [tk.NW, tk.SE])
    
    alive_canvas.pack(side = tk.TOP, padx = 4, pady = 4, fill = "both", expand = False)
    dead_canvas.pack(side = tk.TOP, padx = 4, pady = 4, fill = "both", expand = False)

    for name in data.alive_players.keys():
        bg_frame: tk.Frame = tk.Frame(alive_canvas)
        tk.Label(bg_frame, bg = bg_2, text = name, fg = text_colour).pack(fill = "both", padx = 4, pady = 2, expand = False)
        frames.append(bg_frame)
        alive_canvas.add(bg_frame)

    for name in data.dead_players.keys():
        bg_frame: tk.Frame = tk.Frame(dead_canvas)
        tk.Label(bg_frame, bg = bg_2, text = name, fg = text_colour).pack(fill = "both", padx = 4, pady = 2, expand = False)
        frames.append(bg_frame)
        dead_canvas.add(bg_frame)


    alive_margin.update()
    dead_margin.update()
    alive_margin.pack_propagate(False)
    dead_margin.pack_propagate(False)

    alive_canvas.scroll_all()
    dead_canvas.scroll_all()

    root.update()