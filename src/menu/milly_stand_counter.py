# -- Imports -- #
from utils import *
from menu.menu_classes import *
from tkinter import messagebox
from copy import deepcopy
import tkinter as tk
import sys
import json

# -- Global Variables -- #
milly_stand_counter: int = 0

# -- Functions -- #
@ enforce_types
def display_count() -> None:
    messagebox.showinfo("Stand Counter", f"Milly has stood up {milly_stand_counter} time{"s" if milly_stand_counter != 1 else ""}!")

@enforce_types
def change_counter(amount: int) -> None:
    globals()["milly_stand_counter"] += amount

    if milly_stand_counter < 0:
        globals()["milly_stand_counter"] = 0

    display_count()

@enforce_types
def counter_init(root: tk.Tk, frame: tk.Frame, size: tuple[int], padding: tuple[int], side: str) -> None:
    root.bind("m", lambda x: change_counter(1))
    root.bind("n", lambda x: change_counter(-1))
    milly_stand_button = tk.Button(frame, text = "Stand Counter", command = display_count, bg = "#F4BC2F", highlightbackground = "#D4A52F", activebackground = "#BD9226", fg = "#000000", activeforeground = "#000000")
    milly_stand_button.pack(side = side, padx = padding[0], pady = padding[1], ipadx = size[0], ipady = size[1])
