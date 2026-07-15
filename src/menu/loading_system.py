# -- Imports -- #
from utils import *
from menu.menu_classes import *
from menu.settings import update_settings
from random import choice, shuffle
import json

# -- Global Variables -- #
max_players: int = 0
good_data: dict = None
neutral_data: dict = None
evil_data: dict = None
boundary_data: dict = None

# -- Methods -- #
@enforce_types
def load_role_data() -> int:
    # -- Role Load System V4 -- #
    global data, good_data, neutral_data, evil_data, boundary_data, max_players

    with open("loading_data.json", "r") as file:
        data = json.load(file)
    
    good_data = data["good"]
    neutral_data = data["neutral"]
    evil_data = data["evil"]
    boundary_data = data["boundaries"]

    max_players = len(good_data["information"]) + len(good_data["defensive"]) + len(good_data["other"]) + len(neutral_data["roles"])
    return max_players

@enforce_types
def new_get_roles(player_count: int, settings: dict, offset: int = 1) -> list[list[Role]]:
    # -- Uses Role Load System V4 -- #
    global good_data, neutral_data, evil_data, boundary_data, max_players
    update_settings()

    # -- Guarenteed Roles -- #
    shuffle(evil_data["lead"])
    roles: list[list[Role]] = [deepcopy((evil_data["lead"]))]
    evil_boundaries: list[int] = boundary_data["evil_support"]
    player_count += offset

    # -- Adding The Evil Roles -- #
    evil_range: list[bool] = [player_count >= num for num in evil_boundaries]

    for item in evil_range:
        if item:
            roles.append(deepcopy(evil_data["support"]))

    for item in boundary_data["guarenteed"][1:]:
        shuffle(good_data[item])
        roles.append(deepcopy(choice(good_data[item])))

    # -- Adding All Of The Other Roles -- #
    non_evil: list[list[str]] = good_data["information"] + good_data["defensive"] + good_data["other"] + neutral_data["roles"]
    all_unselected_roles: list[list[str]] = [role for role in non_evil if role not in roles] #list(set(non_evil) - set(roles))
    shuffle(all_unselected_roles)

    # -- Testing Role -- #
    if settings["Testing Role"]["value"] == 1:
        all_unselected_roles.insert(0, ["Testing"])

    all_unselected_roles = all_unselected_roles[:-1 * (len(boundary_data["evil_support"]) + 1)]

    for i in range(player_count - len(roles)):
        if i < len(all_unselected_roles):
            roles.append(deepcopy(all_unselected_roles[i]))
        else: break

    # -- Filters Any Overflow (Fixing Shuffle Bug) -- #
    if len(roles) > player_count:
        roles = roles[:player_count]

    shuffle(roles)

    # -- Adding In Overflow Role If We Have Too Many Players -- #
    if player_count > max_players:
        for i in range(player_count - max_players):
            roles.append(deepcopy(boundary_data["overflow"]))

    return roles

@enforce_types
def get_all_role_lists() -> list[list[str]]:
    # -- Start By Getting Each Category -- #
    info_roles: list[list[str]] = good_data["information"]
    defensive_roles: list[list[str]] = good_data["defensive"]
    other_good_roles: list[list[str]] = good_data["other"]

    neutral_roles: list[list[str]] = neutral_data["roles"]

    evil_lead: list[list[str]] = evil_data["lead"]
    evil_support: list[list[str]] = [evil_data["support"]]

    # -- Create The Output Roles -- #
    all_roles: list[list[str]] = deepcopy(info_roles) + deepcopy(defensive_roles) + deepcopy(other_good_roles) + deepcopy(neutral_roles) + deepcopy(evil_lead) + deepcopy(evil_support)

    return all_roles

@enforce_types
def unpack_role_types(roles: dict, loaded_role_data: dict, role_functions: dict, alignment: bool | Literal[None]) -> None:
    for name, data in loaded_role_data.items():
        ability_name: str = data["ability"]  
        data["ability"] = deepcopy(role_functions[ability_name])

        if "secondary_ability" in data.keys():
            secondary_name: str = data["secondary_ability"]
            data["secondary_ability"] = deepcopy(role_functions[secondary_name])

        data["abilities"] = {}
            
        roles[name] = Role(name = name, _alignment = alignment, **data)