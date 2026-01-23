# -- Imports -- #
import json
import os
from copy import deepcopy
from utils import *
from classes import *
import abilities as a

# -- Functions -- #
@enforce_types
def get_jester(players: dict[str, Role]) -> dict[str, Role]:
    jesters = {}
    for key, role in players.items():
        if role.key == "Jester": 
            jesters[key] = role
    return jesters

@enforce_types
def select_player(user: str, players: dict[str, Role]) -> None:
    target_num: int = players[user].ability.targets

    for i in range(target_num):
        players[user].targets.append(valid_input_list(f"{user} is {players[user].name}, pick a player to {players[user].ability.__name__}", "Invalid Player!", [*players.keys()]).lower().capitalize())

# -- Main -- #
@enforce_types
def main() -> None:
    # -- Game Data -- #
    role_functions: dict[str, Callable] = {name : getattr(a, name) for name in dir(a) if callable(getattr(a, name))}
    roles: list[Role] = []

    # -- File Handling -- #
    path = "Roles"

    for item in os.listdir(path):
        with open(path + "/" + item, 'r') as file:
            data: dict = json.load(file)  
            data["ability"] = role_functions[data["ability"]]
            roles.append(Role(**data, targets = []))

    # -- Player Organisation -- #
    players: dict[str, Role] = {role.name.capitalize(): role for role in roles} # -- Replace Later - #
    priority: dict[str, Role] = dict(sorted(players.items(), key = lambda item: item[1].priority))
    good_aligned: dict[str, Role] = {name: role for name, role in players.items() if role.alignment}
    evil_aligned: dict[str, Role] = {name: role for name, role in players.items() if not role.alignment}
    alive_players: dict[str, Role] = deepcopy(players)
    dead_players: dict[str, Role] = {}

    # -- Filter The Sherrif To Be Last -- #
    sherrif: dict[str, Role] = {name: role for name, role in players.items() if role.name == "Sherrif"}
    sherrif_name = next(iter(sherrif))
    del players[sherrif_name]
    players[sherrif_name] = sherrif[sherrif_name]

    # -- Game Loop -- #
    playing: bool = True
    jester_win = False
    good_win = False

    while playing:
        # -- Game Loop -- #
        for name, role in alive_players.items():
            if not (role.ability_type == "singular" and role.used_ability):
                select_player(name, players)

        for name, role in priority.items():
            role.ability(name, players)

        for name, role in players.items():
            if not role.currently_alive:
                del alive_players[name]
                dead_players[name] = role

        for role in players.values():
            for i in range(len(role.targets)):
                del role.targets[0]

        printLine(f"Alive Players: {[name for name in alive_players.keys()]}")
        printLine(f"Dead Players: {[name for name in dead_players.keys()]}")

        # -- Checks For Win Conditions -- #
        if len(evil_aligned) == 0:
            playing = False
            good_win = True
        if jester_win or len(evil_aligned) == len(good_aligned):
            playing = False

    if jester_win: printLine("The Jester Wins!")
    elif good_win: printLine("Good Team Wins!")
    else: printLine("Mafia Wins!")
    
# -- On Run -- #
if __name__ == "__main__":
    main()