# -- Imports -- #
import json
import os
from utils import *
from classes_and_types import *
from menu.menu import *
import abilities as a

# -- Functions -- #
@enforce_types
def get_jester(players: Players) -> Players:
    jesters = {}
    for key, role in players.items():
        if role.key == "Jester": 
            jesters[key] = role
    return jesters

@enforce_types
def select_player(user: str, players: Players) -> None:
    target_num: int = players[user].ability.targets

    for i in range(target_num):
        players[user].targets.append(valid_input_list(f"{user} is {players[user].name}, pick a player to {players[user].ability.__name__}", "Invalid Player!", [*players.keys()]).lower().capitalize())

# -- Main -- #
@enforce_types
def main() -> None:
    # -- Game Data -- #
    role_functions: dict[str, Callable] = {name : getattr(a, name) for name in dir(a) if callable(getattr(a, name))}
    roles: dict[str, Role] = {}
    role_priority_list: list[str] = []

    # -- File Handling -- #
    path: str = "Roles"
    roles_load_priority: list[list[Role]] = []


    for item in os.listdir(path):
        with open(path + "/" + item, 'r') as file:
            data: dict = json.load(file)  
            data["ability"] = role_functions[data["ability"]]
            data["_alignment"] = data["alignment"]
            del data["alignment"]
            roles[data["name"]] = Role(**data, targets = [])

    with open("load_priority.json", 'r') as file:
        data: dict = json.load(file)
        for value in data.values():
            roles_load_priority.append(value)

    entries = Menu_Entry([], list(roles.values()))

    # -- Menu -- #
    setup_menu(entries, roles_load_priority)

def play():
    # -- Player Organisation -- #
    players = Players({role.name.capitalize(): role for role in roles}) # -- Replace Later - #
    priority = Players(dict(sorted(players.items(), key = lambda item: item[1].priority)))
    good_aligned = Players({name: role for name, role in players.items() if role.alignment})
    evil_aligned = Players({name: role for name, role in players.items() if not role.alignment})
    alive_players = players.deepcopy()
    dead_players = Players({})

    # -- Filter The Sherrif To Be Last -- #
    sherrif: dict[str, Role] = {name: role for name, role in players.items() if role.name == "Sherrif"}
    sherrif_name = next(iter(sherrif))
    del players[sherrif_name]
    players[sherrif_name] = sherrif[sherrif_name]

    # -- Game Loop -- #
    playing: bool = True
    jester_win: bool = False
    good_win: bool = False

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