# -- Imports -- #
from utils import enforce_types, valid_input_list
from classes import Role

# -- Roles -- #
@enforce_types
def none(players: dict[str, Role]) -> None:
    pass

@enforce_types
def reveal(players: dict[str, Role]) -> str:
    valid_input_list("", "", [])