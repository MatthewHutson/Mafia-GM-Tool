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
    game_data = Game_Data(Players(entries.assign_roles()))
    game_data.innit(a.none, a.vote)

    # -- Game Loop -- #
    playing: bool = True
    good_win: bool = False

    innit_game_menu(game_data)

    while playing:
        # -- Game Loop -- #
        for name, role in game_data.alive_players.items():
            if (not (role.ability_type == "singular" and role.used_ability)) and role.ability.targets > 0:
                selection_menu(game_data, name)

        use_abilities(game_data)
        life_death_sort(game_data)

        information(game_data)
        remove_round_data(game_data)

        voted_out: str = voting_menu(game_data)
        game_data.players[voted_out].die(game_data.players)

        life_death_sort(game_data)

        pack_alive_and_dead(game_data, game_data.vote_role)

        # -- Checks For Win Conditions -- #
        if len(game_data.evil_aligned) == 0:
            playing = False
            good_win = True

        if (len(game_data.evil_aligned) == 1 and len(game_data.good_aligned) == 1) or len(game_data.evil_aligned) > len(game_data.good_aligned):
            playing = False

    winners = []

    for name, role in game_data.players.items():
        if role.solo_win:
            winners.append(f"{name} as {role.name}")

    if good_win: winners.append("The Good Team!")
    else: winners.append("The Evil Team!")

    show_victory(winners)
    
# -- On Run -- #
if __name__ == "__main__":
    main()