# -- Imports -- #
from utils import *
from menu.menu_classes import *
from menu.mimi_stand_counter import counter_init
from menu.card_index import card_index, destroy_card_index
from menu.settings import display_settings, remove_instances, update_settings
from menu.timer import create_timer, delete_timer
from menu.loading_system import *
from tkinter import messagebox
from copy import deepcopy
from random import shuffle
from pathlib import Path
import tkinter as tk
import sys
import json

# -- Setup Global Variables -- #
root: tk.Tk = tk.Tk()

MIN_PLAYERS: int = 4
max_players: int = 4

# -- Colour Schemes -- #
bg_1: str  = "#F0F0F0"
bg_2: str = "#d3d3d3"
text_colour: str = "#000000"

root.config(bg = bg_1)

players: list[Player_Select_Frame] = []

# -- Role Load System V3 -- #
evil_role_dict: dict[int, list[list[Role]]] = {}
other_role_dict: dict[int, list[list[Role]]] = {}
guarenteed_roles: list[Role] = []

# -- Tkitner Vars -- #
player_margin = tk.Frame(root, bg = bg_1)
player_tab = tk.Frame(player_margin, bg = bg_2)

input_frame = tk.Frame(player_margin, bg = bg_1)
name_entry: tk.Entry = tk.Entry(input_frame, bg = bg_2, fg = text_colour)

settings_frame = tk.Frame(root, bg = bg_1)

role_frame = tk.Frame(root, bg = bg_2)
role_row_frames = Role_Row(role_frame, bg_2)

main_font: tuple[str, int] = ("Airial", 10)

global_entries: Menu_Entry = None

# -- Game Menu Global Vars -- #
alive_frames = []
dead_frames = []
selected_players = []
load_from_backup: bool = False

def none(): pass

@enforce_types
def get_roles_by_players(offset: int = 1) -> list[list[Role]]:
    return get_roles(len(players), offset)

@enforce_types
def get_roles(player_count: int, offset: int = 1) -> list[list[str]]:
    return new_get_roles(player_count, global_entries.settings, offset)

@enforce_types
def role_boundary_reset(roles: list[list[Role]]) -> None:
    global global_entries

    if global_entries != None:
        global_entries.current_roles_lists = []

    i = 0
    role_temp = roles

    shuffle(role_temp)
    for role_icon in role_row_frames.icon_list:
        role_icon.re_init(role_temp[i])
        i += 1

    role_row_frames.shuffle()

@enforce_types
def role_boundary_reset_for_icons() -> None:
    role_boundary_reset(get_roles_by_players(0))

@enforce_types
def add_player(players: list[Player_Select_Frame], roles: list[list[Role]], entries: Menu_Entry, name: str) -> None:
    try:
        if not name:
            raise ValueError
        
        name_entry.delete(0, tk.END)
        
        for frame in players:
            if frame == capitalise_words(name): raise NameError

        add_role_tile(len(players), roles, entries)
            
        player_frame = Player_Select_Frame(name, player_canvas, main_font, players, role_row_frames, role_boundary_reset_for_icons, bg_2, text_colour)
        player_canvas.update()
        player_canvas.scroll_all()
        players.append(player_frame)

        role_boundary_reset(roles)

    except OverflowError as e:
        messagebox.showwarning("Warning", "You Have Reached The Maximum Number of Players!", icon = "warning")
    except NameError:
        messagebox.showwarning("Warning", "A Player With This Name Already Exists!", icon = "warning")
    except ValueError:
        pass

@enforce_types
def get_roles_by_defaults(default_names: list[str]) -> list[list[Role]]:
    return get_roles(len(default_names), 0)

@enforce_types
def add_defaults(players: list[tk.Label], entries: Menu_Entry, default_names: list[str]) -> None:
    roles = get_roles_by_defaults(default_names)
    for i in range(len(players)):
        players[0].delete()

    for name in default_names:
        add_player(players, roles, entries, name)

@enforce_types
def add_player_from_entry(players: list[tk.Label], roles: list[list[Role]], entries: Menu_Entry, max_players: int) -> None:
    user_input: str = name_entry.get().strip()
    add_player(players, roles, entries, user_input)

@enforce_types
def add_role_tile(player_count: int, roles: list[list[str]], entries: Menu_Entry) -> None:
    role_icon = Role_Icon(roles[player_count], main_font, entries)
    role_row_frames.add_item(role_icon)

