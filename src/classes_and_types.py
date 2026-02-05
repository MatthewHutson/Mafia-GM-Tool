# -- Imports -- #
from dataclasses import dataclass
from utils import *
from random import shuffle
from copy import deepcopy

# -- Role Class -- #
@dataclass
class Role:
    # -- Attributes - #
    name: str
    ability: Callable
    _alignment: bool # True Being Good, False Being Evil #
    mafia_alternative: bool # Switches to Mafia Abiltity When All Normal Mafia Dies #
    priority: int # Order of Execution of Abilities From Lowest To Highest #
    max_count: int
    ability_type: list[str] # Can contain "singular", "passive", "repeat", "on death", "on vote", "on_demand", "recurse_targets" and "activate_again" #
    targets: list[object]
    information: list[str]
    visited_by: list[str]
    currently_alive: bool = True
    protected: bool = False
    poisoned: bool = False
    linked: bool = False
    linker: str = None
    linked_to: str = None
    used_ability: bool = False
    selected_target = False
    solo_win: bool = False
    was_voted_out: bool = False
    just_died: bool = False
    ability_cancel: bool = False # For "on_demand"
    recursion_fuck_up: bool = False
    channeled_role: str = None

    # -- Properties -- #
    @property
    @enforce_types
    def alignment(self) -> bool:
        if self._alignment == None: return True
        else: return self._alignment

    @property
    def true_alignment(self) -> bool | None:
        return self._alignment
    
    @property
    @enforce_types
    def named_alignment(self) -> str:
        match(self._alignment):
            case None: return "Neutral"
            case True: return "Good"
            case False: return "Evil"

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
    def on_death_ability(self, data: object) -> None:
        if "on_death" in self.ability_type and not "on_vote" in self.ability_type and self.just_died:
            user = list(data.players.keys())[list(data.players.values()).index(self)]
            self.ability(user, data)
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

    # -- Properties -- #
    @property
    def role_dict(self) -> Players:
        return Players({role.name: role for role in self.roles})

    # -- Methods -- #
    @enforce_types
    def assign_roles(self) -> Players:
        shuffle(self.players)
        shuffle(self.roles)
        return Players({self.players[i]: self.roles[i] for i in range(len(self.players))})
    
    @enforce_types
    def filter_roles(self, roles: list[str]) -> None:
        self.roles = [deepcopy(self.role_dict[role]) for role in roles]
    
@dataclass
class Game_Data():
    # -- Attributes -- #
    players: Players
    mafia_role: Role
    none_role: Role
    priority: Players = None
    good_aligned: Players = None
    evil_aligned: Players = None
    alive_players: Players = None
    dead_players = None
    playing: bool = True
    good_win: bool = False
    evil_win: bool = False

    # -- Properties -- #
    @property
    def next_evil_player(self) -> str | None:
        try:
            player = next(iter(self.evil_aligned.keys()))
            if self.players[player].mafia_alternative:
                return player
            else:
                return self.next_evil_player
        except: 
            return None

    # -- Methods -- #
    def init(self, vote_function: Callable) -> None:
        self.priority = Players(dict(sorted(self.players.items(), key = lambda item: item[1].priority)))
        self.good_aligned = Players({name: role for name, role in self.players.items() if role.alignment})
        self.evil_aligned = Players({name: role for name, role in self.players.items() if not role.alignment})
        self.alive_players = self.players.deepcopy()
        self.dead_players = Players({})
        self.vote_role: Role = Role("Voting", vote_function, True, False, 999, 999, "passive", [], [], []) # -- Using A Role For Menu Purposes -- #