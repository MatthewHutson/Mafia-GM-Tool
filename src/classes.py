# -- Imports -- #
from dataclasses import dataclass
from utils import *

@dataclass
class Role():
    name: str
    ability: Callable
    alignment: bool # True Being Good, False Being Evil #
    individual: bool
    currently_alive: bool = True
    protected: bool = False
    poisoned: bool = False