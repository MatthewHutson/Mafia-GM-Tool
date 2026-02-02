# -- Imports -- #
from utils import *
from classes_and_types import Role, Players
from game_loop_functions import *

# -- Roles -- #
@add_attributes(targets = 0)
@enforce_types
def none(user: str, players: Players) -> None:
    pass

@add_attributes(targets = 1)
@enforce_types
def vote(user: str, players: Players) -> None:
    pass

@add_attributes(targets = 1)
@enforce_types
def reveal(user: str, players: Players) -> None:
    target: str = players[user].targets[0]
    alignment: bool = players[user].poisoned ^ players[target].alignment

    if alignment: players[user].information.append(f"{target} is GOOD!")
    else: players[user].information.append(f"{target} is EVIL!")

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
def Jester(user: str, players: Players) -> None:
    if players[user].was_voted_out: 
        players[user].solo_win = True

@add_attributes(targets = 1)
@enforce_types
def stop_vote(user: str, players: Players) -> None: 
    if not players[user].solo_win:
        players[user].solo_win = True
        if players[players[user].targets[0]].was_voted_out:
            players[user].solo_win = False

        if not players[players[user].targets[0]].currently_alive and players[user].solo_win:
            role_switch(players, user, Role("Villager", none, True, False, 999, 999, "passive", [], []))

@add_attributes(targets = 1)
@enforce_types
def execute(user: str, players: Players) -> None:
    if not players[user].solo_win:
        if players[players[user].targets[0]].was_voted_out:
            players[user].solo_win = True

        if not (players[players[user].targets[0]].currently_alive or players[user].solo_win):
            role_switch(players, user, Role("Villager", none, True, False, 999, 999, "passive", [], []))

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

@add_attributes(targets = 1)
@enforce_types
def telepathy(user: str, players: Players) -> None:
    target: str = players[user].targets[0]
    role: Role = players[target]
    is_lover: bool = role.linked

    players[user].information.append(f"{target} is {role.name}!")
    if is_lover:
        players[user].information.append(f"{target} is linked to another player!")
