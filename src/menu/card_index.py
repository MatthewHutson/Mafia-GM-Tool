# -- Imports -- #
from utils import *
from menu.menu_classes import *
import tkinter as tk
import json

# -- Global Variables -- #
instances: list[tk.Toplevel] = []

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
def card_index(root: tk.Tk, bg: str, font: tuple[str, int], fg: str, entries: Menu_Entry, data: Game_Data = None) -> None:
    # -- Initialisation - #
    global instances
    card_data: dict[str, str] = card_init()
    card_root = tk.Toplevel()
    card_root.resizable(False, True)
    card_root.geometry("256x384")
    card_root.title("Card Index")

    destroy_card_index()
    instances.append(card_root)

    main_frame = Vertical_Scroll_Frame(master = card_root, bg = bg)

    # -- Card Index-- #
    frames: list[tk.Frame] = []
    roles: list[Role_Icon] = []
    card_labels: list[tk.Label] = []

    for role_name, card in card_data.items():
        if data != None:
            try: assert entries.role_dict[role_name] in data.players.values()
            except AssertionError: continue
            except KeyError: continue
        elif role_name == "Testing":
            continue


        frame = tk.Frame(main_frame, bg = bg)
        role_icon = Role_Icon([role_name], font, entries, (10, 2), (2, 2), none)
        card_label = tk.Label(frame, text = card, bg = bg, fg = fg)

        frames.append(frame)
        roles.append(role_icon)
        card_labels.append(card_label)

        role_icon.pack(frame, frames)
        card_label.pack(side = tk.RIGHT, padx = 2, pady = 2, anchor = "e", fill = "both", expand = True)
        main_frame.add(frame)
        main_frame.update()

    main_frame.scroll_all()

def destroy_card_index() -> None:
    global instances

    for i in range(len(instances)):
        instance = instances.pop(0)
        instance.destroy()