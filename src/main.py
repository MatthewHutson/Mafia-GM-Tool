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

# -- Main -- #
@enforce_types
def main() -> None:
    # -- Game Data -- #
    role_functions: dict[str, a.Ability] = {ability.__name__: ability() for ability in Ability.__subclasses__()}
    roles: dict[str, Role] = {}
    ability_distribution: dict[str, float] = {}

    # -- File Handling -- #
    path: str = "Roles"

    for key, value in role_functions.items():
        ability_distribution[key] = float(value.p)

    for item in os.listdir(path):
        with open(path + "/" + item, 'r') as file:
            data: dict = json.load(file)

            ability_name = data["ability"]  
            data["ability"] = role_functions[ability_name]
            data["_alignment"] = data["alignment"]

            del data["alignment"]
            
            roles[data["name"]] = Role(**data, targets = [], information = [], visited_by = [])

    with open("defaults.txt") as file:
        string_data: str = file.readline()
        name_data: list[str] = string_data.split(", ")

    entries = Menu_Entry([], list(roles.values()))

    # -- Menu -- #
    setup_menu(entries, name_data)

    # -- Player Organisation -- #
    game_data = Game_Data(Players(entries.assign_roles()), roles, role_functions, ability_distribution, card_init(), entries)
    game_data.init()

    # -- Game Loop -- #
    init_game_menu(entries, game_data)

    while game_data.playing:
        # -- Game Loop -- #
        for name, role in game_data.alive_players.items():
            role.made_choice = False
            can_pick_primary_target: bool = selection_coindition(game_data, role, name, True)
            if can_pick_primary_target: selection_menu(game_data, entries, name)

            if "secondary_ability" in role.ability_type and not ("alternate" in role.ability_type and not role.ability_cancel):
                can_pick_secondary_target: bool = selection_coindition(game_data, role, name, False)
                if can_pick_secondary_target: selection_menu(game_data, entries, name, is_primary_ability = False)
            else:
                can_pick_secondary_target = False

            if game_data.playing and not (can_pick_primary_target or can_pick_secondary_target) and not role.made_choice:
                sleep(0.5)
                messagebox.showinfo("Wake Up", f"Wake Up {name} to use no ability.")

        if game_data.playing:
            use_abilities(game_data)
            information(game_data)
            life_death_sort(game_data)
            information(game_data, False)

            remove_round_data(game_data)

            pack_alive_and_dead(game_data, game_data.vote_role, 0)
            use_death_abilities(game_data)
            life_death_sort(game_data)
            remove_round_data(game_data)

            check_for_victory(game_data)

            if game_data.playing:
                voted_out: str = voting_menu(game_data, entries)

                if game_data.playing and voted_out != "none":
                    game_data.players[voted_out].voted_out(game_data.players)
            
                life_death_sort(game_data)
                use_vote_abiltities(game_data)
                use_death_abilities(game_data)
                life_death_sort(game_data)

                if game_data.playing:
                    pack_alive_and_dead(game_data, game_data.vote_role, 0)

        check_for_victory(game_data)

    for name, role in game_data.players.items():
        if "game_end" in role.ability_type:
            role.ability(name, game_data)

    winners = []

    for name, role in game_data.players.items():
        if role.solo_win:
            if not role.team_win_condition:
                if role.channeled_role == None:
                    winners.append(f"\n{name} as the {role.name}")
                else:
                    winners.append(f"\n{name} as the {role.name} chanelling the {role.channeled_role}")
            else:
                # -- For Mayor -- #
                if role.currently_alive:
                    if role.alignment:
                        game_data.good_win = True
                        game_data.evil_win = False
                    else:
                        game_data.good_win = False
                        game_data.evil_win = True

    if game_data.good_win: winners.append("\nThe Good Team!")
    if game_data.evil_win: winners.append("\nThe Evil Team!")

    show_victory(winners)
    
# -- On Run -- #
if __name__ == "__main__":
    playing: bool = True
    while playing == True:
        try:
            main()
            playing = messagebox.askyesno("Game Over", "Do you want to play another round?")
        except Exception as e:
            playing = False