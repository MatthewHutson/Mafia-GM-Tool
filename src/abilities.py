# -- Imports -- #
from utils import *
from classes_and_types import Role, Game_Data
from game_loop_functions import *

# -- Roles -- #
@add_attributes(targets = 0)
@enforce_types
def none(user: str, data: Game_Data) -> None:
    pass

@add_attributes(targets = 1)
@enforce_types
def vote(user: str, data: Game_Data) -> None:
    pass

@add_attributes(targets = 1)
@enforce_types
def reveal(user: str, data: Game_Data) -> None:
    target: str = data.players[user].targets[0]
    alignment: bool = data.players[user].poisoned ^ data.players[target].alignment

    if alignment: data.players[user].information.append(f"{target} is GOOD!")
    else: data.players[user].information.append(f"{target} is EVIL!")

@add_attributes(targets = 0)
@enforce_types
def endure(user: str, data: Game_Data) -> None:
    if not data.players[user].poisoned: data.players[user].protected = True

@add_attributes(targets = 1)
@enforce_types
def protect(user: str, data: Game_Data) -> None:
    target: str = data.players[user].targets[0]
    if not data.players[user].poisoned: data.players[target].protected = True

@add_attributes(targets = 2)
@enforce_types
def link(user: str, data: Game_Data) -> None:
    link_1: str = data.players[user].targets[0]
    link_2: str = data.players[user].targets[1]
    
    data.players[link_1].linked = True
    data.players[link_2].linked = True

    data.players[link_1].linker = user
    data.players[link_2].linker = user

    data.players[link_1].linked_to = link_2
    data.players[link_2].linked_to = link_1

@add_attributes(targets = 0)
@enforce_types
def Jester(user: str, data: Game_Data) -> None:
    if data.players[user].was_voted_out: 
        data.players[user].solo_win = True

@add_attributes(targets = 1)
@enforce_types
def stop_vote(user: str, data: Game_Data) -> None: 
    if not data.players[user].solo_win:
        data.players[user].solo_win = True
        if data.players[data.players[user].targets[0]].was_voted_out:
            data.players[user].solo_win = False

        if not data.players[data.players[user].targets[0]].currently_alive and data.players[user].solo_win:
            role_switch(data.players, user, Role("Villager", none, True, False, 999, 999, "passive", [], [], []))

@add_attributes(targets = 1)
@enforce_types
def execute(user: str, data: Game_Data) -> None:
    if not data.players[user].solo_win:
        if data.players[data.players[user].targets[0]].was_voted_out:
            data.players[user].solo_win = True

        if not (data.players[data.players[user].targets[0]].currently_alive or data.players[user].solo_win):
            role_switch(data.players, user, Role("Villager", none, True, False, 999, 999, "passive", [], [], []))

@add_attributes(targets = 1)
@enforce_types
def poison(user: str, data: Game_Data) -> None:
    if data.players[user].name != "Mafia":
        target: str = data.players[user].targets[0]
        data.players[target].poisoned = True

@add_attributes(targets = 1)
@enforce_types
def kill(user: str, data: Game_Data) -> None:
    target: str = data.players[user].targets[0]
    data.players[target].die(data.players)

@add_attributes(targets = 1)
@enforce_types
def telepathy(user: str, data: Game_Data) -> None:
    if data.players[user].name != "Mafia":
        target: str = data.players[user].targets[0]
        role: Role = data.players[target]
        is_lover: bool = role.linked

        data.players[user].information.append(f"{target} is {role.name}!")
        if is_lover:
            data.players[user].information.append(f"{target} is linked to another player!")

@add_attributes(targets = 1)
@enforce_types
def stalk(user: str, data: Game_Data) -> None:
    if not data.players[user].poisoned:
        target: str = data.players[user].targets[0]
        visitors = data.players[target].visited_by
        target_str = f"{target} was visited by "
        
        for player in visitors:
            if player != user:
                target_str += player + ", "

        target_str = target_str[:-2]

        data.players[user].information.append(target_str)

@add_attributes(targets = 0)
@enforce_types
def vengance(user: str, data: Game_Data) -> None:
    if not data.players[user].was_voted_out:
        data.players[user].ability.targets = 1
        selection_menu(data, user)

        target = data.players[user].targets[0]
        role = data.players[target]
        role.protected = False
        role.die(data.players)

    data.players[user].ability.targets = 0

@add_attributes(targets = 1)
@enforce_types
def channel(user: str, data: Game_Data) -> None:
    if len(data.players[user].targets) > 0:
        target = data.players[user].targets[0]
        del data.players[user].targets[0]

        if not data.players[target].currently_alive and not data.players[user].recursion_fuck_up:
            data.players[user].ability = data.players[target].ability

            data.players[user].ability_type.remove("on_demand")
            data.players[user].ability_type.remove("recurse_targets")
            
            for ability_type in data.players[target].ability_type:
                if ability_type == "on_death":
                    data.players[user].ability_type.append("on_death")
                if ability_type == "on_vote":
                    data.players[user].ability_type.append("on_vote")
                if ability_type == "on_demand":
                    data.players[user].ability_type.append("on_demand")
                if ability_type == "recurse_targets":
                    data.players[user].ability_type.append("recurse_targets")

        else:
            data.players[user].used_ability = False
            data.players[user].targets = []
            data.players[user].recursion_fuck_up = True
            messagebox.showerror("Error", "The Necromancer Cannot Channel an ALive Player!\nThey Shall Regain Their Ability!")
