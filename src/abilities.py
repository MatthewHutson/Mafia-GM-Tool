# -- Imports -- #
from utils import *
from classes_and_types import Role, Players

# -- Roles -- #
@add_attributes(targets = 0)
@enforce_types
def none(user: str, players: Players) -> None:
    pass

@add_attributes(targets = 1)
@enforce_types
def reveal(user: str, players: Players) -> None:
    target: str = players[user].targets[0]
    alignment: bool = players[user].poisoned ^ players[target].alignment

    if alignment: printLine(f"{user} is revealed that {target} is good.")
    else: printLine(f"{user} is revealed that {target} is evil.")

@add_attributes(targets = 0)
@enforce_types
def endure(user: str, players: Players) -> None:
    if not players[user].poisoned: players[user].protected = True

@add_attributes(targets = 1)
@enforce_types
def protect(user: str, players: Players) -> None:
    target: str = players[user].targets[0]
    if not players[user].poisoned: players[target].protected = True

@add_attributes(targets = 2)
@enforce_types
def link(user: str, players: Players) -> None:
    link_1: str = players[user].targets[0]
    link_2: str = players[user].targets[1]
    
    players[link_1].linked = True
    players[link_2].linked = True

    players[link_1].linker = user
    players[link_2].linker = user

    players[link_1].linked_to = link_2
    players[link_2].linked_to = link_1

@add_attributes(targets = 0)
@enforce_types
def Jester(user: str, players: Players) -> None: pass

@add_attributes(targets = 0)
@enforce_types
def Trial(user: str, players: Players) -> None: pass

@add_attributes(targets = 1)
@enforce_types
def poison(user: str, players: Players) -> None:
    target: str = players[user].targets[0]
    players[target].poisoned = True

@add_attributes(targets = 1)
@enforce_types
def kill(user: str, players: Players) -> None:
    target: str = players[user].targets[0]
    players[target].die(players)