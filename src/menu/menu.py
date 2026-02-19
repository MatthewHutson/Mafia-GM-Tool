# -- Imports -- #
from utils import *
from menu.menu_classes import *
from menu.mimi_stand_counter import counter_init
from menu.card_index import card_index
from tkinter import messagebox
from copy import deepcopy
import tkinter as tk
import sys
import json

# -- Setup Global Variables -- #
root: tk.Tk = tk.Tk()

MIN_PLAYERS: int = 4
max_players: int = 4

bg_2: str = "#d3d3d3"

players: list[Player_Select_Frame] = []
role_player_dict: dict[int, list[list[Role]]] = {}
role_adjust_boundaries: int = []

player_margin = tk.Frame(root)
player_tab = tk.Frame(player_margin, bg = bg_2)

input_frame = tk.Frame(player_margin)
name_entry: tk.Entry = tk.Entry(input_frame)

settings_frame = tk.Frame(root)

role_frame = tk.Frame(root, bg = bg_2)
role_row_frames = Role_Row(role_frame)

main_font: tuple[str, int] = ("Airial", 10)

# -- Game Menu Global Vars -- #
alive_margin = None
alive_canvas = None
dead_margin = None
dead_canvas = None
alive_frames = []
dead_frames = []
selected_players = []

# -- Functions -- #
@enforce_types
def new_load_system() -> None:
    role_load_priority: dict[int, list[list[Role]]] = {}

    with open("load_priority.json", 'r') as file:
        data: dict = json.load(file)
        for key, value in data.items():
            role_load_priority[int(key)] = value

    globals()["role_player_dict"] = role_load_priority
    globals()["max_players"] = len(list(role_load_priority.values())[-1])
    globals()["role_adjust_boundaries"] = list(role_load_priority.keys())

@enforce_types
def get_roles_by_players(role_load_priority: dict[int, list[list[Role]]], ascending: bool = True) -> list[list[Role]]:
    keys = list(role_load_priority.keys())
    offset = int(ascending)

    for i in range(0, len(keys)):
        key = keys[i]

        if key > len(players) + offset:
            if i >= 1:
                key = keys[i - 1]
            else:
                key = 4
            break
        elif key == len(players) + offset:
            break
        
    return role_load_priority[key]

@enforce_types
def role_boundary_reset(roles: list[list[Role]]) -> None:
    i = 0
    shuffle(roles)
    for role_icon in role_row_frames.icon_list:
        role_icon.re_init(roles[i])
        i += 1

    role_row_frames.shuffle()

@enforce_types
def role_boundary_reset_for_icons() -> None:
    role_boundary_reset(get_roles_by_players(role_player_dict, False))

@enforce_types
def add_player(players: list[Player_Select_Frame], roles: list[list[Role]], entries: Menu_Entry, name: str, role_adjust_flag: bool = True) -> None:
    try:
        if not name:
            raise ValueError
        
        name_entry.delete(0, tk.END)

        if len(players) >= max_players: raise IndexError
        
        for frame in players:
            if frame == capitalise_words(name): raise NameError

        add_role_tile(len(players), roles, entries)
        player_frame = Player_Select_Frame(name, player_tab, main_font, players, role_row_frames)
        players.append(player_frame)

        role_boundary_reset(roles)

    except IndexError:
        messagebox.showwarning("Warning", "You Have Reached The Maximum Number of Players!")
    except NameError:
        messagebox.showwarning("Warning", "A Player With This Name Already Exists!")
    except ValueError:
        pass

@enforce_types
def get_roles_by_defaults(role_load_priority: dict[int, list[list[Role]]], default_names: list[str]) -> list[list[Role]]:
    return role_load_priority[len(default_names)]

@enforce_types
def add_defaults(players: list[tk.Label], role_load_priority: dict[int, list[list[Role]]], entries: Menu_Entry, default_names: list[str]) -> None:
    roles = get_roles_by_defaults(role_load_priority, default_names)
    for i in range(len(players)):
        players[0].delete()

    for name in default_names:
        add_player(players, roles, entries, name)

