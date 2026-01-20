# -- Imports -- #
import utils
from classes import Role

# -- Roles -- #
@utils.enforce_types
def none(players: dict[str, Role]) -> None:
    pass
