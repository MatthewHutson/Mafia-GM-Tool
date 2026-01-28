# -- Imports -- #
from dataclasses import dataclass
from utils import *
from random import shuffle

# -- Role Class -- #
@dataclass
class Role:
    # -- Attributes - #
    name: str
    ability: Callable
    _alignment: bool # True Being Good, False Being Evil #
    mafia_alternative: bool # Switches to Mafiaa Abiltity When All Normal Mafia Dies #
    priority: int # Order of Execution of Abilities From Lowest To Highest #
    max_count: int
    ability_type: str # Either "singular", "passive", "repeat", "on death" or "on vote" #
    targets: list[object]
    currently_alive: bool = True
    protected: bool = False
    poisoned: bool = False
    linked: bool = False
    is_protected: bool = False
    linker: str = None
    linked_to: str = None
    used_ability: bool = False

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
        if self.poisoned or (not self.is_protected): 
            if not (self.linked and recurse): 
                self.currently_alive = False
                return True
            elif recurse and (not players[self.linker].poisoned): # Recursion Base Case and Cupid Poison Check #
                if players[self.linked_to].die(players, recurse = False):
                        self.currently_alive = False
                        return True
                
        return False

    @enforce_types
    def voted_out(self, players: dict[str, object]) -> bool:
        self.die()
        jester_win: bool = self.ability.__name__ == "Jester" and (not self.poisoned)
        if self.linked: jester_win = jester_win or (players[self.linked_to].ability.__name__ == "Jester" and (not players[self.linked_to].poisoned))
        return jester_win
    
    @enforce_types
    def __eq__(self, value: str) -> None:
        return self.name == value
    
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
    
    @enforce_types
    def __delitem__(self, key: str) -> None:
        return super().__delitem__(key)
    
# -- Data Handling Classes -- #
@dataclass
class Menu_Entry:
    players: list[str]
    roles: list[Role]

    # -- Properties -- #
    @property
    def role_dict(self) -> dict[str, Role]:
        return {role.name: role for role in self.roles}

    # -- Methods -- #
    @enforce_types
    def assign_roles(self) -> Players:
        shuffle(self.roles)
        print([role.name for role in self.roles])
        return Players({self.players[i]: self.roles[i] for i in range(len(self.players))})
    
    @enforce_types
    def filter_roles(self, roles: list[str]) -> None:
        dict = self.role_dict
        self.roles = [dict[name] for name in roles]
    
@dataclass
class Game_Data():
    # -- Attributes -- #
    players: Players
    priority: Players = None
    good_aligned: Players = None
    evil_aligned: Players = None
    alive_players: Players = None
    dead_players = Players({})

    # -- Methods -- #
    def innit(self) -> None:
        self.priority = Players(dict(sorted(self.players.items(), key = lambda item: item[1].priority)))
        self.good_aligned = Players({name: role for name, role in self.players.items() if role.alignment})
        self.evil_aligned = Players({name: role for name, role in self.players.items() if not role.alignment})
        self.alive_players = self.players.deepcopy()

        # -- Filter The Sherrif To Be Last -- #
        sherrif: dict[str, Role] = {name: role for name, role in self.players.items() if role.name == "Sherrif"}
        sherrif_name = next(iter(sherrif))
        del self.players[sherrif_name]
        self.players[sherrif_name] = sherrif[sherrif_name]