@enforce_types
def add_player_from_entry(players: list[tk.Label], roles: list[list[Role]], entries: Menu_Entry, max_players: int) -> None:
    user_input: str = name_entry.get().strip()
    add_player(players, roles, entries, user_input)

@enforce_types
def add_role_tile(player_count: int, roles: list[Role], entries: Menu_Entry) -> None:
    role_icon = Role_Icon(roles[player_count], main_font, entries)
    role_row_frames.add_item(role_icon)

@enforce_types
def clear(root: tk.Tk) -> None:
    clear_widgets(root)
    root.unbind("<Return>")

    for i in range(len(players)):
        players[0].delete()

@enforce_types
def clear_widgets(root: Has_Widget_Children) -> None:
    try:
        for widget in root.winfo_children():
            widget.pack_forget()
            clear_widgets(widget)
    except: pass

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
def life_or_death_selection(data: Game_Data, role: Role) -> bool:
    correct: bool = True

    for player in selected_players:
        correct = correct and data.players[player].currently_alive == role.ability.target_living

    return correct

@enforce_types
def confirm_selection(data: Game_Data, role: Role) -> None:
    correct_lives = life_or_death_selection(data, role)
    plural_targets: str = f"target{"s" if role.ability.targets > 1 else ""}"

    if len(selected_players) == role.ability.targets and correct_lives:
        if messagebox.askyesno("Confirm Selection", f"Are you sure you want to select {selected_players}?"):
            root.quit()
    else:
        if role.name != "Voting":
            if role.ability.target_living:
                messagebox.showwarning("Warning", f"You must select {role.ability.targets} alive {plural_targets}!")
            else:
                messagebox.showwarning("Warning", f"You must select {role.ability.targets} dead {plural_targets}!")
        else:
            messagebox.showwarning("Warning", "You can only vote 1 alive player out!")

@enforce_types
def quit(data: Game_Data) -> None:
    if messagebox.askyesno("Confirm Selection", "Are you sure you want to end the game?"):
        data.playing = False
        root.quit()

@enforce_types
def skip() -> None:
    if messagebox.askyesno("Confirm Selection", "Are you sure you want to skip the vote?"):
        root.quit()

@enforce_types
def terminate() -> None:
    if messagebox.askyesno("Confirm Selection", "Are you sure you want to quit?"):
        sys.exit()

