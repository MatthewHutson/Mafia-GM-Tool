# -- Imports -- #
from dataclasses import dataclass
from utils import *
from typing import Any
from copy import deepcopy

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
    linker: object = None
    linked_to: object = None

    # -- Methods -- #
    @enforce_types
    def die(self, recurse: bool = True) -> bool:
        if self.poisoned or (not self.is_protected): 
            if (not self.linked) or self.poisoned: 
                self.currently_alive = False
                return True
            elif recurse and (not self.linker.poisoned): # Recursion Base Case and Cupid Poison Check #
                if self.linked_to.die(recurse = False):
                        self.currently_alive = False
                        return True
                
        return False

    @enforce_types
    def voted_out(self) -> bool:
        self.die()
        jester_win: bool = self.ability.__name__ == "Jester" and (not self.poisoned)
        if self.linked:jester_win = jester_win or (self.linked_to.ability.__name__ == "Jester" and (not self.linked_to.poisoned))
        return jester_win
