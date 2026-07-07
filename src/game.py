# -- Imports -- #
import json
import os
from utils import *
from tkinter import messagebox, simpledialog
from time import sleep
import threading
from classes_and_types import *
from menu.menu import *
#from menu.card_index import card_init
from game_loop_functions import *
import abilities as a

# -- Functions -- #
@enforce_types
def on_demand(role: Role, ability: Ability, is_primary_ability: bool, name: str) -> None:
    if "on_demand" in ability.ability_type and ability.number_of_uses != 0:
        sleep(0.5)
        
        use_ability = None
        while use_ability is None:
            use_ability = messagebox.askyesnocancel("Ability", f"Does {name}, the {role.name} want to use their ability ({ability.__name__})?\n\n   Yes: Use Ability\n   No: Do Nothing", default = "cancel", icon = "question")
            sleep(0.5)

        if is_primary_ability:
            role.ability_cancel = not use_ability
        else:
            role.secondary_ability_cancel = not use_ability

        role.made_choice = True

@enforce_types
def alternate(role: Role, ability: Ability, name: str) -> None:
    if "alternate" in ability.ability_type and ability.number_of_uses != 0:
        sleep(0.5)

        use_ability = None
        while use_ability is None:
            use_ability = messagebox.askyesnocancel("Ability", f"Does {name}, the {role.name} want to usre their primary ability instead of their secondary ability?\n\n   Yes: {ability.__name__}\n   No: {role.secondary_ability.__name__}", icon = "question", default = "cancel")
            sleep(0.5)

        role.ability_cancel = not use_ability
        role.secondary_ability_cancel = use_ability
        role.made_choice = True

@enforce_types
def ability_selection_input(role: Role, ability: Ability) -> None:
    if "selection" in ability.ability_type:
        ability.selection_index = simpledialog.askinteger(F"Index for {role.name}", f"Input A Value Between {0} and {ability.max_selection_index}.", minvalue = 0, maxvalue = ability.max_selection_index)

@enforce_types
def selection_coindition(data: Game_Data, role: Role, name: str, is_primary_ability: bool) -> bool:
    if is_primary_ability:
        ability: Ability = role.ability
    else:
        ability: Ability = role.secondary_ability

    can_use = ability.number_of_uses != 0
    targets = ability.targets > 0 

    dead_targets = (ability.target_living or len(data.dead_players) > 0)

    if can_use and data.playing and dead_targets:
        alternate(role, ability, name)
        on_demand(role, ability, is_primary_ability, name)
    
    if is_primary_ability:
        use_ability = not role.ability_cancel
        role.ability_cancel = not (can_use and data.playing and use_ability and dead_targets)
    else:
        use_ability = not role.secondary_ability_cancel
        role.secondary_ability_cancel = not (can_use and data.playing and use_ability and dead_targets)

    return can_use and data.playing and use_ability and dead_targets and targets

@enforce_types
def nap_time(data: Game_Data) -> None:
    # -- A Menu To Inform Evil Players Of Their Allies And Bluffs -- #
    all_roles: set[str] = set(data.roles.keys()) - set(["Villager", "Testing"])
    playing_roles: set[str] = set(role.name for role in data.players.values())
    evil_roles: set[str] = set(name for name, role in data.roles.items() if not role.alignment)
    bluff_roles: list[str] = list(all_roles - playing_roles - evil_roles)
    shuffle(bluff_roles)

    try:
        bluff_roles = bluff_roles[:len(data.evil_aligned)]
    except:
        bluff_roles = bluff_roles
    evil_cards: list[str] = [role.name for role in list(data.evil_aligned.values()) if role.name != "Mafia"]
    bluff_cards: list[str] = [role for role in bluff_roles]

    info: str = f"Wake up The Evil Team: {list(data.evil_aligned.keys())}. Show Them \n\n #1: Their Teammate(s): {evil_cards}. \n #2: Their Bluff Roles: {bluff_cards}. \n\nIs Everyone Ready To Procede?"
    timer = threading.Timer(0.1, lambda: nap_time_info(info))
    timer.start()

