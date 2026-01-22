# -- Imports -- #
from utils import enforce_types, valid_input_list
from classes import Role

# -- Roles -- #
@enforce_types
def none(user: str, players: dict[str, Role]) -> None:
    pass

@enforce_types
def reveal(user: str, players: dict[str, Role]) -> str:
    target: str = valid_input_list(f"{user} Pick a player to investigate: ", "That's Not A Player!", [*players.keys()])
    alignment: bool = players[user].poisoned ^ players[target].alignment

    if alignment: return f"{user} is revealed that {target} is good."
    else: return f"{user} is revealed that {target} is evil."

def soldier(user: str, players: dict[str, Role]) -> None:
    if not players[user].poisoned: players[user].protected = True

@enforce_types
def link(user: str, players: dict[str, Role]) -> None:
    link_1: str = valid_input_list(f"{user} Pick the first player to Link!: ", "That's Not A Player!", [*players.keys()])
    link_2: str = valid_input_list(f"{user} Pick the second player to Link!: ", "That's Not A Player!",[*players.keys()])
    
    players[link_1].linked = True
    players[link_2].linked = True

@enforce_types
def Jester(user: str, players: dict[str, Role]) -> None: pass

@enforce_types
def kill(user: str, players: dict[str, Role]) -> None:
    target: str = valid_input_list(f"{user} Pick a player to kill!: ", "That's Not A Player!", [*players.keys()])

    if not (players[user].poisoned) or (players[target].is_protected): 
        players[target].kill()