# -- Setup Menu -- #
@enforce_types
def setup_menu(entries: Menu_Entry, default_names: list[str]) -> None:
    # -- File Handling -- #
    new_load_system()
    role_row_frames.get_role_reset_function(role_boundary_reset_for_icons)
    role_row_frames.add_entries(entries)

    # -- Specific Functions --  #
    @enforce_types
    def add_enter_press(event) -> None:
        add_player_from_entry(players, get_roles_by_players(role_player_dict), entries, max_players)
        
    # -- Menu -- #
    clear(root)
    root.resizable(False, False)
    root.geometry("1216x512")
    root.title("Mafia Game")
    tk.Label(root, text = "Player Selection", font = ("Airial", 16), bg = bg_2).pack(side = tk.TOP, fill = "x", pady = 4)

    # -- Add Player Input -- #
    tk.Label(input_frame, text = "Name:").pack(side = tk.LEFT, padx = 8, pady = 8)
    tk.Button(input_frame, text = "Defaults", command = lambda: add_defaults(players, role_player_dict, entries, default_names), bg = "#5D9FF0", highlightbackground = "#4980C4", activebackground = "#4980C4", fg = "#ffffff", activeforeground = "#ffffff").pack(side = tk.RIGHT, padx = 8, pady = 8)
    tk.Button(input_frame, text = "Add", command = lambda: add_player_from_entry(players, get_roles_by_players(role_player_dict), entries, max_players), bg = "#00ff00", highlightbackground = "#00cd00", activebackground = "#00aa00").pack(side = tk.RIGHT, padx = 8, pady = 8)
    name_entry.pack(fill = "x", padx = 8, pady = 8, ipady = 12)
    name_entry.bind("<Return>", add_enter_press)
    input_frame.pack_propagate(False)
    input_frame.pack(side = tk.TOP, anchor = "w", ipadx = 158, ipady = 20)

    # -- Settings Buttons -- #
    start = tk.Button(settings_frame, text = "Start", command = lambda: start_confirm(entries), bg = "#5D9FF0", activebackground = "#4980C4", fg = "#ffffff", activeforeground = "#ffffff")
    exit = tk.Button(settings_frame, text = "Quit", command = terminate, bg = "#E03636", activebackground = "#8B2B2B", fg = "#ffffff", activeforeground = "#ffffff")
    random_button = tk.Button(settings_frame, text = "Randomise", command = role_boundary_reset_for_icons, bg = "#48f748", activebackground = "#55E036", fg = "#000000", activeforeground = "#000000")
    start.pack(side = tk.RIGHT, ipady = 3, ipadx = 16, padx = 4)
    exit.pack(side = tk.RIGHT, ipady = 3, ipadx = 16, padx = 4)
    random_button.pack(side = tk.RIGHT, ipady = 3, ipadx = 16, padx = 4)

    # -- Mimi Stand Counter -- #
    counter_init(root, settings_frame, (8, 3), (4, 0), tk.LEFT)

    # -- Card Index -- #
    index_access_button = tk.Button(settings_frame, text = "Card Index", command = lambda: card_index(root, bg_2, main_font, entries), bg = "#C65DF0", activebackground = "#C049C4", fg = "#ffffff", activeforeground = "#ffffff")
    index_access_button.pack(side = tk.RIGHT, ipadx = 8, ipady = 3, padx = 4)

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
def init_game_menu(entries: Menu_Entry, data: Game_Data) -> None:
    tk.Label(root, text = "Game Menu", font = ("Airial", 16), bg = bg_2).pack(side = tk.TOP, fill = "x", pady = 4)
    
    globals()["alive_margin"] = tk.Frame(root, bg = bg_2)
    globals()["dead_margin"] = tk.Frame(root, bg = bg_2)

    tk.Label(alive_margin, text = "Alive Players").pack(side = tk.TOP, padx = 4, pady = 4, fill = "x", ipady = 4)
    tk.Label(dead_margin, text = "Dead Players").pack(side = tk.TOP, padx = 4, pady = 4, fill = "x", ipady = 4)
    
    #globals()["alive_canvas"] = Vertical_Scroll_Frame(alive_margin)
    #globals()["dead_canvas"] = Vertical_Scroll_Frame(dead_margin)

    #alive_canvas.pack(side = tk.TOP, padx = 4, pady = 4, fill = "both")
    #dead_canvas.pack(side = tk.TOP, padx = 4, pady = 4, fill = "both")

    alive_margin.pack(side = tk.LEFT, padx = 4, pady = 4, fill = "y", ipadx = 128)
    dead_margin.pack(side = tk.RIGHT, padx = 4, pady = 4, fill = "y", ipadx = 128)

    pack_alive_and_dead(data, data.vote_role) # -- Prevents Popup before the first night -- #
    card_index(root, bg_2, main_font, entries, data) # -- Gives Role Card Before Popups Appear -- #