@enforce_types
def clear() -> None:
    delete_timer()
    destroy_card_index()

    clear_widgets(root)

    root.unbind("<Return>")

    for i in range(len(players)):
        players[0].delete(False)

@enforce_types
def clear_widgets(root: Has_Widget_Children) -> None:
    try:
        for widget in root.winfo_children():
            widget.pack_forget()
            clear_widgets(widget)
    except Exception as e: 
        messagebox.showerror("Error", f"An error occurred while clearing the menu: \n\n{e}", icon = "error")

@enforce_types
def get_data(root: tk.Tk, entries: Menu_Entry) -> None:
    entries.filter_roles([str(icon) for icon in role_row_frames.icon_list])
    entries.players = [str(frame) for frame in players]
    clear()
    root.quit()

@enforce_types
def start_confirm(entries: Menu_Entry) -> None:
    if len(players) < 4:
        messagebox.showerror("Error", "You Need at Least 4 Players to Start!", icon = "error")
    else:
        if messagebox.askyesno("Confirm Choice", "Do you wish to start the game?", icon = "question"):
            remove_instances()
            get_data(root, entries)

@enforce_types
def pack_alive_and_dead(data: Game_Data, active_role: Role, number_of_targets: int) -> None:
    for i in range(len(alive_frames)):
        frame = alive_frames[0]
        alive_frames.remove(frame)
        frame.delete()

    for i in range(len(dead_frames)):
        frame = dead_frames[0]
        dead_frames.remove(frame)
        frame.delete()

    for name in data.alive_players.keys():
        player_frame = Player_Role_Frame(name, data, alive_canvas, main_font, selected_players, active_role, number_of_targets, pack_alive_and_dead, bg_2, text_colour)
        alive_frames.append(player_frame)

    for name in data.dead_players.keys():
        player_frame = Player_Role_Frame(name, data, dead_canvas, main_font, selected_players, active_role, number_of_targets, pack_alive_and_dead, bg_2, text_colour)
        dead_frames.append(player_frame)

    alive_canvas.update()
    dead_canvas.update()
    alive_canvas.scroll_all()
    dead_canvas.scroll_all()

@enforce_types
def life_or_death_selection(data: Game_Data, ability: Ability, role: Role) -> bool:
    correct: bool = True

    for player in selected_players:
        correct = correct and data.players[player].currently_alive == ability.target_living

    return correct

@enforce_types
def no_double_down(data: Game_Data, role: Role, ability: Ability) -> bool:
    if isinstance(role.previous_targets, list) and data.settings["Double Down"] == 0:
        for target in selected_players:
            if target in role.previous_targets and not ability.can_pick_same_target:
                messagebox.showwarning("Warning", f"You Cannot Pick The Same Target Twice!", icon = "warning")
                return False
    
    return True

@enforce_types
def confirm_selection(data: Game_Data, role: Role, is_primary_ability: bool) -> None:
    if is_primary_ability:
        ability = role.ability
    else:
        ability = role.secondary_ability

    correct_lives = life_or_death_selection(data, ability, role)
    plural_targets: str = f"target{"s" if ability.targets > 1 else ""}"

    can_pick_that_target: bool = no_double_down(data, role, ability)

    if len(selected_players) == ability.targets and correct_lives and can_pick_that_target:
        if messagebox.askyesno("Confirm Selection", f"Are you sure you want to select {selected_players}?", icon = "question"):
            root.quit()
    elif can_pick_that_target:
        if role.name != "Voting":
            if ability.target_living:
                messagebox.showwarning("Warning", f"You must select {ability.targets} alive {plural_targets}!", icon = "warning")
            else:
                messagebox.showwarning("Warning", f"You must select {ability.targets} dead {plural_targets}!", icon = "warning")
        else:
            messagebox.showwarning("Warning", "You can only vote 1 alive player out!", icon = "warning")

@enforce_types
def menu_quit(data: Game_Data) -> None:
    if messagebox.askyesno("Confirm Selection", "Are you sure you want to end the game?", icon = "question"):
        data.playing = False
        root.quit()
        clear()
        delete_timer()

@enforce_types
def skip() -> None:
    global selected_players
    if messagebox.askyesno("Confirm Selection", "Are you sure you want to skip the vote?", icon = "question"):
        selected_players = []
        root.quit()

