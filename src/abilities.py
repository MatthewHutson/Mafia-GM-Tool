# -- Imports -- #
from utils import *
from classes_and_types import Role, Game_Data
from game_loop_functions import *
from time import sleep

# -- Roles -- #
@add_attributes(targets = 0, target_living = True)
@enforce_types
def none(user: str, data: Game_Data) -> None:
    pass

@add_attributes(targets = 1, target_living = True)
@enforce_types
def vote(user: str, data: Game_Data) -> None:
    pass

@enforce_types
def reveal(user: str, data: Game_Data) -> None:
    target: str = data.players[user].targets[0]
    alignment: bool = data.players[user].poisoned ^ data.players[target].alignment

    if alignment: data.players[user].information.append(f"{target} is GOOD!")
    else: data.players[user].information.append(f"{target} is EVIL!")

@enforce_types
def endure(user: str, data: Game_Data) -> None:
    if not data.players[user].poisoned: data.players[user].protected = True

@enforce_types
def protect(user: str, data: Game_Data) -> None:
    target: str = data.players[user].targets[0]
    if not data.players[user].poisoned: data.players[target].protected = True

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

@enforce_types
def jester(user: str, data: Game_Data) -> None:
    if data.players[user].was_voted_out: 
        data.players[user].solo_win = True

@enforce_types
def stop_vote(user: str, data: Game_Data) -> None: 
    if not data.players[user].solo_win:
        data.players[user].solo_win = True
        if data.players[data.players[user].targets[0]].was_voted_out:
            data.players[user].solo_win = False

        if not data.players[data.players[user].targets[0]].currently_alive and data.players[user].solo_win:
            role_switch(data, user, Role("Villager", none, True, False, 999, 999, "passive", [], [], []))

@enforce_types
def execute(user: str, data: Game_Data) -> None:
    if not data.players[user].solo_win:
        if data.players[data.players[user].targets[0]].was_voted_out:
            data.players[user].solo_win = True

        if not (data.players[data.players[user].targets[0]].currently_alive or data.players[user].solo_win):
            role_switch(data, user, Role("Villager", none, True, False, 999, 999, "passive", [], [], []))

@enforce_types
def poison(user: str, data: Game_Data) -> None:
    if data.players[user].name != "Mafia":
        target: str = data.players[user].targets[0]
        data.players[target].poisoned = True

@enforce_types
def kill(user: str, data: Game_Data) -> None:
    target: str = data.players[user].targets[0]
    data.players[target].die(data.players)

@enforce_types
def telepathy(user: str, data: Game_Data) -> None:
    if data.players[user].name != "Mafia":
        target: str = data.players[user].targets[0]
        role: Role = data.players[target]
        is_lover: bool = role.linked

        data.players[user].information.append(f"{target} is {role.name}!")
        if is_lover:
            data.players[user].information.append(f"{target} is linked to another player!")

@enforce_types
def stalk(user: str, data: Game_Data) -> None:
    visitors = []

    if not data.players[user].poisoned:
        target: str = data.players[user].targets[0]
        visitors = data.players[target].visited_by

    target_str = f"{target} was visited by "
        
    for player in visitors:
        if player != user:
            target_str += player + ", "

    if len(visitors) > 0:
        target_str = target_str[:-2]
    else:
        target_str += " nobody"

    data.players[user].information.append(target_str)

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

@enforce_types
def channel(user: str, data: Game_Data) -> None:
    if len(data.players[user].targets) > 0:
        target = data.players[user].targets[0]
        del data.players[user].targets[0]

        if not data.players[target].currently_alive and not data.players[user].recursion_fuck_up:
            data.players[user].ability = deepcopy(data.players[target].ability)
            data.players[user].channeled_role = data.players[target].name

            extra_types = ["singular"]

            for type in extra_types:
                if type in data.players[user].ability_type:
                    data.players[user].ability.ability_type.append(type)     

            data.players[user].team_win_condition = data.players[target].team_win_condition

        else:
            data.players[user].used_ability = False
            data.players[user].targets = []
            data.players[user].recursion_fuck_up = True
            messagebox.showerror("Error", "The Necromancer Cannot Channel an ALive Player!\nThey Shall Regain Their Ability!")

@enforce_types
def resurrect(user: str, data: Game_Data) -> None:
    if len(data.players[user].targets) > 0:
        target = data.players[data.players[user].targets[0]]
        target.revive()

@enforce_types
def ambush(user: str, data: Game_Data) -> None:
    target = data.players[user].targets[0]
    try:
        new_target = data.players[target].visited_by[0]
        bystanders = deepcopy(data.players[target].visited_by[1:])

        bystanders.remove(user)

        data.players[user].targets = [new_target]
        kill(user, data)

        for player in bystanders:
            data.players[player].information.append(f"{user} attempted to ambush {new_target}!")
    except:
        pass

@enforce_types
def mayor(user: str, data: Game_Data) -> None:
    if data.playing:
        if not data.players[user].solo_win:
            sleep(1)
            if messagebox.askyesno("Mayor", "Has The Mayor Revealed Themselves?"):
                data.players[user].solo_win = True
    else:
        data.players[user].solo_win = len(data.players) == data.players[user].alternative_end_count

@enforce_types
def gamble(user: str, data: Game_Data) -> None:
    user: Role = data.players[user]
    if user.ability_cancel:
        user.secondary_ability(user, data)

    else:
        user.secondary_ability = data.random_ability
        
        if "instant" in user.secondary_ability.ability_type:
            user.secondary_ability(user, data)

@enforce_types
def instant_death(user: str, data: Game_Data) -> None:
    data.players[user].die()