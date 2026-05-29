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
    can_use = role.ability.number_of_uses != 0
    normal_activation = not ("no_action_round" in role.ability_type)
    first_night_special: bool = not ("first_night" in role.ability.ability_type and data.turn_count == 1)

    if has_recursed:
        recurse_case = "activate_again" in role.ability_type
    else:
        recurse_case = True

    return life and can_use and recurse_case and normal_activation and not_cancel and first_night_special

@enforce_types
def use_abilities(data: Game_Data, can_recurse: bool = True) -> None:
    priority: Players = data.priority

    for role in priority.values():
        if role.remaining_life_counter is not None:
            role.remaining_life_counter -= 1

    for name, role in priority.items():
        if ability_conditions(role, not can_recurse, data):
            role.ability(name, data)

        elif "first_night" in role.ability.ability_type and data.turn_count == 1:
            role.ability(name, data, first_night = True)

    for role in priority.values():
        if role.remaining_life_counter is not None:
            if role.remaining_life_counter <= 0:
                protected: bool = role.statuses.protected
                role.statuses.protected = False
                role.die(data.players)
                role.statuses.protected = protected
                role.remaining_life_counter = None

@enforce_types
def life_death_sort(data: Game_Data) -> None:
    data.update_life()

@enforce_types
def remove_round_data(data: Game_Data, used_Death_ability: bool = False, post_vote: bool = False) -> None:
    for name, role in data.players.items():
        if ("keep_targets" not in role.ability.ability_type) and (used_Death_ability or not ("on_death" in role.ability_type or "on_vote" in role.ability_type)): 
            targets = role.targets
            
            for i in range(len(targets)):
                targets.pop(0)

        role.recursion_fuck_up = False
        role.information = []
        role.visited_by = []

        # -- Silence Check -- #
        if post_vote: 
            if role.statuses.silenced:
                survived: bool = None
                while survived is None:
                    survived = messagebox.askyesnocancel("Ability", f"Did {name} Stay Silent?", default = "cancel", icon = "question")

                if not survived:
                    role.remaining_life_counter = 1

        # -- Status Conditions -- #
        if post_vote: 
            role.statuses.silenced = False
        else:
            role.statuses.protected = False
            role.statuses.poisoned = False

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
def show_victory(victory_data: list[str], turn_count: int) -> None:
    victory_str = "Winners:\n"
    for item in victory_data:
        victory_str += item + ", "

    if len(victory_data) > 0:
        victory_str = victory_str[:-2]
    else:
        victory_str += "None"

    messagebox.showinfo(f"Game Over On Turn {turn_count}", victory_str, icon = "info")

@enforce_types
def check_for_victory(data: Game_Data) -> None:
    if not (data.good_win or data.evil_win):
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
    else:
        data.playing = False

@enforce_types
def revert_to_mafia(data: Game_Data) -> None:
    mafia_count = 0
    for role in data.players.values():
        if role.ability == data.mafia_role.ability and not role.alignment and role.currently_alive:
            mafia_count += 1

    if mafia_count == 0:
        next_evil_player = data.next_evil_player
        if next_evil_player != None:
            ability_swap(data, next_evil_player)
    
    elif mafia_count > 1:
        for name, role in data.players.items():
            if role.currently_alive and not role.alignment:
                if role.ability == data.mafia_role.ability and role.name != "Mafia":
                    ability_swap(data, name)

        data.evil_count = 0

@enforce_types
def role_switch(data: Game_Data, player: str, new_role: Role) -> None:
    players = data.players
    role = players[player]
    information = role.information
    players[player] = deepcopy(new_role)
    players[player].ability = deepcopy(new_role.ability)
    data.priority[player] = players[player]
    players[player].statuses.linked = role.linked
    players[player].linked_to = role.linked_to
    players[player].information = information

@enforce_types
def ability_swap(data: Game_Data, player: str) -> None:
    players = data.players
    role = players[player]
    role.ability, role.secondary_ability = role.secondary_ability, role.ability
    role.information.append(f"Your ability is now {data.get_role_by_ability(role.ability, player).name} ({role.ability.__name__})")
    
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
                role.secondary_ability(user, data)

@enforce_types
def use_death_abilities(data: Game_Data) -> None:
    for role in data.players.values():
        role.on_death_ability(data)

@enforce_types
def init_evil_alternative(data: Game_Data) -> None:
    for role in data.evil_aligned.values():
        if role.secondary_ability == data.none_role.ability:
            role.secondary_ability = deepcopy(data.mafia_role.ability)

@enforce_types
def game_over_abilities(data: Game_Data) -> None:
    for name, role in data.players.items():
        if "game_end" in role.ability.ability_type:
            role.ability.ability(name, data)
        if "game_end" in role.secondary_ability.ability_type:
            role.secondary_ability.ability(name, data)