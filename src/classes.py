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
    individual: bool
    priority: int
    currently_alive: bool = True
    protected: bool = False
    poisoned: bool = False
    linked: bool = False
    is_protected: bool = False

    # -- Methods -- #

    @enforce_types
    def get_link(self, players: list[dict[str, Any]]) -> dict[str, Any]:
        for key, role in players.items():
            if role.linked and role.name != self.name:
                return {key, role}
            
        return {}
