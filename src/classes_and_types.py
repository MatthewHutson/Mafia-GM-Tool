# -- Imports -- #
from __future__ import annotations
from dataclasses import dataclass
from utils import *
from random import shuffle, choice
from copy import deepcopy
from colorist import style_text, ColorHex
from enum import Enum
import numpy as np
import csv
import json

# -- Enums -- #
class colours(Enum):
    winning = "#00ff00"
    poisoned = "#96466e"
    drunk = "#de8c36"
    protected = "#c671ff"
    linked = "#ff00ff"
    blessed = "#22ffed"
    silenced = "#424242"
    doused = "#ff5e00"
    good = "#00ff00"
    evil = "#ff0000"
    neutral = "#ffffff"
    testing = "#36eeee"

# -- Ability Template Class -- #
@dataclass
class Status_Manager():
    # -- Statuses -- #
    poisoned: bool = False
    drunk: bool = False
    protected: bool = False
    linked: bool = False
    blessed: bool = False
    silenced: bool = False
    doomed: bool = False
    doused: bool = False

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
    def get_data(self, user: str = "", inverse = False, add_colours: bool = False, additions: dict[str, bool] = {}) -> list[str]:
        output: list[str] = []

        for status, value in (self.__dict__ | additions).items():
            if add_colours:
                colour: ColorHex = ColorHex(colours[status].value)
                out_string: str = style_text(status, colour)
            else:
                out_string: str = status

            if value ^ inverse:
                output.append(f"{user} is {out_string}.")
            else:
                output.append(f"{user} is NOT {out_string}.")

        return output
    
    @enforce_types
    def count_statuses(self, additions: dict[str, bool] = {}) -> int:
        count: int = 0

        for value in (self.__dict__ | additions).values():
            count += int(value)

        return count

    @enforce_types
    def bullshit_data(self, user: str) -> list[str]:
        output: list[str] = []
        for status in self.__dict__.items():
            extra: str = choice([" NOT", " NOT", " NOT", ""])
            output.append(f"{user} is{extra} {status}.")

        return output
    
    def __setattr__(self, name: str, value: Any) -> None:
        super().__setattr__(name, value)

        if self.blessed:
            cleared_effects: list[str] = ["poisoned", "drunk", "silenced"]
            for effect in cleared_effects:
                super().__setattr__(effect, False)

# -- Equation Type -- #
class equation():
    # -- A Simple Equation -- #
    @enforce_types
    def __init__(self, equation: str):
        temp: str = deepcopy(equation)
        temp = temp.replace("x", "0")

        try: eval(temp)
        except: raise TypeError

        self.equation = equation

    @enforce_types
    def get_value(self, x: int) -> int:
        equation: str = deepcopy(self.equation).replace("x", str(x))
        return eval(equation)
    
    @enforce_types
    def __str__(self) -> str:
        return self.equation + " (Equation)"

