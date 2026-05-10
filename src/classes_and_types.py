# -- Imports -- #
from __future__ import annotations
from dataclasses import dataclass
from utils import *
from random import shuffle, choice
from copy import deepcopy
import numpy as np
import csv
import json

# -- Ability Template Class -- #
@dataclass
class Status_Manager():
    # -- Statuses -- #
    poisoned: bool = False
    drunk: bool = False
    linked: bool = False
    unemployed: bool = False # Only Used For Neutrals #

    # -- Properties -- #
    @property
    @enforce_types
    def status_dict(self) -> dict:
        return {capitalise_words(name): value for name, value in self.__dict__.items()}
    
    # -- Methods -- #
    @enforce_types
    def ability_conditions(self) -> list[bool]:
        return [self.poisoned, self.drunk]
    
    @enforce_types
    def get_data(self, user: str, inverse = False) -> list[str]:
        output: list[str] = []

        for status, value in self.__dict__.items():
            if value ^ inverse:
                output.append(f"{user} is {status}.")
            else:
                output.append(f"{user} is NOT {status}.")

        return output

    @enforce_types
    def bullshit_data(self, user: str) -> list[str]:
        output: list[str] = []
        for status in self.__dict__.items():
            extra: str = choice([" NOT", " NOT", " NOT", ""])
            output.append(f"{user} is{extra} {status}.")

        return output

class Ability():
    @enforce_types
    def __init__(self, targets: int, p: Union[int, float], ability_type: list[str], target_living: bool = True, priority: int = 255, can_pick_same_target: bool = False) -> None:
        # -- Attributes -- #
        self.targets: int = targets
        self.p: int | float = p
        self.ability_type: list[str] = ability_type
        self.target_living: bool = target_living
        self.priority: float = priority
        self.used_ability: bool = False
        self.can_pick_same_target: bool = can_pick_same_target
    
    @property
    @enforce_types
    def __name__(self) -> str:
        return capitalise_words(type(self).__name__, "_")
    
    @property
    @enforce_types
    def true_name(self) -> str:
        return type(self).__name__

    # -- Methods -- #
    def ability(self, user: str, data: Game_Data) -> None:
        ...

    def if_poisoned(self, user: str, data: Game_Data) -> None:
        ...

    def if_drunk(self, user: str, data: Game_Data) -> None:
        ...

    def __call__(self, user: str, data: Game_Data, **kwargs) -> None:
        match data.players[user].statuses.ability_conditions():
            case [True, False]: self.if_poisoned(user, data, **kwargs)
            case [False, True]: self.if_poisoned(user, data, **kwargs)
            case _: self.ability(user, data, **kwargs)

    @enforce_types
    def __eq__(self, ability2: Union[Ability, type, None]) -> bool:
        if type(ability2) == type:
            return type(self) == ability2
        elif ability2 is None:
            return str(self).lower() == "none" # -- Catches Null Value and None Ability -- #
        else:
            return type(ability2) == type(self)
        
    @enforce_types
    def to_dict(self) -> dict:
        dict: dict = self.__dict__

        for key, item in dict.items():
            if type(item) == set:
                dict[key] = list(item)

        return dict
    
    @enforce_types
    def set_attribuite(self, name: str, value: Any) -> None:
        if type(self.__getattribute__(name)) == set and type(value) == list:
            value = set(value)

        self.__setattr__(name, value)