@enforce_types
def terminate() -> None:
    if messagebox.askyesno("Confirm Selection", "Are you sure you want to quit?", icon = "question"):
        sys.exit()

@enforce_types
def load_backup() -> None:
    global load_from_backup
    if Path("backup.json").is_file():
        if messagebox.askyesno("Load Backup", "Do You Want To Load The Previous Backup And Thus Continue From That State?", icon = "question", default = "no"):
            load_from_backup = True
            remove_instances()
            clear()
            root.quit()
    else:
        messagebox.showerror("Error", "No Backup Exists!", icon = "error")

# -- Setup Menu -- #
@enforce_types
def setup_menu(entries: Menu_Entry, default_names: list[str]) -> bool:
    # -- Globals Handling -- #
    global global_entries, player_canvas, load_from_backup, max_players
    global_entries = entries
    load_from_backup = False

    # -- File Handling -- #
    max_players = load_role_data()
    entries.all_roles_lists = get_all_role_lists()
    role_row_frames.get_role_reset_function(role_boundary_reset_for_icons)
    role_row_frames.add_entries(entries)

    # -- Specific Functions --  #
    @enforce_types
    def add_enter_press(event) -> None:
        add_player_from_entry(players, get_roles_by_players(), entries, max_players)
        
    # -- Menu -- #
    clear()
    root.resizable(False, False)
    root.geometry("1216x512")
    root.title("Mafia Game")
    tk.Label(root, text = "Player Selection", font = ("Airial", 16), bg = bg_2, fg = text_colour).pack(side = tk.TOP, fill = "x", pady = 4)

    # -- Add Player Input -- #
    tk.Label(input_frame, text = "Name:", bg = bg_1, fg = text_colour).pack(side = tk.LEFT, padx = 8, pady = 8)
    tk.Button(input_frame, text = "Defaults", command = lambda: add_defaults(players, entries, default_names), bg = "#5D9FF0", highlightbackground = "#4980C4", activebackground = "#4980C4", fg = "#ffffff", activeforeground = "#ffffff").pack(side = tk.RIGHT, padx = 8, pady = 8)
    tk.Button(input_frame, text = "Add", command = lambda: add_player_from_entry(players, get_roles_by_players(), entries, max_players), bg = "#00ff00", highlightbackground = "#00cd00", activebackground = "#00aa00").pack(side = tk.RIGHT, padx = 8, pady = 8)
    name_entry.pack(fill = "x", padx = 8, pady = 8, ipady = 12)
    name_entry.bind("<Return>", add_enter_press)
    input_frame.pack_propagate(False)
    input_frame.pack(side = tk.TOP, anchor = "w", ipadx = 158, ipady = 20)

    # -- Menu Progression Buttons -- #
    start = tk.Button(settings_frame, text = "Start", command = lambda: start_confirm(entries), bg = "#5D9FF0", activebackground = "#4980C4", fg = "#ffffff", activeforeground = "#ffffff")
    restore_backup = tk.Button(settings_frame, text = "Load Backup", command = load_backup, bg = "#A25DF0", activebackground = "#8249C4", fg = "#ffffff", activeforeground = "#ffffff")
    exit = tk.Button(settings_frame, text = "Quit", command = terminate, bg = "#E03636", activebackground = "#8B2B2B", fg = "#ffffff", activeforeground = "#ffffff")
    start.pack(side = tk.RIGHT, ipady = 3, ipadx = 16, padx = 4)
    restore_backup.pack(side = tk.RIGHT, ipady = 3, ipadx = 16, padx = 4)
    exit.pack(side = tk.RIGHT, ipady = 3, ipadx = 16, padx = 4)

    # -- Mimi Stand Counter -- #
    counter_init(root, settings_frame, (8, 3), (4, 0), tk.LEFT)

    # -- Settings Button -- #
    settings_button = tk.Button(settings_frame, text = "Settings", command = lambda: display_settings(root, bg_1, bg_2, text_colour, entries), bg = "#CACACA", activebackground = "#AFAFAF", fg = "#000000", activeforeground = "#ffffff")
    settings_button.pack(side = tk.RIGHT, ipady = 3, ipadx = 8, padx = 4)

    # -- Randomise Button -- #
    random_button = tk.Button(settings_frame, text = "Randomise", command = role_boundary_reset_for_icons, bg = "#48f748", activebackground = "#55E036", fg = "#000000", activeforeground = "#000000")
    random_button.pack(side = tk.RIGHT, ipady = 3, ipadx = 8, padx = 4)

    # -- Card Index -- #
    index_access_button = tk.Button(settings_frame, text = "Card Index", command = lambda: card_index(root, bg_2, main_font, text_colour, entries), bg = "#C65DF0", activebackground = "#C049C4", fg = "#ffffff", activeforeground = "#ffffff")
    index_access_button.pack(side = tk.RIGHT, ipadx = 8, ipady = 3, padx = 4)

    # -- Role Selection -- #
    tk.Label(role_frame, text = "Roles", font = main_font, bg = bg_1, fg = text_colour).pack(side = tk.TOP, padx = 4, pady = 4, fill = "x")

    # -- Main Partitions -- #
    player_margin.pack(side = tk.LEFT, anchor = "nw")
    settings_frame.pack(side = tk.TOP, anchor = "n", padx = 4, pady = 4, fill = "x")
    role_frame.pack(side = tk.TOP, anchor = "nw", fill = "both", padx = 4, pady = 4, expand = True)

    # -- Setting Partitions -- #
    role_frame.pack_propagate(False)

    # -- Player Display Tab -- #
    tk.Label(player_tab, text = "Players", font = main_font, bg = bg_1, fg = text_colour).pack(side = tk.TOP, padx = 4, pady = 4,  fill = "x")
    player_tab.pack(side = tk.TOP, anchor = "w", padx = 4, pady = 4, ipadx = 128, ipady = 256, expand = False)
    player_tab.update()
    player_tab.pack_propagate(False)
    player_canvas = Vertical_Scroll_Frame(master = player_tab, bg = bg_1, bg_2 = bg_2)
    root.mainloop()

    return not load_from_backup

