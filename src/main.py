# -- Imports -- #
import json
import os
from utils import *
from tkinter import messagebox
from time import sleep
from classes_and_types import *
from menu.menu import *
from game_loop_functions import *
import abilities as a

# -- Functions -- #
@enforce_types
def selection_coindition(data: Game_Data, role: Role, name: str) -> bool:
    singular = (not ("singular" in role.ability_type and (role.selected_target)))
    targets = role.ability.targets > 0 

    universal_conditions = singular and targets and data.playing
    use_ability = True

    if "on_demand" in role.ability_type and universal_conditions:
        sleep(1)
        use_ability = messagebox.askyesno("Ability", f"Does {name}, the {role.name} want to use their ability ({role.ability.__name__})?")
        role.ability_cancel = not use_ability

    return universal_conditions and use_ability

# -- Main -- #
@enforce_types
def main() -> None:
    # -- Game Data -- #
    role_functions: dict[str, Callable] = {name : getattr(a, name) for name in dir(a) if callable(getattr(a, name))}
    roles: dict[str, Role] = {}

    # -- File Handling -- #
    path: str = "Roles"
    roles_load_priority: list[list[Role]] = []

    for item in os.listdir(path):
        with open(path + "/" + item, 'r') as file:
            data: dict = json.load(file)  
            data["ability"] = role_functions[data["ability"]]
            data["_alignment"] = data["alignment"]
            del data["alignment"]
            roles[data["name"]] = Role(**data, targets = [], information = [], visited_by = [])

    with open("load_priority.json", 'r') as file:
        data: dict = json.load(file)
        for value in data.values():
            roles_load_priority.append(value)

    with open("defaults.txt") as file:
        string_data: str = file.readline()
        name_data: list[str] = string_data.split(", ")

    entries = Menu_Entry([], list(roles.values()))

    # -- Menu -- #
    setup_menu(entries, roles_load_priority, name_data, len(roles_load_priority))

    # -- Player Organisation -- #
    game_data = Game_Data(Players(entries.assign_roles()), deepcopy(roles["Mafia"]), deepcopy(roles["Villager"]))
    game_data.init(a.vote)

    # -- Game Loop -- #
    innit_game_menu()

    while game_data.playing:
        # -- Game Loop -- #
        for name, role in game_data.alive_players.items():
            if selection_coindition(game_data, role, name):
                selection_menu(game_data, name)

        if game_data.playing:
            use_abilities(game_data)
            life_death_sort(game_data)

            information(game_data)
            remove_round_data(game_data)

            pack_alive_and_dead(game_data, game_data.vote_role)
            use_death_abilities(game_data)
            life_death_sort(game_data)
            remove_round_data(game_data)

            check_for_victory(game_data)

            if game_data.playing:
                voted_out: str = voting_menu(game_data)

                if game_data.playing:
                    game_data.players[voted_out].voted_out(game_data.players)
            
                life_death_sort(game_data)
                use_vote_abiltities(game_data)
                use_death_abilities(game_data)
                life_death_sort(game_data)

                if game_data.playing:
                    pack_alive_and_dead(game_data, game_data.vote_role)

        check_for_victory(game_data)

    winners = []

    for name, role in game_data.players.items():
        if role.solo_win:
            winners.append(f"{name} as {role.name}")

    if game_data.good_win: winners.append("The Good Team!")
    if game_data.evil_win: winners.append("The Evil Team!")

    show_victory(winners)
    
# -- On Run -- #
if __name__ == "__main__":
    playing: bool = True
    while playing == True:
        main()
        playing = messagebox.askyesno("Restart", "Do you want to play another round?")