# -- Imports -- #
from utils import *
from menu.menu_classes import *
from tkinter import messagebox
from copy import deepcopy
import tkinter as tk
import sys

# -- Setup Global Variables -- #
root: tk.Tk = tk.Tk()

MAX_PLAYERS: int = 7
MIN_PLAYERS: int = 4

bg_2 = "#d3d3d3"

players: list[Player_Select_Frame] = []

player_margin = tk.Frame(root)
player_tab = tk.Frame(player_margin, bg = bg_2)

input_frame = tk.Frame(player_margin)
name_entry: tk.Entry = tk.Entry(input_frame)

settings_frame = tk.Frame(root)

role_frame = tk.Frame(root, bg = bg_2)
role_row_frames = Role_Row(role_frame)

main_font = ("Airial", 10)

# -- Game Menu Global Vars -- #
alive_margin = None
dead_margin = None
alive_frames = []
dead_frames = []
selected_players = []

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

@enforce_types
def pack_alive_and_dead(data: Game_Data, active_role: Role) -> None:
    for i in range(len(alive_frames)):
        frame = alive_frames[0]
        alive_frames.remove(frame)
        frame.delete()

    for i in range(len(dead_frames)):
        frame = dead_frames[0]
        dead_frames.remove(frame)
        frame.delete()

    for name, Role in data.alive_players.items():
        player_frame = Player_Role_Frame(name, data, alive_margin, main_font, selected_players, active_role)
        alive_frames.append(player_frame)

    for name, Role in data.dead_players.items():
        player_frame = Player_Role_Frame(name, data, dead_margin, main_font, selected_players, active_role)
        dead_frames.append(player_frame)

@enforce_types
def confirm_selection(role: Role) -> None:
    if len(selected_players) == role.ability.targets:
        if messagebox.askyesno("Confirm Selection", f"Are you sure you want to select {selected_players}?"):
            root.quit()
    else:
        if role.name != "Voting":
            messagebox.showwarning("Warning", f"{role.name} must select {role.ability.targets} target{"s" if role.ability.targets > 1 else ""}!")
        else:
            messagebox.showwarning("Warning", "You can only vote 1 person out!")

@enforce_types
def quit(data: Game_Data) -> None:
    if messagebox.askyesno("Confirm Selection", "Are you sure you want to end the game?"):
        data.playing = False
        root.quit()

@enforce_types
def terminate() -> None:
    if messagebox.askyesno("Confirm Selection", "Are you sure you want to quit?"):
        sys.exit()

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
    tk.Label(root, text = "Player Selection", font = ("Airial", 16), bg = bg_2).pack(side = tk.TOP, fill = "x", pady = 4)

    # -- Add Player Input -- #
    tk.Label(input_frame, text = "Name:").pack(side = tk.LEFT, padx = 8, pady = 8)
    add: tk.Button = tk.Button(input_frame, text = "Add", command = lambda: add_player(players, all_roles, entries), bg = "#00ff00", highlightbackground = "#00cd00", activebackground = "#00aa00").pack(side = tk.RIGHT, padx = 8, pady = 8)
    name_entry.pack(fill = "x", padx = 8, pady = 8, ipady = 12)
    name_entry.bind("<Return>", enter_pressed)
    input_frame.pack_propagate(False)
    input_frame.pack(side = tk.TOP, anchor = "w", ipadx = 158, ipady = 20)

    # -- Settings Buttons -- #
    start = tk.Button(settings_frame, text = "Start", command = lambda: start_confirm(entries), bg = "#5D9FF0", activebackground = "#4980C4", fg = "#ffffff", activeforeground = "#ffffff")
    exit = tk.Button(settings_frame, text = "Quit", command = terminate, bg = "#E03636", activebackground = "#8B2B2B", fg = "#ffffff", activeforeground = "#ffffff")
    start.pack(side = tk.RIGHT, ipady = 3, ipadx = 16, padx = 4)
    exit.pack(side = tk.RIGHT, ipady = 3, ipadx = 16, padx = 4)

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
def innit_game_menu() -> None:
    tk.Label(root, text = "Game Menu", font = ("Airial", 16), bg = bg_2).pack(side = tk.TOP, fill = "x", pady = 4)
    globals()["alive_margin"] = tk.Frame(root, bg = bg_2)
    globals()["dead_margin"] = tk.Frame(root, bg = bg_2)
    tk.Label(alive_margin, text = "Alive Players").pack(side = tk.TOP, padx = 4, pady = 4, fill = "x", ipady = 4)
    tk.Label(dead_margin, text = "Dead Players").pack(side = tk.TOP, padx = 4, pady = 4, fill = "x", ipady = 4)
    alive_margin.pack(side = tk.LEFT, padx = 4, pady = 4, fill = "y", ipadx = 104)
    dead_margin.pack(side = tk.RIGHT, padx = 4, pady = 4, fill = "y", ipadx = 104)

@enforce_types
def selection_menu(data: Game_Data, user: str) -> None:
    # -- Setup -- #
    globals()["selected_players"] = []

    try: role = data.players[user]
    except: role = data.vote_role

    # -- Sub Functions -- #
    @enforce_types
    def enter_pressed(event) -> None:
        confirm_selection(role)

    # -- Subroutine Main -- #
    pack_alive_and_dead(data, role)
    action_frame = tk.Frame(root, bg = bg_2)

    if user == "none":
        text = "Voting Menu"
    else:
        text =  f"{user} is the {role.name}. They need to select {role.ability.targets} target{"s" if role.ability.targets > 1 else ""}"

    action_label = tk.Label(action_frame, font = main_font, text = text)
    confirm_frame = tk.Frame(action_frame, bg = bg_2)

    action_label.pack(side = tk.TOP, fill = "x", padx = 4, pady = 4, ipady = 4)

    tk.Button(confirm_frame, text = "Confirm Choices", command = lambda: confirm_selection(role), bg = "#5D9FF0", activebackground = "#4980C4", fg = "#ffffff", activeforeground = "#ffffff").pack(side = tk.LEFT, ipadx = 16, ipady = 8, padx = 4)
    tk.Button(confirm_frame, text = "End Game", command = lambda: quit(data), bg = "#E03636", activebackground = "#8B2B2B", fg = "#ffffff", activeforeground = "#ffffff").pack(side = tk.RIGHT, ipadx = 16, ipady = 8, pady = 4, padx = 4)
    confirm_frame.bind("<Return>", enter_pressed)

    confirm_frame.pack(side = tk.BOTTOM, fill = "x", ipady = 1)

    action_frame.pack(side = tk.TOP, fill = "both", padx = 4, pady = 4, expand = True)

    root.mainloop()

    if data.playing:
        action_frame.pack_forget()
        action_label.pack_forget()

    role.selected_target = True
    role.targets = deepcopy(selected_players)

@enforce_types
def voting_menu(data: Game_Data) -> str:
    selection_menu(data, "none")

    if data.playing:
        return selected_players[0]
    else: 
        return "none"

@enforce_types
def information(data: Game_Data) -> None:
    for player, role in data.players.items():
        info = ""

        for item in role.information:
            info += "" + item
        
        if info != "":
            messagebox.showinfo("Info", f"{player} is told: {info}")