# -- Role Class -- #
@dataclass
class Role:
    # -- Attributes - #
    name: str
    ability: Ability
    _alignment: bool # True Being Good, False Being Evil #
    mafia_alternative: bool # Switches to Mafia Abiltity When All Normal Mafia Dies #
    max_count: int
    current_targets: list[str]
    information: list[str]
    visited_by: list[str]
    statuses: Status_Manager
    secondary_ability: Ability = None
    new_mafia = False # For Mafia Alternative Handling
    currently_alive: bool = True
    protected: bool = False
    linker: str = None
    linked_to: str = None
    selected_target = False
    solo_win: bool = False
    was_voted_out: bool = False
    just_died: bool = False
    ability_cancel: bool = False # For "on_demand"
    secondary_ability_cancel: bool = True
    recursion_fuck_up: bool = False
    channeled_role: str = None
    team_win_condition: bool = False
    alternative_end_count: int = 0
    made_choice: bool = False
    previous_targets: list = None
    
    # -- Properties -- #
    @property
    @enforce_types
    def alignment(self) -> bool:
        if self._alignment == None: return True
        else: return self._alignment

    @property
    @enforce_types
    def true_alignment(self) -> Union[bool, None]:
        return self._alignment
    
    @property
    @enforce_types
    def ability_type(self) -> list[str]: # Can contain "singular", "passive", "repeat", "on death", "on vote", "on_demand", "recurse_targets", "activate_again", "game_end" #
        return self.ability.ability_type
    
    @property
    @enforce_types
    def named_alignment(self) -> str:
        match(self._alignment):
            case None: return "Neutral"
            case True: return "Good"
            case False: return "Evil"

    @property
    @enforce_types
    def can_pick_secondary_targets(self) -> bool:
        # -- Checks If The First Ability Was Cancelled and If Secondary Ability Needs Targets -- #
        return (not self.ability_cancel or self.secondary_ability_cancel) and self.secondary_ability.targets > 0 
    
    @property
    @enforce_types
    def priority(self) -> float: # Order of Execution of Abilities From Lowest To Highest #
        return self.ability.priority
    
    @property
    @enforce_types
    def used_ability(self) -> bool:
        return self.ability.used_ability
    
    @used_ability.setter
    @enforce_types
    def used_ability(self, value: bool) -> None:
        self.ability.used_ability = value

    @property
    @enforce_types
    def used_secondary_ability(self) -> bool:
        if self.secondary_ability is not None:
            return self.secondary_ability.used_ability
        else:
            return False
    
    @used_secondary_ability.setter
    @enforce_types
    def used_secondary_ability(self, value: bool) -> None:
        if self.secondary_ability is not None:
            self.secondary_ability.used_ability = value

    @property
    @enforce_types
    def targets(self) -> list[str]:
        return self.current_targets
    
    @targets.setter
    @enforce_types
    def targets(self, value: list[str]) -> None:
        self.current_targets = value

    # -- Methods -- #
    @enforce_types
    def die(self, players: Players, recurse: bool = True) -> bool:
        if not self.protected: 
            self.currently_alive = False
            self.just_died = True

            if self.statuses.linked and recurse and (not players[self.linker].poisoned): # Recursion Base Case and Cupid Poison Check #
                players[self.linked_to].protected = False
                players[self.linked_to].die(players, recurse = False)

            return True
                
        return False
        
    @enforce_types
    def revive(self) -> None:
        self.currently_alive = True
        self.just_died = False

    @enforce_types
    def __str__(self) -> str:
        if self.secondary_ability is None:
            return f"Role: {self.name}, Alignment: {self.named_alignment}, Primary Ability: {self.ability.__name__}, Secondary Ability: None, Alive: {self.currently_alive}"
        else:
            return f"Role: {self.name}, Alignment: {self.named_alignment}, Primary Ability: {self.ability.__name__}, Secondary Ability: {self.secondary_ability.__name__}, Alive: {self.currently_alive}"
    
    @enforce_types
    def __getattribute__(self, name: str) -> Any:
        # -- Allows The Extention Of All Statuses Into Objects Dictionaries -- #
        if name != "statuses" and name != "__dict__":
            # -- Nesting To Avoid Recursion Errors -- #
            if "statuses" in self.__dict__.keys():
                if name in self.statuses.__dict__.keys():
                    return self.statuses.__getattribute__(name)
            
        return super().__getattribute__(name)
    
    @enforce_types
    def __setattr__(self, name: str, value: Any) -> None:
        # -- Allows The Extention Of All Statuses Into Objects Dictionaries -- #
        if name != "statuses" and name != "__dict__":
            # -- Nesting To Avoid Recursion Errors -- #
            if "statuses" in self.__dict__.keys():
                if name in self.statuses.__dict__.keys():
                     self.statuses.__setattr__(name, value)
            
        super().__setattr__(name, value)

    @enforce_types
    def on_death_ability(self, data: Game_Data) -> None:
        if "on_death" in self.ability_type and not "on_vote" in self.ability_type and self.just_died:
            user = list(data.players.keys())[list(data.players.values()).index(self)]
            self.ability(user, data)
            
        if "on_death" in self.secondary_ability.ability_type and not "on_vote" in self.secondary_ability.ability_type and self.just_died:
            user = list(data.players.keys())[list(data.players.values()).index(self)]
            self.secondary_ability(user, data)

        self.just_died = False

    @enforce_types
    def voted_out(self, players: Players, recurse: bool = True) -> None:
        self.was_voted_out = True
        self.die(players, False)
        if self.statuses.linked and recurse:
            players[self.linked_to].voted_out(players, False)
    
    @enforce_types
    def __eq__(self, value) -> bool:
        return self.name == str(value)
    
    @enforce_types
    def update_targets(self) -> None:
        self.previous_targets = deepcopy(self.targets)

    def new(*args, **kwargs) -> Role:
        return Role(*args, **kwargs, current_targets = [], information = [], visited_by = [], statuses = Status_Manager())
    
