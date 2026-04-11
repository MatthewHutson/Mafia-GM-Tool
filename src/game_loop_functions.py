# -- Imports -- #
from utils import *
from classes_and_types import *
from menu.menu import *
from menu.menu_classes import *

# -- Functions -- #
@enforce_types
def ability_conditions(role: Role, has_recursed: bool, data: Game_Data) -> bool:
    life = role in data.alive_players.values()
    not_cancel = (not role.ability_cancel or "passive" in role.ability_type or "alternate" in role.ability_type)
    singular = not ("singular" in role.ability_type and (role.used_ability))
    normal_activation = not ("on_vote" in role.ability_type or "on_death" in role.ability_type)

    if has_recursed:
        recurse_case = "activate_again" in role.ability_type
    else:
        recurse_case = True

    return life and singular and recurse_case and normal_activation and not_cancel

@enforce_types
def use_abilities(data: Game_Data, can_recurse: bool = True) -> None:
    priority: Players = data.priority

    for name, role in priority.items():
        if ability_conditions(role, not can_recurse, data):
            role.ability(name, data)

            if not (can_recurse or "secondary_ability" in role.ability_type) and not role.recursion_fuck_up:
                role.used_ability = True

    for name, role in priority.items():
        if "late" in role.ability.ability_type:
            role.ability(name, data)
        if "late" in role.secondary_ability.ability_type:
            role.secondary_ability(name, data)

@enforce_types
def life_death_sort(data: Game_Data) -> None:
    init_evil_alternative(data) # -- Ensures Mafia Evil Roles Will Have Kill Switch -- #
    for name, role in data.players.items():
        if name in data.alive_players.keys():
                if not role.currently_alive:
                    del data.alive_players[name]
                    data.dead_players[name] = role
                    if role.alignment:
                        del data.good_aligned[name]
                    else:
                        del data.evil_aligned[name]

        if name in data.dead_players.keys():
            if role.currently_alive:
                del data.dead_players[name]
                data.alive_players[name] = role
                if role.alignment:
                    data.good_aligned[name] = role
                else:
                    data.evil_aligned[name] = role

    revert_to_mafia(data)

@enforce_types
def remove_round_data(data: Game_Data, used_Death_ability: bool = False) -> None:
    for role in data.players.values():
        if (not "singular" in role.ability_type) and (used_Death_ability or not ("on_death" in role.ability_type or "on_vote" in role.ability_type)): 
            targets = role.targets
            for i in range(len(targets)):
                targets.pop(0)

        role.recursion_fuck_up = False
        role.poisoned = False
        role.protected = False
        role.information = []
        role.visited_by = []

@enforce_types
def update_all_targets(data: Game_Data) -> None:
    for role in data.players.values():
        role.update_targets()

@enforce_types
def select_player(user: str, players: Players) -> None: # -- Outdated To Be Replaced -- #
    target_num: int = players[user].ability.targets

    for i in range(target_num):
        players[user].targets.append(valid_input_list(f"{user} is {players[user].name}, pick a player to {players[user].ability.__name__}", "Invalid Player!", [*players.keys()]).lower().capitalize())

@enforce_types
def show_victory(victory_data: list[str]) -> None:
    victory_str = "Winners:\n"
    for item in victory_data:
        victory_str += item + ", "

    if len(victory_data) > 0:
        victory_str = victory_str[:-2]
    else:
        victory_str += "None"

    messagebox.showinfo("Game Over", victory_str)

@enforce_types
def check_for_victory(data: Game_Data) -> None:
    min_players: int = 2

    for role in data.alive_players.values():
        if role.alternative_end_count > min_players:
            min_players = role.alternative_end_count  

    # -- Checks For Win Conditions -- #
    if len(data.evil_aligned) == 0 or (len(data.alive_players) <= min_players and min_players > 2):
        data.playing = False
        data.good_win = True
    elif (len(data.alive_players) == 2) or len(data.evil_aligned) > len(data.good_aligned):
        data.playing = False
        data.evil_win = True
            

@enforce_types
def revert_to_mafia(data: Game_Data) -> None:
    mafia_count = 0
    for role in data.alive_players.values():
        if role.ability == data.mafia_role.ability and not role.alignment:
            mafia_count += 1

    if mafia_count == 0:
        next_evil_player = data.next_evil_player
        if next_evil_player != None:
            ability_swap(data, next_evil_player)

    elif mafia_count > 1:
        for name, role in data.evil_aligned.items():
            if role.ability == data.mafia_role.ability:
                ability_swap(data, name)

        data.evil_count = 0
        revert_to_mafia(data)

@enforce_types
def role_switch(data: Game_Data, player: str, new_role: Role) -> None:
    players = data.players
    role = players[player]
    information = role.information
    players[player] = deepcopy(new_role)
    players[player].ability = deepcopy(new_role.ability)
    data.priority[player] = players[player]
    players[player].linked = role.linked
    players[player].linked_to = role.linked_to
    players[player].linker = role.linker
    players[player].information = information

@enforce_types
def ability_swap(data: Game_Data, player: str) -> None:
    players = data.players
    role = players[player]
    role.ability, role.secondary_ability = role.secondary_ability, role.ability
    
@enforce_types
def use_vote_abiltities(data: Game_Data) -> None:
    for user, role in data.players.items():
        try:
            if "on_vote" in role.ability_type:
                role.ability(user, data)
        except: 
            pass

        if role.secondary_ability != None:
            if "on_vote" in role.secondary_ability.ability_type:
                    try:
                        role.ability(user, data)
                    except IndexError: # -- Dealing With Gambler Drawing Neutrals And Not Being Able To Pick Targets
                        pass

@enforce_types
def use_death_abilities(data: Game_Data) -> None:
    for role in data.players.values():
        role.on_death_ability(data)

@enforce_types
def init_evil_alternative(data: Game_Data) -> None:
    for role in data.evil_aligned.values():
        if role.secondary_ability == data.none_role.ability:
            role.secondary_ability = deepcopy(data.mafia_role.ability)