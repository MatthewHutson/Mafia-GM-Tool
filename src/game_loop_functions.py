# -- Imports -- #
from utils import *
from classes_and_types import *
from menu.menu import *
from menu.menu_classes import *

# -- Functions -- #
@enforce_types
def use_abilities(data: Game_Data) -> None:
    for name, role in data.priority.items():
        if role.currently_alive and not ("on_vote" in role.ability_type or "on_death" in role.ability_type):
            role.ability(name, data)
            role.used_ability = True

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
    victory_str = "Winners: "
    for item in victory_data:
        victory_str += item + ", "

    if len(victory_data) > 0:
        victory_str = victory_str[:-2]
    else:
        victory_str += "None"

    messagebox.showinfo("Game Over", victory_str)

@enforce_types
def check_for_victory(data: Game_Data) -> None:
    # -- Checks For Win Conditions -- #
        if len(data.evil_aligned) == 0:
            data.playing = False
            data.good_win = True

        if (len(data.evil_aligned) == 1 and len(data.good_aligned) == 1) or len(data.evil_aligned) > len(data.good_aligned):
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
            role_switch(data.players, next_evil_player, data.mafia_role)

@enforce_types
def role_switch(players: Players, player: str, new_role: Role) -> None:
    role = players[player]
    players[player] = deepcopy(new_role)
    players[player].linked = role.linked
    players[player].linked_to = role.linked_to
    players[player].linker = role.linker

@enforce_types
def use_vote_abiltities(data: Game_Data) -> None:
    for user, role in data.players.items():
        if "on_vote" in role.ability_type:
            role.ability(user, data)

@enforce_types
def use_death_abilities(data: Game_Data) -> None:
    for role in data.players.values():
        role.on_death_ability(data)