# -- Main Game Menu -- #
@enforce_types
def init_game_menu(entries: Menu_Entry, data: Game_Data) -> None:
    global alive_margin, alive_canvas, dead_margin, dead_canvas
    player_margin_size: int = 160

    tk.Label(root, text = "Game Menu", font = ("Airial", 16), bg = bg_2, fg = text_colour).pack(side = tk.TOP, fill = "x", pady = 4)
    
    alive_margin = tk.Frame(root, bg = bg_2)
    dead_margin = tk.Frame(root, bg = bg_2)

    tk.Label(alive_margin, text = "Alive Players", bg = bg_1, fg = text_colour).pack(side = tk.TOP, padx = 4, pady = 4, fill = "x", ipady = 4)
    tk.Label(dead_margin, text = "Dead Players", bg = bg_1, fg = text_colour).pack(side = tk.TOP, padx = 4, pady = 4, fill = "x", ipady = 4)
    
    alive_canvas = Vertical_Scroll_Frame(master = alive_margin, bg  = bg_1, bg_2 = bg_2, pack = False)
    dead_canvas = Vertical_Scroll_Frame(master = dead_margin, bg = bg_1, bg_2 = bg_2, pack = False)

    alive_margin.pack(side = tk.LEFT, padx = 4, pady = 4, fill = "y", ipadx = player_margin_size)
    dead_margin.pack(side = tk.RIGHT, padx = 4, pady = 4, fill = "y", ipadx = player_margin_size)

    alive_margin.update()
    dead_margin.update()
    alive_margin.pack_propagate(False)
    dead_margin.pack_propagate(False)

    alive_canvas.pack(side = tk.TOP, padx = 4, pady = 4, fill = "both", expand = True)
    dead_canvas.pack(side = tk.TOP, padx = 4, pady = 4, fill = "both", expand = True)

    pack_alive_and_dead(data, data.vote_role, 0) # -- Prevents Popup before the first night -- #
    card_index(root, bg_2, main_font, text_colour, entries, data) # -- Gives Role Card Before Popups Appear -- #