@enforce_types
def nap_time_info(info: str) -> None:
    try:
        if not messagebox.askyesno("Sleepy Time", info, default = "no", icon = "info"):
            timer = threading.Timer(3.0, lambda: nap_time_info(info))
            timer.start()
    except:
        pass

@enforce_types
def start_abilities(data: Game_Data) -> None:
    for user, role in data.players.items():
        if "game_start" in role.ability.ability_type:
            try:
                role.ability.ability(user, data, early_start = True)
            except:
                role.ability.ability(user, data)

        if "game_start" in role.secondary_ability.ability_type:
            try:
                role.secondary_ability.ability(user, data, early_start = True)
            except:
                role.secondary_ability.ability(user, data)

@enforce_types
def game(data: Game_Data, entries: Menu_Entry, normal_start: bool = True) -> None:
    # -- Game Setup -- #
    if normal_start: start_abilities(data)
    init_game_menu(entries, data)
    nap_time(data)
    init_evil_alternative(data)

     # -- Game Loop -- #
    while data.playing:
        # -- Game Loop -- #
        data.turn_count += 1

        for name, role in data.alive_players.items():
            # -- Equation Type Handler -- #
            try:
                if is_instance(role.ability.number_of_uses, equation):
                    role.ability.number_of_uses = role.ability.number_of_uses.get_value(data.total_evil_count)
            except: pass
            
            try:
                if is_instance(role.secondary_ability.number_of_uses, equation):
                    role.secondary_ability.number_of_uses = role.secondary_ability.number_of_uses.get_value(data.total_evil_count)
            except: pass

            if data.playing:
                action_frame, action_label, ability = selection_menu_create(data, entries, name, functional = False)

            role.made_choice = False
            can_pick_primary_target: bool = selection_coindition(data, role, name, True)

            if data.playing:
                ability_selection_input(role, role.ability)
                ability_selection_input(role, role.secondary_ability)  
                selection_menu_destroy(data, entries, name, action_frame, action_label, ability, functional = False)
        
            if can_pick_primary_target:
                selection_menu(data, entries, name)

            if "secondary_ability" in role.ability_type and not ("alternate" in role.ability_type and not role.ability_cancel):
                can_pick_secondary_target: bool = selection_coindition(data, role, name, False)
                if can_pick_secondary_target: selection_menu(data, entries, name, is_primary_ability = False)
            else:
                can_pick_secondary_target = False

            if data.playing and not (can_pick_primary_target or can_pick_secondary_target) and not role.made_choice:
                sleep(0.5)
                messagebox.showinfo("Wake Up", f"Wake Up {name} to use no ability.", icon = "info")

        if data.playing:
            use_abilities(data)

             # -- Ensures Mafia Evil Roles Will Have Kill Switch -- #
            revert_to_mafia(data)

            # -- Player And GM Info -- #
            information(data)
            life_death_sort(data)
            information(data, tell_nothing = False, first_wave = False)

            # -- Resetting The Player Data -- #
            update_all_targets(data)
            remove_round_data(data, keep_announcements = True)

            pack_alive_and_dead(data, data.vote_role, 0)
            use_death_abilities(data)
            life_death_sort(data, update_data = False)
            remove_round_data(data, used_Death_ability = True, keep_announcements = True)

            check_for_victory(data)

            if data.playing:
                voted_out: str = voting_menu(data, entries)

                if data.playing and voted_out != "none":
                    data.players[voted_out].voted_out(data.players)
            
                life_death_sort(data)
                use_vote_abiltities(data)
                use_death_abilities(data)
                life_death_sort(data)
                remove_round_data(data, post_vote = True)

                if data.playing:
                    pack_alive_and_dead(data, data.vote_role, 0)

        game_over_abilities(data)
        check_for_victory(data)