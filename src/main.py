# -- Imports -- #
import json
import os
from dataclasses import asdict
from pathlib import Path
from copy import deepcopy
from utils import *
from classes import *
import abilities as a

# -- Functions -- #
@enforce_types
def get_jester(self, players: dict[str, Role]) -> dict[str, Role]:
    jesters = {}
    for key, role in players.items():
        if role.key == "Jester": 
            jesters[key] = role
    return jesters

# -- Main -- #
@enforce_types
def main() -> None:
    # -- Game Data -- #
    players: dict[str, Role] = {}
    role_functions: dict[str, Callable] = {name : getattr(a, name) for name in dir(a) if callable(getattr(a, name))}
    roles: list = []

    # -- File Handling -- #
    path = "Roles"

    for item in os.listdir(path):
        with open(path + "/" + item, 'r') as file:
            data: dict = json.load(file)  
            data["ability"] = role_functions[data["ability"]]
            roles.append(Role(**data))
    
    #print(roles[0].ability(roles[0].name, {"Sherrif": roles[0]}))
    #roles[0].poisoned = True
    #print(roles[0].ability(roles[0].name, {"Sherrif": roles[0]}))
    
# -- On Run -- #
if __name__ == "__main__":
    main()