@enforce_types
def selection_menu_create(data: Game_Data, entries: Menu_Entry, user: str, target: str = "", is_primary_ability: bool = True, functional: bool = True) -> tuple[tk.Frame, tk.Label, Ability]:
    # -- Setup -- #
    global selected_players
    selected_players = []

    try: 
        # -- To Check if Ability Selection Or Vote Selection -- #
        if target == "":
            role = data.players[user]
        else:
            # -- To Consider recurse_targets -- #
            role = data.players[target]

    except: role = data.vote_role

    # -- Handling Secondary Abilitities -- #
    if is_primary_ability:
        ability = role.ability
    else:
        ability = role.secondary_ability

    # -- Sub Functions -- #
    @enforce_types
    def enter_pressed(event) -> None:
        confirm_selection(data, role, is_primary_ability)

    # -- Subroutine Main -- #
    if functional: pack_alive_and_dead(data, role, ability.targets)
    action_frame = tk.Frame(root, bg = bg_2)

    if user == "none":
        text = "Voting Menu"
    else:
        if target == "":
            text =  f"{user} is the {role.name} using {ability.__name__}. Select {ability.targets} target{"s" if ability.targets != 1 else ""}"
        else:
            text = f"{user} is using the power of {role.name} ({role.ability.__name__}). Select {ability.targets} target{"s" if ability.targets != 1 else ""}"

    action_label = tk.Label(action_frame, font = main_font, text = text, bg = bg_1, fg = text_colour)
    confirm_frame = tk.Frame(action_frame, bg = bg_2)
    info_frame = tk.Frame(action_frame, bg = bg_2)
    vote_frame = tk.Frame(action_frame, bg = bg_2)
    ability_frame = tk.Frame(action_frame, bg = bg_2)

    action_label.pack(side = tk.TOP, fill = "x", padx = 4, pady = 4, ipady = 4)

    if functional: tk.Button(confirm_frame, text = "Confirm Choices", command = lambda: confirm_selection(data, role, is_primary_ability), bg = "#5D9FF0", activebackground = "#4980C4", fg = "#ffffff", activeforeground = "#ffffff").pack(side = tk.LEFT, ipadx = 16, ipady = 8, padx = 4)
    tk.Button(confirm_frame, text = "End Game", command = lambda: menu_quit(data), bg = "#E03636", activebackground = "#8B2B2B", fg = "#ffffff", activeforeground = "#ffffff").pack(side = tk.RIGHT, ipadx = 16, ipady = 8, pady = 4, padx = 4)

    # -- Card Index -- #
    index_access_button = tk.Button(info_frame, text = "Card Index", command = lambda: card_index(root, bg_2, main_font, text_colour, entries, data), bg = "#C65DF0", activebackground = "#C049C4", fg = "#ffffff", activeforeground = "#ffffff", width = 18)
    index_access_button.pack(side = tk.LEFT, ipady = 8, padx = 4)

    # -- Mimi Stand Counter -- #
    counter_init(root, info_frame, (16, 8), (4, 4), tk.RIGHT)

    root.bind("<Return>", enter_pressed)

    info_frame.pack(side = tk.BOTTOM, fill = "x", ipady = 1)
    confirm_frame.pack(side = tk.BOTTOM, fill = "x", ipady = 1)
    vote_frame.pack(side = tk.TOP, fill = "x", ipady = 1)
    action_frame.pack(side = tk.TOP, fill = "both", padx = 4, pady = 4, expand = True)
    ability_frame.pack(side = tk.LEFT, fill = "x", padx = 32, ipady = 96, expand = True)

    # -- Ability Frames -- #
    if user != "none":
        primary_frame = tk.Frame(ability_frame, bg = bg_1, relief = "raised", borderwidth = 4)
        secondary_frame = tk.Frame(ability_frame, bg = bg_1, relief = "raised", borderwidth = 4)

        primary_frame.pack(side = tk.LEFT, ipadx = 64, fill = "y")
        secondary_frame.pack(side = tk.RIGHT, ipadx = 64, fill = "y")

        primary_frame.pack_propagate(False)
        secondary_frame.pack_propagate(False)

        primary_name = tk.Label(primary_frame, text = f"Primary Ability:\n{ability.__name__} ({ability.targets})", bg = bg_2)
        primary_name.pack(side = tk.TOP, fill = "x", padx = 2, pady = 2, ipady = 10, expand = False)
        primary_name.update()
        size: tuple = (primary_name.winfo_width(), 3)

        Role_Icon([data.get_role_by_ability(ability, user).name], main_font, entries, size, command = none, data = data).pack(primary_frame, side = tk.TOP)
        tk.Label(primary_frame, text = f"Card:\n{data.get_card_by_role(data.get_role_by_ability(ability, user))}", bg = bg_2).pack(side = tk.BOTTOM, fill = "both", padx = 2, pady = 2, expand = True, anchor = "w")

        if role.secondary_ability is not None:
            if role.secondary_ability.__name__.lower() != "none":
                tk.Label(secondary_frame, text = f"Secondary Ability:\n{role.secondary_ability.__name__} ({role.secondary_ability.targets})", bg = bg_2).pack(side = tk.TOP, fill = "x", padx = 2, pady = 2, ipady = 10, expand = False, anchor = "w")
                Role_Icon([data.get_role_by_ability(role.secondary_ability, user).name], main_font, entries, size, command = none, data = data).pack(secondary_frame, side = tk.TOP)
                tk.Label(secondary_frame, text = f"Card:\n{data.get_card_by_role(data.get_role_by_ability(role.secondary_ability))}", bg = bg_2).pack(side = tk.BOTTOM, fill = "both", padx = 2, pady = 2, expand = True, anchor = "w")
            else:
                tk.Label(secondary_frame, text = f"Secondary Ability:\nNone (0)", bg = bg_2).pack(side = tk.TOP, fill = "both", padx = 2, pady = 2, ipady = 10, expand = False, anchor = "w")
        else:
            tk.Label(secondary_frame, text = f"Secondary Ability:\nNone (0)", bg = bg_2).pack(side = tk.TOP, fill = "both", padx = 2, pady = 2, ipady = 10, expand = False, anchor = "w")

    # -- Vote Skip Button -- #
    if user == "none":
        tk.Button(vote_frame, text = "Skip Vote", command = skip, bg = "#64F05D", activebackground = "#64C449", fg = text_colour, activeforeground = text_colour).pack(side = tk.LEFT, ipadx = 24, ipady = 8, padx = 4, pady = 2, anchor = "sw")

    # -- Timer Button -- #
    create_timer(vote_frame, 300, main_font, (12, 2), (4, 2), tk.RIGHT)

    return action_frame, action_label, ability

