# -- Imports -- #
import json
import os
from utils import *
from tkinter import messagebox
from time import sleep
from classes_and_types import *
from menu.menu import *
from game_loop_functions import *
import abilities as a

# -- Functions -- #
@enforce_types
def selection_coindition(data: Game_Data, role: Role, name: str) -> bool:
    singular = (not ("singular" in role.ability_type and (role.selected_target)))
    targets = role.ability.targets > 0 

    universal_conditions = singular and targets and data.playing
    use_ability = True
    dead_targets = True 

    if not role.ability.target_living and len(data.dead_players) == 0:
        dead_targets = False

    if "on_demand" in role.ability_type and universal_conditions and dead_targets:
        sleep(1)
        use_ability = messagebox.askyesno("Ability", f"Does {name}, the {role.name} want to use their ability ({role.ability.__name__})?")
        role.ability_cancel = not use_ability

    return universal_conditions and use_ability and dead_targets

# -- Main -- #
@enforce_types
def main() -> None:
    # -- Game Data -- #
    role_functions: dict[str, Callable] = {name : getattr(a, name) for name in dir(a) if callable(getattr(a, name))}
    roles: dict[str, Role] = {}

    # -- File Handling -- #
    path: str = "Roles"

    for item in os.listdir(path):
        with open(path + "/" + item, 'r') as file:
            data: dict = json.load(file)  
            data["ability"] = role_functions[data["ability"]]
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
    game_data = Game_Data(Players(entries.assign_roles()), deepcopy(roles["Mafia"]), deepcopy(roles["Villager"]))
    game_data.init(a.vote)

    # -- Game Loop -- #
    init_game_menu(entries, game_data)

    while game_data.playing:
        # -- Game Loop -- #
        for name, role in game_data.alive_players.items():
            result: bool = selection_coindition(game_data, role, name)
            if result:
                selection_menu(game_data, entries, name)
            elif game_data.playing:
                sleep(1)
                messagebox.showinfo("Wake Up", f"Wake Up {name} to use no ability.")

        if game_data.playing:
            use_abilities(game_data)
            information(game_data)
            life_death_sort(game_data)

            remove_round_data(game_data)

            pack_alive_and_dead(game_data, game_data.vote_role)
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
                    pack_alive_and_dead(game_data, game_data.vote_role)

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
        main()
        playing = messagebox.askyesno("Restart", "Do you want to play another round?")