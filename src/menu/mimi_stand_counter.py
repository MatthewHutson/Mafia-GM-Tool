# -- Imports -- #
from utils import *
from menu.menu_classes import *
from tkinter import messagebox
import tkinter as tk
from tkinter import font

# -- Global Variables -- #
milly_stand_counter: int = 0

# -- Functions -- #
@ enforce_types
def display_count() -> None:
    messagebox.showinfo("Stand Counter", f"Mimi has stood up {milly_stand_counter} time{"s" if milly_stand_counter != 1 else ""}!")

@enforce_types
def add_buttons(frame: tk.Frame, size: tuple[int], padding: tuple[int], side: str) -> None:
    global milly_stand_counter, up_arrow, down_arrow, milly_stand_button
    bold_font = font.Font(family = "Airial", size = 10, weight = "bold")
    font_colour = "#000000"

    try:
        milly_stand_button.pack_forget()
        up_arrow.pack_forget()
        down_arrow.pack_forget()
    except: pass

    milly_stand_button = tk.Button(frame, text = f"Stand Counter: {milly_stand_counter}", command = display_count, bg = "#F4BC2F", highlightbackground = "#D4A52F", activebackground = "#BD9226", fg = font_colour, activeforeground = font_colour, font = bold_font)
    milly_stand_button.pack(side = side, padx = padding[0], pady = padding[1], ipadx = size[0], ipady = size[1])

    up_arrow = tk.Button(frame, text = "↑", command = lambda: change_counter(1, frame, size, padding, side), bg = "#F4BC2F", highlightbackground = "#D4A52F", activebackground = "#BD9226", fg = font_colour, activeforeground = font_colour, font = bold_font)
    down_arrow = tk.Button(frame, text = "↓", command = lambda: change_counter(-1, frame, size, padding, side), bg = "#F4BC2F", highlightbackground = "#D4A52F", activebackground = "#BD9226", fg = font_colour, activeforeground = font_colour, font = bold_font)
    
    up_arrow.pack(side = side, padx = padding[0], pady = padding[1], ipadx = size[1], ipady = size[1])
    down_arrow.pack(side = side, padx = padding[0], pady = padding[1], ipadx = size[1], ipady = size[1])


@enforce_types
def change_counter(amount: int, frame: tk.Frame, size: tuple[int], padding: tuple[int], side: str) -> None:
    global milly_stand_counter
    milly_stand_counter += amount

    if milly_stand_counter < 0:
        milly_stand_counter = 0
    else:
        add_buttons(frame, size, padding, side)

@enforce_types
def counter_init(root: tk.Tk, frame: tk.Frame, size: tuple[int], padding: tuple[int], side: str) -> None:
    root.bind("<Up>", lambda x: change_counter(1, frame, size, padding, side))
    root.bind("<Down>", lambda x: change_counter(-1, frame, size, padding, side))
    add_buttons(frame, size, padding, side)
