# -- Imports -- #
from utils import *
from classes_and_types import *
from menu.menu import *
from menu.menu_classes import *

# -- Functions -- #
@enforce_types
def ability_conditions(role: Role, has_recursed: bool, data: Game_Data) -> bool:
    life = role in data.alive_players.values()
    singular = not ("on_vote" in role.ability_type or "on_death" in role.ability_type)

    if has_recursed:
        recurse_case = "activate_again" in role.ability_type
    else:
        recurse_case = True

    return life and singular and recurse_case

@enforce_types
def use_abilities(data: Game_Data, can_recurse: bool = True) -> None:
    for name, role in data.priority.items():
        if ability_conditions(role, can_recurse, data):
            if not role.ability_cancel or not (can_recurse or "secondary_ability" in role.ability_type) and not role.recursion_fuck_up:
                role.used_ability = True

            role.ability(name, data)

    if can_recurse:
        use_abilities(data, False)

@enforce_types
def life_death_sort(data: Game_Data) -> None:
    for name, role in data.players.items():
        if name in data.alive_players.keys():
            if not role.currently_alive:
                del data.alive_players[name]
                data.dead_players[name] = role
                if role.alignment:
                    del data.good_aligned[name]
                else:
                    del data.evil_aligned[name]
    
    revert_to_mafia(data)

@enforce_types
def remove_round_data(data: Game_Data) -> None:
    for role in data.players.values():
        if not "singular" in role.ability_type: 
            for i in range(len(role.targets)):
                del role.targets[0]

        role.recursion_fuck_up = False
        role.poisoned = False
        role.protected = False
        role.information = []
        role.visited_by = []

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
    mafia_alive = False
    for role in data.alive_players.values():
        mafia_alive = mafia_alive or role.name == "Mafia"

    if not mafia_alive:
        next_evil_player = data.next_evil_player
        if next_evil_player != None:
            role_switch(data, next_evil_player, data.mafia_role)

@enforce_types
def role_switch(data: Game_Data, player: str, new_role: Role) -> None:
    players = data.players
    role = players[player]
    information = role.information
    players[player] = deepcopy(new_role)
    data.priority[player] = players[player]
    players[player].linked = role.linked
    players[player].linked_to = role.linked_to
    players[player].linker = role.linker
    players[player].information = information

@enforce_types
def use_vote_abiltities(data: Game_Data) -> None:
    for user, role in data.players.items():
        if "on_vote" in role.ability_type:
            role.ability(user, data)

@enforce_types
def use_death_abilities(data: Game_Data) -> None:
    for role in data.players.values():
        role.on_death_ability(data)