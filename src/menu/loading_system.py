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
def new_get_roles(player_count: int,  settings: dict, offset: int = 1) -> list[list[Role]]:
    # -- Uses Role Load System V4 -- #
    global good_data, neutral_data, evil_data, boundary_data, max_players

    # -- Guarenteed Roles -- #
    roles: list[list[Role]] = [[evil_data["lead"]]]
    evil_boundaries: list[int] = boundary_data["evil_support"]
    player_count += offset
    
    # -- Adding The Evil Roles -- #
    evil_range: list[bool] = [player_count >= num for num in evil_boundaries]

    for item in evil_range:
        if item:
            roles.append(deepcopy(evil_data["support"]))

    for item in boundary_data["guarenteed"][1:]:
        roles.append(choice(good_data[item]))

    # -- Adding All Of The Other Roles -- #
    non_evil: list[list[str]] = good_data["information"] + good_data["defensive"] + good_data["other"] + neutral_data["roles"]
    all_unselected_roles: list[list[str]] = [role for role in non_evil if role not in roles] #list(set(non_evil) - set(roles))
    shuffle(all_unselected_roles)
    all_unselected_roles = all_unselected_roles[:-1 * (len(boundary_data["evil_support"]) + 1)]

    # -- Testing Role -- #
    if settings["Testing Role"]["value"] == 1:
        all_unselected_roles.insert(0, ["Testing"])

    for i in range(player_count - len(roles)):
        if i < len(all_unselected_roles):
            roles.append(all_unselected_roles[i])
        else: break

    # -- Filters Any Overflow (Fixing Shuffle Bug) -- #
    if len(roles) > player_count:
        roles = roles[:player_count]

    update_settings()
    shuffle(roles)

    # -- Adding In Overflow Role If We Have Too Many Players -- #
    if player_count > max_players:
        for i in range(player_count - max_players):
            roles.append(deepcopy(boundary_data["overflow"]))

    return roles