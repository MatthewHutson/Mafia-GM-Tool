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
def get_jester(self, players: dict[str, Any]) -> dict[str, Any]:
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
            roles.append(Role(**data, individual=True))
    
    print(roles)
    
# -- On Run -- #
if __name__ == "__main__":
    main()