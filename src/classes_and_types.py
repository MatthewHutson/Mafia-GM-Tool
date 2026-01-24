# -- Imports -- #
from dataclasses import dataclass
from utils import *
from typing import cast
from copy import deepcopy

# -- Role Class -- #
@dataclass
class Role():
    # -- Attributes - #
    name: str
    ability: Callable
    alignment: bool # True Being Good, False Being Evil #
    mafia_alternative: bool # Switches to Mafiaa Abiltity When All Normal Mafia Dies #
    priority: int # Order of Execution of Abilities From Lowest To Highest #
    max_count: int
    ability_type: str # Either singular, passive or repeat #
    targets: list[object]
    currently_alive: bool = True
    protected: bool = False
    poisoned: bool = False
    linked: bool = False
    is_protected: bool = False
    linker: str = None
    linked_to: str = None
    used_ability: bool = False

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
    def __eq__(self, value) -> None:
        return self.name == value
    
# -- Type Definitions -- #
class Players(dict[str, Role]):
    @enforce_types
    def __setitem__(self, key: str, value: Role):
        key = key.lower().capitalize()
        return super().__setitem__(key, value)
