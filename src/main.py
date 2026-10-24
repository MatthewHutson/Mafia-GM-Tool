# -- Imports -- #
from __future__ import annotations
import json
import os
from utils import *
from tkinter import messagebox
from time import sleep
from classes_and_types import *
from menu.menu import *
from menu.life_and_death_popup import remove_instances
from menu.settings import load_settings
from game_loop_functions import *
from game import game, win_con_sort
from pathlib import Path
import abilities as a

# -- Main -- #
@enforce_types
def main() -> None:
    # -- Game Data -- #
    role_functions: dict[str, a.Ability] = {ability.__name__: ability() for ability in all_subclasses(Ability)}
    roles: dict[str, Role] = {}
    ability_distribution: dict[str, float] = {}

    # -- File Handling -- #
    for key, value in role_functions.items():
        ability_distribution[key] = float(value.p)

    with open("roles.json", "r") as file:
        loaded_role_data: dict = json.load(file)

    unpack_role_types(roles, loaded_role_data["good_roles"], role_functions, True)
    unpack_role_types(roles, loaded_role_data["evil_roles"], role_functions, False)
    unpack_role_types(roles, loaded_role_data["neutral_roles"], role_functions, None)

    if not Path("defaults.txt").is_file():
        with open("defaults.txt", "w") as file:
            pass
   
    with open("defaults.txt", "r") as file:
        string_data: str = file.readline()

        if string_data[-1:] == "\n":
            string_data = string_data[:-1]

        name_data: list[str] = string_data.split(", ")

    entries = Menu_Entry([], list(roles.values()), deepcopy(list(roles.keys())), [], [], load_settings())

    # -- Menu -- #
    normal_load = setup_menu(entries, name_data)
    in_play_roles: dict[str, Role] = deepcopy({name: roles[name] for name in get_all_roles()})

    # -- Player Organisation -- #
    game_data = Game_Data(Players(entries.assign_roles()), roles, role_functions, ability_distribution, [], entries, in_play_roles)

    if normal_load:
        game_data.init()
    else:
        game_data.load_from_json_backup()

    try:
        game(game_data, entries, normal_load)

        for name, role in game_data.players.items():
            if "game_end" in role.ability_type:
                role.ability(name, game_data)
            if "game_end" in role.secondary_ability.ability_type:
                role.secondary_ability(name, game_data) 

        winners = []
        win_steal: bool = False
        ordered_players: Players = win_con_sort(data)

        for name, role in ordered_players.items():
            if role.solo_win:
                if not role.team_win_condition:
                    if role.channeled_role == None:
                        winners.append(f"\n{name} as the {role.name}")
                        win_steal = win_steal or game_data.win_steal
                    else:
                        winners.append(f"\n{name} as the {role.name} chanelling the {role.channeled_role}")
                else:
                    # -- For Mayor & Chancellor -- #
                    if role.currently_alive:
                        game_data.good_win = role.alignment
                        game_data.evil_win = not role.alignment

        if not win_steal:
            if game_data.good_win: winners.append("\nThe Good Team!")
            if game_data.evil_win: winners.append("\nThe Evil Team!")

        show_victory(winners, game_data.turn_count)
        remove_instances()

    except Exception as e:
        game_data.backup_to_json()
        #raise e
    
# -- On Run -- #
if __name__ == "__main__":
    playing: bool = True
    while playing == True:
        try:
            main()
            playing = messagebox.askyesno("Game Over", "Do you want to play another round?", icon = "question")
        except Exception as e:
            playing = False
            raise e