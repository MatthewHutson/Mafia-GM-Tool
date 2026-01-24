# -- Import -- #
from utils import *
import tkinter as tk
from tkinter import font

# -- Global Variables -- #
root: tk.Tk = tk.Tk()
name_entry: tk.Entry = tk.Entry(root)

# -- Functions -- #
@enforce_types
def setup_menu() -> None:
    root.geometry("1024x512")
    root.title("Mafia Game")
    tk.Label(root, text = "Role Allocation", font = ("Airial", 16), bg = "lightgrey").pack(side = tk.TOP, fill = "x")
    tk.Label(root, text = "Name:").pack(side = tk.LEFT, anchor = "nw", padx = 8, pady = 4)
    name_entry.pack(side = tk.LEFT, ipadx = 64, anchor = "nw", padx = 8, pady = 4)
    add: tk.Button = tk.Button(root, text = "Add", command = add_player).pack(side = tk.LEFT, ipadx = 32, anchor = "nw", padx = 8, pady = 4)
    tk.Label(root, text = "Players", font = ("Airial", 10)).pack(side = tk.TOP, anchor = "e")

    root.mainloop()

@enforce_types
def add_player() -> None:
    try: 
        user_input: str = name_entry.get().strip()
        if not user_input: raise Exception
        name_entry.delete(0, tk.END)
    except: pass