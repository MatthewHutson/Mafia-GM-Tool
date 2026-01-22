# -- Imports -- #
from dataclasses import dataclass
from utils import *
from typing import Any

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
    currently_alive: bool = True
    protected: bool = False
    poisoned: bool = False
    linked: bool = False
    is_protected: bool = False
    linker: str | Any = None
    linked_to: str | Any = None

    # -- Methods -- #

    @enforce_types
    def get_link(self, players: list[dict[str, object]]) -> dict[str, object]:
        for key, role in players.items():
            if role.linked and role.name != self.name:
                return {key, role}
            
        return {}
    
    @enforce_types
    def kill(self) -> None: self.currently_alive = False

    @enforce_types
    def voted_out(self) -> bool:
        self.currently_alive = False
        return (self.ability.__name__ == "Jester" and (not self.poisoned))
