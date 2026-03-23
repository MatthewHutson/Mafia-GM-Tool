# -- Imports -- #
from dataclasses import dataclass
from utils import *
from random import shuffle
from copy import deepcopy
import numpy as np

# -- Ability Template Class -- #
class Ability():
    @enforce_types
    def __init__(self, targets: int, p: Union[int, float], ability_type: list[str], target_living: bool = True, priority: int = 255, can_pick_same_target: bool = False) -> None:
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

    # -- Methods -- #
    def ability(self, user: str, data: object) -> None:
        ...

    @enforce_types
    def __call__(self, user: str, data: object) -> None:
        self.ability(user, data)

    @enforce_types
    def __eq__(self, ability2: Union[object, type]) -> bool:
        if type(ability2) == type:
            return type(self) == ability2
        else:
            return type(ability2) == type(self)

# -- Role Class -- #
@dataclass
class Role:
    # -- Attributes - #
    name: str
    ability: Ability
    _alignment: bool # True Being Good, False Being Evil #
    mafia_alternative: bool # Switches to Mafia Abiltity When All Normal Mafia Dies #
    max_count: int
    current_targets: list[object]
    information: list[str]
    visited_by: list[str]
    secondary_ability: Ability = None
    new_mafia = False # For Mafia Alternative Handling
    currently_alive: bool = True
    protected: bool = False
    poisoned: bool = False
    linked: bool = False
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
        return self.secondary_ability.used_ability
    
    @used_secondary_ability.setter
    @enforce_types
    def used_ability(self, value: bool) -> None:
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
    def die(self, players: dict[str, object], recurse: bool = True) -> bool:
        if not self.protected: 
            self.currently_alive = False
            self.just_died = True

            if self.linked and recurse and (not players[self.linker].poisoned): # Recursion Base Case and Cupid Poison Check #
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
        return f"Role: {self.name}, Alignment: {self.named_alignment}, Primary Ability: {self.ability.__name__}, Secondary Ability: {self.secondary_ability.__name__}, Alive: {self.currently_alive}"

    @enforce_types
    def on_death_ability(self, data: object) -> None:
        if "on_death" in self.ability_type and not "on_vote" in self.ability_type and self.just_died:
            user = list(data.players.keys())[list(data.players.values()).index(self)]
            self.ability(user, data)
            
        if "on_death" in self.secondary_ability.ability_type and not "on_vote" in self.secondary_ability.ability_type and self.just_died:
            user = list(data.players.keys())[list(data.players.values()).index(self)]
            self.secondary_ability(user, data)

        self.just_died = False

    @enforce_types
    def voted_out(self, players: dict[str, object], recurse: bool = True) -> None:
        self.was_voted_out = True
        self.die(players, False)
        if self.linked and recurse:
            players[self.linked_to].voted_out(players, False)
    
    @enforce_types
    def __eq__(self, value) -> bool:
        return self.name == str(value)
    
    @enforce_types
    def update_targets(self) -> None:
        self.previous_targets = deepcopy(self.targets)
    
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
    def deepcopy(self) -> dict[str, Role]:
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
        inactive_roles: list[list[str]] = []

        for role in self.all_roles:
            in_game = False

            for role_list in self.current_roles_lists:
                in_game = in_game or (role in role_list)
                if in_game: break
            
            if not in_game:
                for role_list in self.all_roles_lists:
                    if role in role_list:
                        inactive_roles.append(role_list)
        
        return deepcopy(inactive_roles)
    
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
    card_dict: dict[str, object]
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

    # -- Methods -- #
    def init(self) -> None:
        # -- Player Info -- #
        self.mafia_role = deepcopy(self.roles["Mafia"]) 
        self.none_role = deepcopy(self.roles["Villager"])

        self.good_aligned = Players({name: role for name, role in self.players.items() if role.alignment})
        self.evil_aligned = Players({name: role for name, role in self.players.items() if not role.alignment})

        self.alive_players = self.players.deepcopy()
        self.dead_players = Players({})

        self.settings = {name: data["value"] for name, data in self.menu_entries.settings.items()}

        # -- Using A Role For Menu Purposes -- #
        self.vote_role: Role = Role("Voting", self.abilities["vote"], True, False, 999, [], [], []) 
        
        # -- Secondary Ability Handling -- #
        for role in self.players.values():
            role.secondary_ability = deepcopy(self.abilities["none"])

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
    def random_ability(self, used_abilities: list[Role] = []) -> Ability:
        temp_dist: dict = {ability: probability for ability, probability in self.ablity_distribution.items() if not ability in used_abilities}
        total = sum(temp_dist.values())
        temp_dist = {key: value / total for key, value in temp_dist.items()}
        sample: list[str] = np.random.choice(np.array(list(temp_dist.keys())), size = 1, p = np.array(list(temp_dist.values())))
        return self.abilities[sample[0]]