# -- Type Definitions -- #
class Players(dict[str, Role]):
    @enforce_types
    def __setitem__(self, key: str, value: Role) -> None:
        key = capitalise_words(key)
        return super().__setitem__(key, value)
    
    @enforce_types
    def __eq__(self, value: dict[str, Role]) -> bool:
        if len(self) != len(value):
            return False
        else:
            try:
                for key, item in self.items():
                    if value[key] != item:
                        return False
            except: 
                return False
        return True
    
    @enforce_types
    def deepcopy(self) -> Players:
        # -- To Avoid copy.deepcopy Issues -- #
        new_data: dict[str, Role] = {}

        for key, value in self.items():
            new_data[key] = value

        return Players(new_data)
    
# -- Data Handling Classes -- #
@dataclass
class Menu_Entry:
    players: list[str]
    roles: list[Role]
    all_roles: list[str]
    current_roles_lists: list[list[str]]
    all_roles_lists: list[list[str]]
    settings: dict[Any]

    # -- Properties -- #
    @property
    def role_dict(self) -> Players:
        return Players({role.name: role for role in self.roles})
    
    @property
    @enforce_types
    def non_active_roles(self) -> list[list[str]]:
        inactive_roles_lists: list[list[str]] = []
        inactive_roles: list[str] = []

        for role in self.all_roles:
            in_game = False

            for role_list in self.current_roles_lists:
                in_game = in_game or (role in role_list)
                if in_game: break
            
            if not in_game:
                inactive_roles.append(role)

        for role_list in self.all_roles_lists:
            for role in inactive_roles:
                if role in role_list:
                    inactive_roles_lists.append(role_list)
                    break

        return inactive_roles_lists
    
    @property
    def non_active_non_evil_roles(self) -> list[list[str]]:
        role_list = self.non_active_roles
        new_roles = []

        for roles in role_list:
            if self.role_dict[roles[0]].alignment:
                new_roles.append(roles)

        return new_roles

    # -- Methods -- #
    @enforce_types
    def assign_roles(self) -> Players:
        shuffle(self.players)
        shuffle(self.roles)

        # -- Fixing Sleepy Time Bug With Bogosort -- #
        while self.roles[0].ability.targets == 0 or "on_demand" in self.roles[0].ability.ability_type or "alternate" in self.roles[0].ability.ability_type:
            shuffle(self.roles)

        return Players({self.players[i]: self.roles[i] for i in range(len(self.players))})
    
    @enforce_types
    def filter_roles(self, roles: list[str]) -> None:
        self.roles = [deepcopy(self.role_dict[role]) for role in roles]

    @enforce_types
    def shuffle_roles(self) -> None:
        shuffle(self.roles)
    
