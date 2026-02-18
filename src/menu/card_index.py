# -- Imports -- #
from utils import *
from menu.menu_classes import *
from tkinter import messagebox
from copy import deepcopy
import tkinter as tk
from tkinter import font
import json
# -- Functions -- #
def none() -> None:
    pass

@enforce_types
def card_init() -> dict[str, str]:
    try:
        with open("card_indexes.json", 'r') as file:
            card_data: dict[str, str] = json.load(file)
    except:
        card_data: dict[str, str] = {}

    return card_data  

@enforce_types
def card_index(root: tk.Tk, bg: str, font: tuple[str, int], entries: Menu_Entry, data: Game_Data = None) -> None:
    # -- Initialisation - #
    card_data: dict[str, str] = card_init()
    card_root = tk.Toplevel(root)
    card_root.resizable(False, True)
    card_root.geometry("256x384")
    card_root.title("Card Index")

    scroll_bar = tk.Scrollbar(card_root, orient = "vertical")
    canvas = tk.Canvas(card_root, yscrollcommand = scroll_bar.set)

    scroll_bar.configure(command = canvas.yview)
    scroll_bar.pack(side = tk.RIGHT, fill = "y", ipadx = 4)
    canvas.pack(side = tk.LEFT, fill = tk.BOTH)

    canvas_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window = canvas_frame, anchor = "n")

    # -- Subfunctions -- #
    @enforce_types
    def scroll_all(event) -> None:
        canvas.config(scrollregion=canvas.bbox("all"))

    @enforce_types
    def scroll_event(event) -> None:
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    canvas.bind("<Configure>", scroll_all)
    card_root.bind("<MouseWheel>", scroll_event)

    # -- Card Index-- #
    frames: list[tk.Frame] = []
    roles: list[Role_Icon] = []
    card_labels: list[tk.Label] = []

    for role_name, card in card_data.items():
        if data != None:
            try:
                assert entries.role_dict[role_name] in data.players.values()
            except AssertionError:
                continue
            except KeyError:
                continue

        frame = tk.Frame(canvas_frame)
        role_icon = Role_Icon([role_name], font, entries, (10, 2), (2, 2), none)
        card_label = tk.Label(frame, text = card, bg = bg)

        frames.append(frame)
        roles.append(role_icon)
        card_labels.append(card_label)

        role_icon.pack(frame, frames)
        card_label.pack(side = tk.RIGHT, padx = 2, pady = 2, anchor = "e", fill = "both", expand = True)
        frame.pack(side = tk.TOP, pady = 2, padx = 2, anchor = "n", fill = "x")