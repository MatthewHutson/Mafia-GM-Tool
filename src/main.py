# -- Imports -- #
import json
import os
from utils import *
from classes_and_types import *
from menu.menu import *
from game_loop_functions import *
import abilities as a

# -- Functions -- #
@enforce_types
def get_jester(players: Players) -> Players:
    jesters = {}
    for key, role in players.items():
        if role.name == "Jester": 
            jesters[key] = role
    return jesters

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
            roles[data["name"]] = Role(**data, targets = [], information = [])

    with open("load_priority.json", 'r') as file:
        data: dict = json.load(file)
        for value in data.values():
            roles_load_priority.append(value)

    entries = Menu_Entry([], list(roles.values()))

    # -- Menu -- #
    setup_menu(entries, roles_load_priority)

    # -- Player Organisation -- #
    game_data = Game_Data(Players(entries.assign_roles()), deepcopy(roles["Mafia"]))
    game_data.innit(a.none, a.vote)

    # -- Game Loop -- #
    innit_game_menu()

    while game_data.playing:
        # -- Game Loop -- #
        for name, role in game_data.alive_players.items():
            if (not ("singular" in role.ability_type and (role.selected_target))) and role.ability.targets > 0 and game_data.playing:
                selection_menu(game_data, name)

        if game_data.playing:
            use_abilities(game_data)
            life_death_sort(game_data)

            information(game_data)
            remove_round_data(game_data)

            check_for_victory(game_data)

            if game_data.playing:
                voted_out: str = voting_menu(game_data)

                if game_data.playing:
                    game_data.players[voted_out].voted_out(game_data.players)
            
                life_death_sort(game_data)
                use_vote_abiltities(game_data)

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
    main()