@dataclass
class Game_Data():
    # -- Attributes -- #
    players: Players
    roles: dict[str, Role]
    abilities: dict[str, Callable]
    ablity_distribution: dict[str, float]
    card_dict: dict[str, str]
    menu_entries: Menu_Entry
    settings: dict[str, Any] = None
    mafia_role: Role = None
    none_role: Role = None
    good_aligned: Players = None
    evil_aligned: Players = None
    alive_players: Players = None
    dead_players = None
    playing: bool = True
    good_win: bool = False
    evil_win: bool = False
    evil_count: int = 0

    # -- Properties -- #
    @property
    @enforce_types
    def next_evil_player(self) -> Union[str, None]:
        if self.evil_count >= len(self.evil_aligned):
            return None
        else:
            player = list(self.evil_aligned)[self.evil_count]
            self.evil_count += 1
            return player 
    
    @property
    @enforce_types
    def priority(self) -> Players:
        return Players(dict(sorted(self.players.items(), key = lambda item: item[1].priority)))
    
    @property
    @enforce_types
    def true_ability_names(self) -> dict[str, Ability]:
        out_data: dict = {}
        for ability in self.abilities.values():
            out_data[ability.__name__] = ability

        return out_data

    # -- Methods -- #
    @enforce_types
    def init(self, alter_drunk: bool = True) -> None:
        # -- Player Info -- #
        self.mafia_role = deepcopy(self.roles["Mafia"]) 
        self.none_role = deepcopy(self.roles["Villager"])

        self.good_aligned = Players({name: role for name, role in self.players.items() if role.alignment and role.currently_alive})
        self.evil_aligned = Players({name: role for name, role in self.players.items() if not role.alignment and role.currently_alive})

        self.alive_players = Players({name: role for name, role in self.players.items() if role.currently_alive})
        self.dead_players = Players({name: role for name, role in self.players.items() if not role.currently_alive})

        self.settings = {name: data["value"] for name, data in self.menu_entries.settings.items()}

        # -- Using A Role For Menu Purposes -- #
        self.vote_role: Role = Role.new("Voting", self.abilities["vote"], True, False, 999)
        
        # -- Secondary Ability Handling -- #
        for role in self.players.values():
            if role.secondary_ability is None:
                role.secondary_ability = deepcopy(self.abilities["none"])

        # -- statuses.drunk Consideration -- #
        if alter_drunk:
            self.set_drunk()

    @enforce_types
    def set_drunk(self) -> None:
        if self.settings["Drunk"] == 1:
            valid_players: list = [name for name, role in self.players.items() if role.true_alignment == True]
            player = choice(valid_players)
            self.players[player].drunk = True

    @enforce_types
    def get_role_by_ability(self, ability: Ability) -> Union[Role, None]:
        for role in self.roles.values():
            if role.ability == ability:
                return role
        return None
    
    @enforce_types
    def get_card_by_role(self, role: Role) -> str:
        return self.card_dict[role.name]
    
    @enforce_types
    def random_ability(self, used_abilities: set[str] = set([])) -> list[str, Ability]:
        temp_dist: dict = {ability: probability for ability, probability in self.ablity_distribution.items() if not ability in used_abilities}
        total = sum(temp_dist.values())
        temp_dist = {key: value / total for key, value in temp_dist.items()}
        sample: list[np.str_] = np.random.choice(np.array(list(temp_dist.keys())), size = 1, p = np.array(list(temp_dist.values())))
        return [str(sample[0]), self.abilities[sample[0]]]
    
    @enforce_types
    def backup_to_csv(self) -> None:
        # -- Saves Game State To The Backup csv When Crash Occurs -- #
        file_name: str = "backup.csv"
        data: list[list[str]] = [["Name", "Role", "Alignment", "Has Selected Target", "Used Primary", "Used Secondary", "Alive", "Solo Win", "Drunk", "Lover", "Targets"]]
        data: list[list[str]] = data + [[name, role.name, role._alignment, role.selected_target, role.ability.used_ability, role.secondary_ability.used_ability, role.currently_alive, role.solo_win, role.statuses.drunk, role.statuses.linked, str(role.targets)] for name, role in self.players.items()]

        with open(file_name, "w") as file:
            writer = csv.writer(file, delimiter = ",", lineterminator = "\n")
            writer.writerows(data)

    @enforce_types
    def load_from_backup(self) -> None:
        # -- Loads Game State To The Backup csv From The State When Crash Occurs -- #
        file_name: str = "backup.csv"
        data: list[list[str]] = []
        lovers: list[str] = []
        final_data: dict[str, Role] = {}

        with open(file_name, "r") as file:
            reader = csv.reader(file, delimiter = ",")
            is_data: bool = False
            data: list[list[str]] = []

            for row in reader:
                if is_data: data.append(row)
                else: is_data = True

        for row in data:
            # -- Data Management -- #
            if row[2] == "":
                row[2] = None
            else:
                row[2] = eval(row[2])

            row[3] = eval(row[3])
            row[4] = eval(row[4])
            row[5] = eval(row[5])
            row[6] = eval(row[6])
            row[7] = eval(row[7])
            row[8] = eval(row[8])
            row[9] = eval(row[9])

            if len(row[-1]) > 2:
                row[-1] = row[-1][1:-1].split(", ")

                for item in row[-1]:
                    item = item[1: -1]
            else:
                row[-1] = []

            # -- Loading Data -- #
            role: Role = self.roles[row[1]]
            role._alignment = row[2]
            role.selected_target = row[3]
            role.used_ability = row[4]
            role.used_secondary_ability = row[5]
            role.currently_alive = row[6]
            role.solo_win = row[7]
            role.statuses.drunk = row[8]
            role.statuses.linked = row[9]
            role.targets = row[-1]

            if row[6]: lovers.append(row[0])
            final_data[row[0]] = role

        if len(lovers) == 2:
            cupid: str = None
            for name, role in final_data:
                if role.name == "Cupid":
                    cupid = name
                    break

            final_data[lovers[0]].linked_to = lovers[1]
            final_data[lovers[1]].linked_to = lovers[0]
            final_data[lovers[0]].linker = cupid
            final_data[lovers[1]].linker = cupid

        self.players = Players(final_data)
        self.init(alter_drunk = False)

    @enforce_types
    def backup_to_json(self) -> None:
        input_data: dict[str, dict] = {}

        for name, role in self.players.items():
            # -- Handling Nested Objects -- #
            data: dict = role.__dict__
            statuses: dict = role.statuses.__dict__
            primary_ability: dict = role.ability.to_dict()
            secondary_ability: dict = role.secondary_ability.to_dict()

            primary_name, secondary_name = role.ability.__name__, role.secondary_ability.__name__

            data["statuses"] = statuses
            data["ability"] = primary_ability
            data["secondary_ability"] = secondary_ability

            # -- Extra Data For Reverse Operation -- #
            data["ability"]["name"] = primary_name
            data["secondary_ability"]["name"] = secondary_name

            input_data[name] = data

        with open("backup.json", "w") as file:
            json.dump(input_data, file, indent = 4, ensure_ascii = False)

    @enforce_types
    def load_from_json_backup(self) -> None:
        final_data: dict = {}

        with open("backup.json", "r") as file:
            out_data: dict = json.load(file)

        for player, data in out_data.items():
            # -- Dealing With Dictionaries of Nested Objects -- #
            status_data: dict = data["statuses"]
            ability_data: dict = data["ability"]
            secondary_ability_data: dict = data["secondary_ability"]

            primary_name, secondary_name = ability_data["name"], secondary_ability_data["name"]

            del ability_data["name"]
            del secondary_ability_data["name"]

            statuses: Status_Manager = Status_Manager()
            ability: Ability = deepcopy(self.true_ability_names[primary_name])
            secondary_ability: Ability = deepcopy(self.true_ability_names[secondary_name])

            for name, value in status_data.items():
                statuses.__setattr__(name, value)

            for name, value in ability_data.items():
                ability.set_attribuite(name, value)

            for name, value in secondary_ability_data.items():
                secondary_ability.set_attribuite(name, value)

            data["statuses"] = statuses
            data["ability"] = ability
            data["secondary_ability"] = secondary_ability

            # -- Main Role Object -- #
            role: Role = Role("temp", ability, True, False, 1, [], [], [], statuses)

            for name, value in data.items():
                role.__setattr__(name, value)

            final_data[player] = role
    
        self.players = Players(final_data)
        self.init(alter_drunk = False)