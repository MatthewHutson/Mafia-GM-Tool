# -- Imports -- #
from utils import *
from menu.menu_classes import *
import tkinter as tk
from tkinter import messagebox

# -- Global Variables -- #
root: tk.Tk = tk.Tk()
root.resizable(False, False)

MAX_PLAYERS: int = 7
players: list[Player_Frame] = []

player_margin = tk.Frame(root)
player_tab = tk.Frame(player_margin, bg = "#d3d3d3")

input_frame = tk.Frame(player_margin)
name_entry: tk.Entry = tk.Entry(input_frame)

role_frame = tk.Frame(root, bg = "#d3d3d3")
role_row_frames = Role_Row(role_frame)

main_font = ("Airial", 10)

# -- Functions -- #
@enforce_types
def add_player(players: list[tk.Label], roles: list[Role]) -> None:
    try: 
        user_input: str = name_entry.get().strip()
        
        if not user_input: 
            raise ValueError
        
        name_entry.delete(0, tk.END)

        if len(players) >= MAX_PLAYERS: 
            messagebox.showwarning("Warning", "You Have Reached The Maximum Number of Players!")
            raise IndexError
        
        for frame in players:
            if frame == capitalise_words(user_input):
                messagebox.showwarning("Warning", "A Player With This Name Already Exists!")
                raise ValueError
        
        add_role_tile(len(players), roles)
        player_frame = Player_Select_Frame(user_input, player_tab, main_font, players, role_row_frames)
        players.append(player_frame)

    except: pass

@enforce_types
def add_role_tile(player_count: int, roles: list[Role]) -> None:
    role_icon = Role_Icon(roles[player_count], main_font)
    role_row_frames.add_item(role_icon)

@enforce_types
def setup_menu(entries: Menu_Entry, all_roles: list[Role]) -> None:
    # -- Menu -- #
    root.geometry("1024x512")
    root.title("Mafia Game")
    tk.Label(root, text = "Player Selection", font = ("Airial", 16), bg = "#d3d3d3").pack(side = tk.TOP, fill = "x", pady = 4)

    # -- Add Player Input -- #
    tk.Label(input_frame, text = "Name:").pack(side = tk.LEFT, padx = 8, pady = 8)
    add: tk.Button = tk.Button(input_frame, text = "Add", command = lambda: add_player(players, all_roles), bg = "#00ff00", highlightbackground = "#00cd00", activebackground = "#00aa00").pack(side = tk.RIGHT, padx = 8, pady = 8)
    name_entry.pack(fill = "x", padx = 8, pady = 8, ipady = 12)
    input_frame.pack_propagate(False)
    input_frame.pack(side = tk.TOP, anchor = "w", ipadx = 158, ipady = 20)

    # -- Role Selection -- #
    tk.Label(role_frame, text = "Roles", font = main_font).pack(side = tk.TOP, padx = 4, pady = 4 , fill = "x")
    #role_tab.pack(side = tk.TOP, anchor = "nw", padx = 4, pady = 4, fill = "both", expand = True)

    # -- Main Partitions -- #
    player_margin.pack(side = tk.LEFT, anchor = "nw")
    role_frame.pack(side = tk.TOP, anchor = "nw", fill = "both", padx = 4, pady = 4, expand = True)

    # -- Player Display Tab -- #
    tk.Label(player_tab, text = "Players", font = main_font).pack(side = tk.TOP, padx = 4, pady = 4,  fill = "x")
    player_tab.pack(side = tk.TOP, anchor = "w", padx = 4, pady = 4, ipadx = 128, ipady = 256)
    root.mainloop()