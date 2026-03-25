# -- Imports -- #
import json
import os
from utils import *
from tkinter import messagebox
from time import sleep
from classes_and_types import *
from menu.menu import *
from menu.card_index import card_init
from game_loop_functions import *
import abilities as a

# -- Functions -- #
@enforce_types
def on_demand(data: Game_Data, role: Role, ability: Ability, is_primary_ability: bool, name: str) -> None:
    if "on_demand" in ability.ability_type and (not ("singular" in ability.ability_type and (role.selected_target))):
        sleep(0.5)
        use_ability = messagebox.askyesno("Ability", f"Does {name}, the {role.name} want to use their ability ({ability.__name__})?")
        
        if is_primary_ability:
            role.ability_cancel = not use_ability
        else:
            role.secondary_ability_cancel = not use_ability

        role.made_choice = True

@enforce_types
def alternate(data: Game_Data, role: Role, ability: Ability, name: str) -> None:
    if "alternate" in ability.ability_type and (not ("singular" in ability.ability_type and (role.selected_target))):
        sleep(0.5)
        use_ability = messagebox.askyesno("Ability", f"Does {name}, the {role.name} want to usre their primary ability ({ability.__name__}) instead of their secondary ability ({role.secondary_ability.__name__})?")
        role.ability_cancel = not use_ability
        role.secondary_ability_cancel = use_ability
        role.made_choice = True

@enforce_types
def selection_coindition(data: Game_Data, role: Role, name: str, is_primary_ability: bool) -> bool:
    if is_primary_ability:
        ability = role.ability
    else:
        ability = role.secondary_ability

    ability_type = ability.ability_type
    singular = (not ("singular" in ability_type and (role.selected_target)))
    targets = ability.targets > 0 

    dead_targets = (ability.target_living or len(data.dead_players) > 0)

    if singular and data.playing and dead_targets:
        alternate(data, role, ability, name)
        on_demand(data, role, ability, is_primary_ability, name)
    
    if is_primary_ability:
        use_ability = not role.ability_cancel
        role.ability_cancel = not (singular and data.playing and use_ability and dead_targets)
    else:
        use_ability = not role.secondary_ability_cancel
        role.secondary_ability_cancel = not (singular and data.playing and use_ability and dead_targets)

    return singular and data.playing and use_ability and dead_targets and targets

@enforce_types
def nap_time(data: Game_Data) -> None:
    # -- A Menu To Inform Evil Players Of Their Allies And Bluffs -- #
    all_roles: set[str] = set(data.roles.keys()) - set(["Villager"])
    playing_roles: set[str] = set(role.name for role in data.players.values())
    evil_roles: set[str] = set(name for name, role in data.roles.items() if not role.alignment)
    bluff_roles: list[str] = list(all_roles - playing_roles - evil_roles)
    shuffle(bluff_roles)
    bluff_roles = bluff_roles[:len(data.evil_aligned)]
    evil_cards: list[str] = [data.get_card_by_role(role) for role in list(data.evil_aligned.values()) if role.name != "Mafia"]
    bluff_cards: list[str] = [data.get_card_by_role(data.roles[role]) for role in bluff_roles]

    sleep(0.5)
    info: str = f"Wake up The Evil Team: {list(data.evil_aligned.keys())}. Show Them \n\n #1: Their Teammate(s): {evil_cards}. \n #2: Their Bluff Roles: {bluff_cards}. \n\nPress NO When Everyone Is Ready To Procede."
    while messagebox.askyesno("Sleepy Time", info): sleep(0.5)

@enforce_types
def game(data: Game_Data, entries: Menu_Entry) -> None:
    # -- Game Setup -- #
    init_game_menu(entries, data)
    nap_time(data)

     # -- Game Loop -- #
    while data.playing:
        # -- Game Loop -- #
        for name, role in data.alive_players.items():
            role.made_choice = False
            can_pick_primary_target: bool = selection_coindition(data, role, name, True)
            if can_pick_primary_target: selection_menu(data, entries, name)

            if "secondary_ability" in role.ability_type and not ("alternate" in role.ability_type and not role.ability_cancel):
                can_pick_secondary_target: bool = selection_coindition(data, role, name, False)
                if can_pick_secondary_target: selection_menu(data, entries, name, is_primary_ability = False)
            else:
                can_pick_secondary_target = False

            if data.playing and not (can_pick_primary_target or can_pick_secondary_target) and not role.made_choice:
                sleep(0.5)
                messagebox.showinfo("Wake Up", f"Wake Up {name} to use no ability.")

        if data.playing:
            use_abilities(data)
            information(data)
            life_death_sort(data)
            information(data, False)

            update_all_targets(data)
            remove_round_data(data)

            pack_alive_and_dead(data, data.vote_role, 0)
            use_death_abilities(data)
            life_death_sort(data)
            remove_round_data(data)

            check_for_victory(data)

            if data.playing:
                voted_out: str = voting_menu(data, entries)

                if data.playing and voted_out != "none":
                    data.players[voted_out].voted_out(data.players)
            
                life_death_sort(data)
                use_vote_abiltities(data)
                use_death_abilities(data)
                life_death_sort(data)

                if data.playing:
                    pack_alive_and_dead(data, data.vote_role, 0)

        check_for_victory(data)