@enforce_types
def selection_menu(data: Game_Data, entries: Menu_Entry, user: str, target: str = "", can_recurse: bool = True) -> None:
    # -- Setup -- #
    globals()["selected_players"] = []

    try: 
        # -- To Check if Ability Selection Or Vote Selection -- #
        if target == "":
            role = data.players[user]
        else:
            # -- To Consider recurse_targets -- #
            role = data.players[target]

    except: role = data.vote_role

    # -- Sub Functions -- #
    @enforce_types
    def enter_pressed(event) -> None:
        confirm_selection(data, role)

    # -- Subroutine Main -- #
    pack_alive_and_dead(data, role)
    action_frame = tk.Frame(root, bg = bg_2)


    if user == "none":
        text = "Voting Menu"
    else:
        if target == "":
            text =  f"{user} is the {role.name}. They need to select {role.ability.targets} target{"s" if role.ability.targets > 1 else ""}"
        else:
            text = f"{user} is channeling the power of {role.name}. They need to select {role.ability.targets} target{"s" if role.ability.targets > 1 else ""}"

    action_label = tk.Label(action_frame, font = main_font, text = text)
    confirm_frame = tk.Frame(action_frame, bg = bg_2)
    info_frame = tk.Frame(action_frame, bg = bg_2)

    action_label.pack(side = tk.TOP, fill = "x", padx = 4, pady = 4, ipady = 4)

    tk.Button(confirm_frame, text = "Confirm Choices", command = lambda: confirm_selection(data, role), bg = "#5D9FF0", activebackground = "#4980C4", fg = "#ffffff", activeforeground = "#ffffff").pack(side = tk.LEFT, ipadx = 16, ipady = 8, padx = 4)
    tk.Button(confirm_frame, text = "End Game", command = lambda: quit(data), bg = "#E03636", activebackground = "#8B2B2B", fg = "#ffffff", activeforeground = "#ffffff").pack(side = tk.RIGHT, ipadx = 16, ipady = 8, pady = 4, padx = 4)

    # -- Card Index -- #
    index_access_button = tk.Button(info_frame, text = "Card Index", command = lambda: card_index(root, bg_2, main_font, entries, data), bg = "#C65DF0", activebackground = "#C049C4", fg = "#ffffff", activeforeground = "#ffffff", width = 18)
    index_access_button.pack(side = tk.LEFT, ipady = 8, padx = 4)

    # -- Mimi Stand Counter -- #
    counter_init(root, info_frame, (16, 8), (4, 4), tk.RIGHT)

    root.bind("<Return>", enter_pressed)

    info_frame.pack(side = tk.BOTTOM, fill = "x", ipady = 1)
    confirm_frame.pack(side = tk.BOTTOM, fill = "x", ipady = 1)
    action_frame.pack(side = tk.TOP, fill = "both", padx = 4, pady = 4, expand = True)

    # -- Vote Skip Button -- #
    if user == "none":
        tk.Button(action_frame, text = "Skip Vote", command = skip, bg = "#64F05D", activebackground = "#64C449", fg = "#000000", activeforeground = "#000000").pack(side = tk.BOTTOM, ipadx = 16, ipady = 8, padx = 4, pady = 2, anchor = "sw")

    root.mainloop()

    try: role = data.players[user] # -- To Consider recurse_targets -- #
    except: pass

    if data.playing:
        action_frame.pack_forget()
        action_label.pack_forget()

    role.selected_target = True
    role.targets = role.targets + deepcopy(selected_players)

    for player in selected_players:
        data.players[player].visited_by.append(user)
        shuffle(data.players[player].visited_by)

    if "recurse_targets" in role.ability_type and can_recurse and data.playing:
        for i in range(len(selected_players)):
            player = selected_players[i]
            if data.players[player].ability.targets > 0 and not data.players[user].recursion_fuck_up:
                selection_menu(data, entries, user, player, False)

@enforce_types
def voting_menu(data: Game_Data, entries: Menu_Entry) -> str:
    selection_menu(data, entries, "none")

    if data.playing and len(selected_players) > 0:
        return selected_players[0]
    else: 
        return "none"

@enforce_types
def information(data: Game_Data) -> None:
    for player, role in data.alive_players.items():
        info: str = "\n"
        count: int = 0

        for item in role.information:
            info += f"\n #{count + 1}: " + item
            count += 1
        
        if info != "\n":
            messagebox.showinfo("Info", f"{player} is told: {info}")
        else:
            messagebox.showinfo("Info", f"{player} is told nothing!")