class Ability():
    @enforce_types
    def __init__(self, targets: int | list[int], p: int | float, ability_type: list[str], target_living: bool = True, priority: int = 255, can_pick_same_target: bool = False, uses: int | equation | str | None = None, refresh_max: int = 0) -> None:
        # -- Attributes -- #
        self.p: int | float = p
        self.ability_type: list[str] = ability_type
        self.target_living: bool = target_living
        self.priority: float = priority
        self.can_pick_same_target: bool = can_pick_same_target
        self.refresh_max = refresh_max
        self.refresh_count = 0
        self.selection_index = 0

        if not is_instance(uses, str): self.number_of_uses: int | equation = uses
        else: self.number_of_uses = equation(uses)

        self.target_list: list[int] = [targets] if isinstance(targets, int) else targets
        self.max_selection_index = len(self.target_list) - 1

    @property
    @enforce_types
    def __name__(self) -> str:
        return capitalise_words(type(self).__name__, "_")
    
    @property
    @enforce_types
    def true_name(self) -> str:
        return type(self).__name__
    
    @property
    @enforce_types
    def targets(self) -> int:
        return self.target_list[self.selection_index]
    
    @targets.setter
    @enforce_types
    def targets(self, value: int) -> None:
        self.target_list[self.selection_index] = value

    # -- Methods -- #
    def ability(self, user: str, data: Game_Data, **kwargs) -> None:
        ...

    def if_poisoned(self, user: str, data: Game_Data, **kwargs) -> None:
        ...

    def if_drunk(self, user: str, data: Game_Data, **kwargs) -> None:
        ...

    def __call__(self, user: str, data: Game_Data, **kwargs) -> None:
        if is_instance(self.number_of_uses, int):
            self.number_of_uses -= 1

        elif is_instance(self.number_of_uses, equation):
            self.number_of_uses: int = self.number_of_uses.get_value(data.total_evil_count)
            self.number_of_uses -= 1

        match data.players[user].statuses.ability_conditions():
            case [True, False]: self.if_poisoned(user, data, **kwargs)
            case [False, True]: self.if_poisoned(user, data, **kwargs)
            case _: self.ability(user, data, **kwargs)

    @enforce_types
    def __eq__(self, ability2: Ability | type | None) -> bool:
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
    abilities: dict[int, Ability]
    secondary_ability: Ability = None
    new_mafia = False # For Mafia Alternative Handling
    currently_alive: bool = True
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
    doom_count: int = None
    protector: str = None
    silencer: str = None
    
    # -- Properties -- #
    @property
    @enforce_types
    def alignment(self) -> bool:
        if self._alignment == None: return True
        else: return self._alignment

    @property
    @enforce_types
    def true_alignment(self) -> bool | Literal[None]:
        return self._alignment
    
    @property
    @enforce_types
    def ability_type(self) -> list[str]: # Can contain "passive", "on death", "on vote", "on_demand", "recurse_targets", "activate_again", "game_end" #
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
    def targets(self) -> list[str]:
        return self.current_targets
    
    @targets.setter
    @enforce_types
    def targets(self, value: list[str]) -> None:
        self.current_targets = value

    @property
    @enforce_types
    def remaining_life_counter(self) -> None:
        return self.doom_count

    @remaining_life_counter.setter
    @enforce_types
    def remaining_life_counter(self, value: int | Literal[None]) -> None:

        if value == None: self.statuses.doomed = False
        else: self.statuses.doomed = True

        if self.doom_count is not None:
            if value is None:
                self.doom_count = value
            else:
                if value < self.doom_count:
                    self.doom_count = value
        else:
            self.doom_count = value

    # -- Methods -- #
    @enforce_types
    def die(self, players: Players) -> bool:
        # -- Doctor Case -- #
        if self.protector is not None:
            doctor: Role = players[self.protector]
            
            if not doctor.statuses.poisoned:
                doctor.ability.can_pick_same_target = True
                doctor.ability.refresh_count = 0

        if not self.statuses.protected: 
            self.currently_alive = False
            self.just_died = True

            # -- Cupid Effect -- #
            if self.statuses.linked:
                players[self.linked_to].statuses.drunk = True

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
    def voted_out(self, players: Players) -> None:
        self.was_voted_out = True
        self.die(players)
    
    @enforce_types
    def __eq__(self, value) -> bool:
        return self.name == str(value)
    
    @enforce_types
    def update_targets(self) -> None:
        self.previous_targets = deepcopy(self.targets)

    def new(*args, **kwargs) -> Role:
        try: # Fix This Later
            return Role(*args, **kwargs, current_targets = [], information = [], visited_by = [], statuses = Status_Manager())
        except:
            return Role(*args, **kwargs, current_targets = [], information = [], visited_by = [], statuses = Status_Manager(), abilities = {})
    
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
    abilities: dict[str, Ability]
    ablity_distribution: dict[str, float]
    card_dict: dict[str, str]
    menu_entries: Menu_Entry
    announcements: list[str] = None
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
    win_steal: bool = False
    evil_count: int = 0
    total_evil_count: int = 0 # -- Holds Both Alive And Dead Evils -- #
    turn_count: int = 0
    previous_deaths: list[str] = None
    second_previous_deaths: list[str] = None
    wanted_data: list[str] = None
    temp_deaths: list[str] = None
    temp_ressurections: list[str] = None

    # -- Properties -- #
    @property
    @enforce_types
    def next_evil_player(self) -> str | None:
        if self.evil_count >= len(self.evil_aligned):
            return None
        else:
            player = list(self.evil_aligned)[self.evil_count]
            self.evil_count += 1
            if self.players[player].currently_alive:
                return player 
            else:
                return self.next_evil_player
    
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
        self.previous_deaths = []
        self.second_previous_deaths = []
        self.announcements = []
        self.temp_deaths = []
        self.temp_ressurections = []

        # -- Variable Count Considerations -- #
        if self.total_evil_count == 0:
            self.total_evil_count: int = len(self.evil_aligned)

        # -- Using A Role For Menu Purposes -- #
        self.vote_role: Role = Role.new("Voting", self.abilities["vote"], True, False, 999)
        
        # -- Secondary Ability Handling -- #
        for role in self.players.values():
            if role.secondary_ability is None:
                role.secondary_ability = deepcopy(self.abilities["none"])

        # -- statuses.drunk Consideration -- #
        if alter_drunk:
            self.set_drunk()

        # -- For Backup Purposes -- #
        self.wanted_data = ["turn_count", "deaths", "previous_deaths"]

    @enforce_types
    def set_drunk(self) -> None:
        if self.settings["Drunk"] == 1:
            valid_players: list = [name for name, role in self.players.items() if role.true_alignment == True]
            player = choice(valid_players)
            self.players[player].statuses.drunk = True

    @enforce_types
    def get_role_by_ability(self, ability: Ability, user: str = None) -> Role:
        for role in self.roles.values():
            if role.ability == ability:
                return role
            
        if user is not None:
            return deepcopy(self.players[user])
        
        return self.roles["Testing"]
    
    @enforce_types
    def get_card_by_role(self, role: Role) -> str:
        return role.name
    
    @enforce_types
    def random_ability(self, used_abilities: set[str] = set([])) -> list[str, Ability]:
        temp_dist: dict = {ability: probability for ability, probability in self.ablity_distribution.items() if not ability in used_abilities}
        total = sum(temp_dist.values())
        temp_dist = {key: value / total for key, value in temp_dist.items()}
        sample: list[np.str_] = np.random.choice(np.array(list(temp_dist.keys())), size = 1, p = np.array(list(temp_dist.values())))
        return [str(sample[0]), self.abilities[sample[0]]]
    
    @enforce_types
    def backup_to_json(self) -> None:
        input_data: dict[str, dict] = {}

        for name, role in self.players.items():
            # -- Handling Nested Objects -- #
            data: dict = role.__dict__
            statuses: dict = role.statuses.__dict__

            # -- Equation Type Handler -- #
            try:
                if is_instance(role.ability.number_of_uses, equation):
                    role.ability.number_of_uses = role.ability.number_of_uses.get_value(self.total_evil_count)

                if is_instance(role.secondaary_ability.number_of_uses, equation):
                    role.secondaary_ability.number_of_uses = role.secondary_ability.number_of_uses.get_value(self.total_evil_count)
            except: pass

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

        try:
            with open("backup.json", "w") as file:
                json.dump(input_data, file, indent = 4, ensure_ascii = False)

            with open("game_data_backup.json", "w") as file:
                game_data: dict = {name: value for name, value in self.__dict__.items() if name in self.wanted_data}
                json.dump(game_data, file, indent = 4, ensure_ascii = False)
        except:
            pass

    @enforce_types
    def load_from_json_backup(self) -> None:
        final_data: dict = {}

        with open("backup.json", "r") as file:
            out_data: dict = json.load(file)

        with open("game_data_backup.json", "r") as file:
            game_data: dict = json.load(file)
    
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
            role: Role = Role("temp", ability, True, False, 1, [], [], [], statuses, abilities = {})

            for name, value in data.items():
                role.__setattr__(name, value)

            final_data[player] = role
    
        self.players = Players(final_data)
        self.init(alter_drunk = False)

        game_data["turn_count"] -= 1

        for name, value in game_data.items():
            setattr(self, name, value)

    @enforce_types
    def update_life(self, update_data: bool = False) -> None:
        deaths: list[str] = []
        resurrections: list[str] = []

        for name, role in self.players.items():
            if name in self.alive_players.keys():
                if not role.currently_alive:
                    del self.alive_players[name]
                    self.dead_players[name] = role
                    deaths.append(name)
                    if role.alignment:
                        del self.good_aligned[name]
                    else:
                        del self.evil_aligned[name]

            if name in self.dead_players.keys():
                if role.currently_alive:
                    del self.dead_players[name]
                    self.alive_players[name] = role
                    resurrections.append(name)
                    if role.alignment:
                        self.good_aligned[name] = role
                    else:
                        self.evil_aligned[name] = role

        if update_data:
            full_deaths = deaths + [name for name in self.temp_deaths if name not in deaths]
            full_resurrections = resurrections + [name for name in self.temp_ressurections if name not in resurrections]

            full_deaths.sort(), full_resurrections.sort()

            deaths_info: list[str] = [f"\n       {chr(i + 97)}) {full_deaths[i]}" for i in range(len(full_deaths))]
            resurrections_info: list[str] = [f"\n       {chr(i + 97)}) {full_resurrections[i]}" for i in range(len(full_resurrections))]

            if len(full_deaths) == 0: self.announcements.append("Nobody Died Tonight!")
            else: self.announcements.append(f"The following players died tonight:" + "".join(deaths_info))
                
            if len(full_resurrections) > 0: self.announcements.append(f"The following players have been revived tonight:" + "".join(resurrections_info))

            if len(deaths) > 0:
                self.second_previous_deaths = deepcopy(self.previous_deaths)
                self.previous_deaths = deepcopy(deaths)

            self.temp_deaths = []
            self.temp_ressurections = []
            
        else:
            self.temp_deaths = deepcopy(deaths)
            self.temp_ressurections = deepcopy(resurrections)

    def get_lovers(self) -> list[str]:
        out: list[str] = [name for name, role in self.players.items() if role.statuses.linked]
        return out
    
    def death_announcements(self) -> None:
        pass