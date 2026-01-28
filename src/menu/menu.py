# -- Imports -- #
from utils import *
from menu.menu_classes import *
import tkinter as tk
from tkinter import messagebox

# -- Setup Global Variables -- #
root: tk.Tk = tk.Tk()

MAX_PLAYERS: int = 7
MIN_PLAYERS: int = 4
players: list[Player_Select_Frame] = []

player_margin = tk.Frame(root)
player_tab = tk.Frame(player_margin, bg = "#d3d3d3")

input_frame = tk.Frame(player_margin)
name_entry: tk.Entry = tk.Entry(input_frame)

settings_frame = tk.Frame(root)

role_frame = tk.Frame(root, bg = "#d3d3d3")
role_row_frames = Role_Row(role_frame)

main_font = ("Airial", 10)

# -- Game Menu Global Vars -- #

# -- Functions -- #
@enforce_types
def add_player(players: list[tk.Label], roles: list[list[Role]], entries: Menu_Entry) -> None:
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
        
        add_role_tile(len(players), roles, entries)
        player_frame = Player_Select_Frame(user_input, player_tab, main_font, players, role_row_frames)
        players.append(player_frame)

    except: pass

@enforce_types
def add_role_tile(player_count: int, roles: list[Role], entries: Menu_Entry) -> None:
    role_icon = Role_Icon(roles[player_count], main_font, entries)
    role_row_frames.add_item(role_icon)

@enforce_types
def clear(root: tk.Tk) -> None:
    for widget in root.winfo_children():
        widget.destroy()

@enforce_types
def get_data(root: tk.Tk, entries: Menu_Entry) -> None:
    entries.filter_roles([str(icon) for icon in role_row_frames.icon_list])
    entries.players = [str(frame) for frame in players]
    clear(root)
    root.quit()

@enforce_types
def start_confirm(entries: Menu_Entry) -> None:
    if len(players) < 4:
        messagebox.showerror("Error", "You Need at Least 4 Players to Start!")
    else:
        if messagebox.askyesno("Confirm Choice", "Do you wish to start the game?"):
            get_data(root, entries)

# -- Setup Menu -- #
@enforce_types
def setup_menu(entries: Menu_Entry, all_roles: list[list[Role]]) -> None:
    # -- Specific Functions -- #
    @enforce_types
    def enter_pressed(event) -> None:
        add_player(players, all_roles, entries)

    # -- Menu -- #
    root.resizable(False, False)
    root.geometry("1024x512")
    root.title("Mafia Game")
    tk.Label(root, text = "Player Selection", font = ("Airial", 16), bg = "#d3d3d3").pack(side = tk.TOP, fill = "x", pady = 4)

    # -- Add Player Input -- #
    tk.Label(input_frame, text = "Name:").pack(side = tk.LEFT, padx = 8, pady = 8)
    add: tk.Button = tk.Button(input_frame, text = "Add", command = lambda: add_player(players, all_roles, entries), bg = "#00ff00", highlightbackground = "#00cd00", activebackground = "#00aa00").pack(side = tk.RIGHT, padx = 8, pady = 8)
    name_entry.pack(fill = "x", padx = 8, pady = 8, ipady = 12)
    name_entry.bind("<Return>", enter_pressed)
    input_frame.pack_propagate(False)
    input_frame.pack(side = tk.TOP, anchor = "w", ipadx = 158, ipady = 20)

    # -- Settings Buttons -- #
    start = tk.Button(settings_frame, text = "Start", command = lambda: start_confirm(entries), bg = "#5D9FF0", activebackground = "#4980C4")
    start.pack(side = tk.RIGHT, ipady = 3, ipadx = 16, padx = 4)

    # -- Role Selection -- #
    tk.Label(role_frame, text = "Roles", font = main_font).pack(side = tk.TOP, padx = 4, pady = 4, fill = "x")

    # -- Main Partitions -- #
    player_margin.pack(side = tk.LEFT, anchor = "nw")
    settings_frame.pack(side = tk.TOP, anchor = "n", padx = 4, pady = 4, fill = "x")
    role_frame.pack(side = tk.TOP, anchor = "nw", fill = "both", padx = 4, pady = 4, expand = True)

    # -- Setting Partitions -- #
    role_frame.pack_propagate(False)

    # -- Player Display Tab -- #
    tk.Label(player_tab, text = "Players", font = main_font).pack(side = tk.TOP, padx = 4, pady = 4,  fill = "x")
    player_tab.pack(side = tk.TOP, anchor = "w", padx = 4, pady = 4, ipadx = 128, ipady = 256)
    root.mainloop()

# -- Main Game Menu -- #
@enforce_types
def innit_game_menu(data: Game_Data) -> None:
    tk.Label(root, text = "Game Menu", font = ("Airial", 16), bg = "#d3d3d3").pack(side = tk.TOP, fill = "x", pady = 4)

@enforce_types
def selection_menu(data: Game_Data, user: str) -> None:
    root.mainloop()

@enforce_types
def voting_menu(data: Game_Data, user: str) -> None:
    root.mainloop()