@enforce_types
def selection_menu_destroy(data: Game_Data, entries: Menu_Entry, user: str, action_frame: tk.Frame, action_label: tk.Label, ability: Ability, is_primary_ability: bool = True, can_recurse: bool = True, functional: bool = True) -> None:
    try: role = data.players[user] # -- To Consider recurse_targets -- #
    except: pass

    if data.playing:
        action_frame.pack_forget()
        action_label.pack_forget()

    if functional:
        try:
            role.selected_target = True
            role.targets = role.targets + deepcopy(selected_players)
        except:
            pass

        for player in selected_players:
            data.players[player].visited_by.append(user)
            shuffle(data.players[player].visited_by)

        if "recurse_targets" in ability.ability_type and can_recurse and data.playing:
            for i in range(len(selected_players)):
                player = selected_players[i]
                if data.players[player].ability.targets > 0 and not data.players[user].recursion_fuck_up:
                    selection_menu(data, entries, user, player, is_primary_ability, False)

@enforce_types
def selection_menu(data: Game_Data, entries: Menu_Entry, user: str, target: str = "", is_primary_ability: bool = True, can_recurse: bool = True) -> None:
    global selected_players
    action_frame, action_label, ability = selection_menu_create(data, entries, user, target, is_primary_ability)
    root.mainloop()
    selection_menu_destroy(data, entries, user, action_frame, action_label, ability, is_primary_ability, can_recurse)

@enforce_types
def voting_menu(data: Game_Data, entries: Menu_Entry) -> str:
    selection_menu(data, entries, "none")

    if data.playing and len(selected_players) > 0:
        return selected_players[0]
    else: 
        return "none"

@enforce_types
def information(data: Game_Data, tell_nothing: bool = True, first_wave: bool = True) -> None:
    for player, role in data.alive_players.items():
        info: str = "\n"
        count: int = 0

        if role.statuses.silenced & first_wave:
            role.information.append("You have been Silenced!")

        for item in role.information:
            info += f"\n #{count + 1}: " + item
            count += 1
        
        if info != "\n":
            messagebox.showinfo("Info", f"{player} is told: {info}", icon = "info")
        elif tell_nothing:
            messagebox.showinfo("Info", f"{player} is told nothing!", icon = "info")

        role.information = []