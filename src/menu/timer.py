# -- Imports -- #
from utils import *
from menu.menu_classes import *
import tkinter as tk

# -- Global Variables -- #
remaining_time: int = 0
timer_active: bool = False

# -- Functions -- #
@enforce_types
def timer_button(root: tk.Misc, button: tk.Button, duration: int) -> None:
    global remaining_time, timer_active
    timer_active = not timer_active

    if timer_active:
        if remaining_time == 0: 
            remaining_time = duration

        ticker(root, button)


@enforce_types
def ticker(root: tk.Misc, button: tk.Button) -> None:
    global remaining_time, timer_active

    if timer_active and remaining_time > 0:
        remaining_time -= 1
        button.config(text = f"Timer: {remaining_time // 60}:{remaining_time % 60}")
        root.after(1000, lambda: ticker(root, button))
    else:
        if remaining_time == 0:
            button.config(text = "Start Timer")
        else:
            button.config(text = f"Paused: {remaining_time // 60}:{remaining_time % 60}")
            
        timer_active = False

@enforce_types
def create_timer(root: tk.Misc, duration: int, font: tuple[str, int], size: tuple[int], padding: tuple[int], side: str) -> None:
    global remaining_time
    timer = tk.Button(root, text = "Start Timer", command = lambda: timer_button(root, timer, duration), bg = "#F42F5A", highlightbackground = "#D42F6E", activebackground = "#BD2658", fg = "#FFFFFF", activeforeground = "#FFFFFF", font = font, width = size[0], height = size[1])
    timer.pack_propagate(False)
    timer.pack(side = side, padx = padding[0], pady = padding[1])
    remaining_time = 0

def delete_timer() -> None:
    global timer_active, remaining_time
    timer_active = False
    remaining_time = 0
