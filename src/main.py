# -- Imports -- #
from __future__ import annotations
import json
import os
from utils import *
from tkinter import messagebox
from time import sleep
from classes_and_types import *
from menu.menu import *
from menu.card_index import card_init
from menu.settings import load_settings
from game_loop_functions import *
from game import game
from pathlib import Path
import abilities as a

# -- Main -- #
@enforce_types
def main() -> None:
    # -- Game Data -- #
    role_functions: dict[str, a.Ability] = {ability.__name__: ability() for ability in Ability.__subclasses__()}
    roles: dict[str, Role] = {}
    ability_distribution: dict[str, float] = {}

    # -- File Handling -- #
    path: str = "Roles"

    for key, value in role_functions.items():
        ability_distribution[key] = float(value.p)

    for item in os.listdir(path):
        with open(path + "/" + item, 'r') as file:
            data: dict = json.load(file)

            ability_name: str = data["ability"]  
            data["ability"] = deepcopy(role_functions[ability_name])
            data["_alignment"] = data["alignment"]

            if "secondary_ability" in data.keys():
                secondary_name: str = data["secondary_ability"]
                data["secondary_ability"] = deepcopy(role_functions[secondary_name])

            del data["alignment"]

            data["abilities"] = {} #{0, data["ability"]}
            
            roles[data["name"]] = Role.new(**data)

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

    # -- Player Organisation -- #
    game_data = Game_Data(Players(entries.assign_roles()), roles, role_functions, ability_distribution, card_init(), entries)

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

        for name, role in game_data.players.items():
            if role.solo_win:
                if not role.team_win_condition:
                    if role.channeled_role == None:
                        winners.append(f"\n{name} as the {role.name}")
                    else:
                        winners.append(f"\n{name} as the {role.name} chanelling the {role.channeled_role}")
                else:
                    # -- For Mayor -- #
                    if role.currently_alive:
                        if role.alignment:
                            game_data.good_win = True
                            game_data.evil_win = False
                        elif not game_data.good_win:
                            game_data.good_win = False
                            game_data.evil_win = True

        if game_data.good_win: winners.append("\nThe Good Team!")
        if game_data.evil_win: winners.append("\nThe Evil Team!")

        show_victory(winners, game_data.turn_count)

    except Exception as e:
        game_data.backup_to_json()
        raise e
    
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