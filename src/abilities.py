# -- Imports -- #
from utils import *
from classes_and_types import Role, Game_Data, Ability
from game_loop_functions import *
from random import choice
from time import sleep
from re import fullmatch
import colorist
import json

# -- Roles -- #
class none(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 0, p = 25, ability_type = ["passive"])
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        pass

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        pass

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        pass

class vote(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 1, p = 0, ability_type = ["repeat"], can_pick_same_target = True)
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        pass

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        pass

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        pass

class reveal(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 1, p = 5, ability_type = ["repeat", "investigative"], priority = 7, can_pick_same_target = True)
        self.override: Literal[None, True, False] = None # -- Useful For Roles That Force A Specific Result -- #

    # -- Methods -- #
    @enforce_types
    def information(self, data: Game_Data, user: str, result: bool | None, target: str = "Your target") -> None:
        match self.override:
            case True: 
                data.players[user].information.append(f"{target} is GOOD!")
            case False: 
                data.players[user].information.append(f"{target} is EVIL!")
            case None:
                if result == True: data.players[user].information.append(f"{target} is GOOD!")
                elif result == False: data.players[user].information.append(f"{target} is EVIL!")
                else: data.players[user].information.append(f"{target} is NEUTRAL!")

        self.override = None
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        target: str = data.players[user].targets[0]
        alignment: bool = data.players[target].true_alignment

        self.information(data, user, alignment, target)

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        target: str = data.players[user].targets[0]

        if data.players[target].true_alignment is not None:
            alignment: bool = not data.players[target].alignment
        else:
            alignment = choice([True, True, False, None])

        self.information(data, user, alignment, target)

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        alignment: bool = choice([True, True, False])

        self.information(data, user, alignment)

class endure(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 0, p = 12.5, ability_type = ["passive", "defensive"], priority = 2)
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        data.players[user].statuses.protected = True

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        pass

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        pass

class protect(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 1, p = 7.5, ability_type = ["repeat", "defensive"], priority = 2)

    # -- Extra Methods -- #
    @enforce_types
    def check_for_mayor_case(self, target: str, data: Game_Data) -> bool:
        target_role: Role = data.players[target]
        return not (target_role.name == "Mayor" and target_role.solo_win)

    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        target: str = data.players[user].targets[0]

        if self.check_for_mayor_case(target, data): 
            data.players[target].protector = user
            data.players[target].statuses.protected = True

    def if_poisoned(self, user: str, data: Game_Data) -> None:
        pass

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        pass

class link(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 2, p = 0, ability_type = ["on_demand"], priority = 2, uses = 1)

    # -- Extra Methods -- #
    @enforce_types
    def link(self, data: Game_Data, user: str, link_1: str, link_2: str) -> None:
        data.players[link_1].statuses.linked = True
        data.players[link_2].statuses.linked = True

        data.players[link_1].linked_to = link_2
        data.players[link_2].linked_to = link_1

        data.players[user].ability = heart_break()
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        link_1: str = data.players[user].targets[0]
        link_2: str = data.players[user].targets[1]
        self.link(data, user, link_1, link_2)

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        self.ability(user, data)

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        link_1: str = choice([name for name, role in data.players.items() if role.name != "Cupid"])
        self.link(data, user, user, link_1)

@enforce_types
class cupid_victory(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 0, p = 0, ability_type = ["passive", "on_vote", "game_end"], priority = 2)

    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        user_role: Role = data.players[user]
        lovers: list[str] = data.get_lovers()

        if len(lovers) > 0:
            link_1: str = lovers[0]
            link_2: str = lovers[1]

            if link_1 in data.previous_deaths:
                if link_2 in data.previous_deaths or link_2 in data.second_previous_deaths:
                    user_role.solo_win = True
            
            if link_2 in data.previous_deaths:
                if link_1 in data.previous_deaths or link_1 in data.second_previous_deaths:
                    user_role.solo_win = True

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        self.ability(user, data)

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        self.ability(user, data)

class heart_break(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 1, p = 0, ability_type = ["on_demand"], priority = 2, uses = 1, can_pick_same_target = True)

    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        target: str = data.players[user].targets[0]

        if target in data.get_lovers():
            data.players[target].remaining_life_counter = 1
        else:
            self.number_of_uses += 1

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        self.ability(user, data)

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        self.ability(user, data)

class jester(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 0, p = 0, ability_type = ["on_death", "no_action_round"])
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data, does_effect: bool = True) -> None:
        data.players[user].solo_win = data.players[user].was_voted_out

        if data.players[user].solo_win and does_effect:
            for role in data.alive_players.values():
                role.statuses.poisoned = True

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        self.ability(user, data)

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        self.ability(user, data, does_effect = False)

class prosecute(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 1, p = 0, ability_type = ["on_vote", "no_action_round", "keep_targets"], uses = 1)
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        data.players[user].solo_win = data.players[data.players[user].targets[0]].was_voted_out

        if not (data.players[data.players[user].targets[0]].currently_alive or data.players[data.players[user].targets[0]].was_voted_out):
            data.players[user].solo_win = data.players[user].currently_alive

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        self.ability(user, data)

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        pass
        data.players[user].solo_win = not data.players[data.players[user].targets[0]].was_voted_out

        if not (data.players[data.players[user].targets[0]].currently_alive or data.players[data.players[user].targets[0]].was_voted_out):
            data.players[user].solo_win = data.players[user].was_voted_out

            if data.settings["Early End"] == 1 and data.players[user].solo_win:
                data.playing = False

class poison(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 1, p = 0, ability_type = ["repeat"], priority = 0)
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        target: str = data.players[user].targets[0]
        data.players[target].poisoned = True

        if data.players[target].ability == self or data.players[target].secondary_ability == self:
            # -- Prevents Unfair Poison Clashes -- #
            targets_target: str = data.players[target].targets[0]
            data.players[targets_target].poisoned = False

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        pass

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        pass

class kill(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 1, p = 0, ability_type = ["repeat"], priority = 5, can_pick_same_target = True)
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        user_role: Role = data.players[user]

        if "evil_priority" in user_role.secondary_ability.ability_type and user_role.secondary_ability.number_of_uses != 0:
            user_role.secondary_ability(user, data)
        else:
            target: str = data.players[user].targets[0]
            data.players[target].die(data.players)

            if user_role.secondary_ability == mayor:
                user_role.secondary_ability(user, data)

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        user_role: Role = data.players[user]
        if "evil_priority" in user_role.secondary_ability.ability_type and user_role.secondary_ability.number_of_uses != 0:
            user_role.secondary_ability(user, data)

        elif user_role.secondary_ability == mayor:
            user_role.secondary_ability(user, data)

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        pass

class telepathy(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 1, p = 0, ability_type = ["repeat", "investigative"], priority = 4, can_pick_same_target = True)

    # -- Methods -- #
    def show_info(self, user: str, data: Game_Data, user_role: Role, target: str, role: Role) -> None:
        user_role.information.append(f"Your psychic uncovered {role.name}!")
        temp_examine = examine()
        temp_examine(user, data)

        if user_role.name == "Psychic":
            mafia_roles: dict[str, Role] = {name: role for name, role in data.evil_aligned.items() if role.name != "Psychic"}

            for name, evil_role in mafia_roles.items():
                evil_role.information.append(f"{target} is {role.name}!")
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        target: str = data.players[user].targets[0]
        user_role = data.players[user]

        role: Role = data.players[target]
        
        self.show_info(user, data, user_role, target, role)

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        target: str = data.players[user].targets[0]
        user_role = data.players[user]

        if user_role.name == "Psychic":
            roles = [role for role in data.roles.values() if role.alignment]
        else:
            roles = list(data.roles.values())

        role: Role = choice(roles)

        self.show_info(user, data, user_role, target, role)

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        pass

class stalk(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 1, p = 7.5, ability_type = ["repeat", "investigative"], can_pick_same_target = True, priority = 11)
        self.invisible_players: set[str] = {}

    # -- Methods -- #
    @enforce_types
    def information(self, data: Game_Data, user: str, target: str, visitors: list[str]) -> None:
        target_str: str = f"{target} was visited by "
        count: int = 0

        # -- Removing Invisible Players -- #
        visitors = list(set(visitors).difference(self.invisible_players))
        self.invisible_players = {}

        # -- Filtering For " " and Case -- #
        for i in range(len(visitors)):
            visitor = visitors[count]

            if fullmatch(" ", visitor) or visitor == user:
                visitors.remove(visitor)
            else:
                count += 1
            
        for player in visitors:
            if player != user:
                target_str += player + ", "

        if len(visitors) > 0:
            target_str = target_str[:-2]
        else:
            target_str += "nobody"

        data.players[user].information.append(target_str)
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data, altered_target: str = None) -> None:
        visitors: list[str] = None
        
        if altered_target == None:
            target: str = data.players[user].targets[0]
        else:
            try:
                target: str = data.players[data.players[user].targets[0]].targets[0]
            except:
                visitors = []

        if visitors is None:
            visitors = data.players[target].visited_by

        self.information(data, user, target, visitors)

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        target: str = data.players[user].targets[0]

        selected_players = set([]) 
        visitors = set(data.players[target].visited_by)
        visitors.add(user)
        can_see = set(data.players.keys()) - visitors

        random_num: int = randint(0, len(can_see))
        can_see_too = list(can_see)
        for i in range(random_num): selected_players.add(choice(can_see_too))
        visitors = list(selected_players)

        self.information(data, user, target, visitors)

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        target: str = data.players[user].targets[0]
        self.ability(user, data, target)

class resurrect(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 1, p = 10, ability_type = ["on_demand", "defensive"], target_living = False, uses = 1)  
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        user_role: Role = data.players[user]
        evil = evil or not user_role.alignment

        if user_role.ability == self: # -- Gambler Check -- #
            ability_cancel = user_role.ability_cancel
        else:
            ability_cancel = user_role.secondary_ability_cancel

        if len(user_role.targets) > 0 and not ability_cancel:
            target = data.players[user_role.targets[0]]
            target.revive()

            target.information.append("You have Been Ressurected")

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        self.ability(user, data)
        data.players[user].remaining_life_counter = 1
        data.players[self.targets].remaining_life_counter = data.total_evil_count

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        pass

class vengance(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 1, p = 0, ability_type = ["on_death", "no_action_round"], can_pick_same_target = True)
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        if not data.players[user].was_voted_out:
            target = data.players[user].targets[0]
            role = data.players[target]
            role.protected = False
            role.die(data.players)

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        pass

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        pass

class ambush(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 1, p = 0, ability_type = ["repeat", "on_demand"], priority = 3, can_pick_same_target = True)
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data, active: bool = True) -> None:
        target = data.players[user].targets[0]
        visitors = deepcopy(data.players[target].visited_by)
        new_target: str = "nobody"

        try:
            visitors.remove(user)
        except:
            pass

        if active:
            try:
                new_target = visitors[0]
                visitors = visitors[1:]

                data.players[user].targets = [new_target]
                kill()(user, data)
            except:
                pass

        for player in visitors:
            data.players[player].information.append(f"Someone attempted to ambush {new_target}!")

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        self.ability(user, data, False)

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        pass

class mayor(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 0, p = 0, ability_type = ["passive", "game_end"], priority = 8)
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        if data.playing:
            if not data.players[user].solo_win:
                sleep(0.5)
                if messagebox.askyesno("Mayor", f"Has {user} claimed mayor?", icon = "question"):
                    data.players[user].solo_win = True
        else:
            data.players[user].solo_win = len(data.players) == data.players[user].alternative_end_count
            
    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        self.ability(user, data)

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        if data.playing:
            messagebox.showinfo("Info", f"The May Is Drunk Silly, So Nothing Should Happen", icon = "info")
            data.players[user].alternative_end_count = 2
        else:
            data.players[user].solo_win = len(data.players) == data.players[user].alternative_end_count

class gamble(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 0, p = 0, ability_type = ["secondary_ability", "passive", "game_start"], priority = 6)
        self.used_abilities: set[str] = set([])
        self.non_starting_abilities: set[str] = set([])
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data, early_start: bool = False) -> None:
        role: Role = data.players[user]

        if early_start:
            self.non_starting_abilities: set[str] = {role.ability.true_name for role in data.roles.values()} - {role.ability.true_name for role in data.roles.values() if role.true_alignment == True}
            self.non_starting_abilities = self.non_starting_abilities.union({"none", "vote", "instant_death", "jackpot"})
            role_data: list[str, Ability] = data.random_ability(self.non_starting_abilities)
            
            self.used_abilities.add(role_data[0])
            role.secondary_ability = role_data[1]

            if data.settings["Instant Death"] == 0:
                self.used_abilities.add("instant_death")
        else:
            role.secondary_ability(user, data)

            role_data: list[str, Ability] = data.random_ability(self.used_abilities)
            role.secondary_ability = role_data[1]

            if role.secondary_ability == instant_death or role.secondary_ability == none or role.secondary_ability == jackpot:
                role.information.append(f"They rolled {role.secondary_ability.__name__}!")
            else:
                new_role: Role = data.get_role_by_ability(role.secondary_ability)
                new_card: str = new_role.name

                role.information.append(f"They rolled {new_role.name}, which has the card {new_card}!")

            role.ability.priority = role.secondary_ability.priority + 0.5

            if "instant" in role.secondary_ability.ability_type:
                role.secondary_ability(user, data)

            # -- Removed The Ability From Being Drawn Again -- #
            if not (role.secondary_ability == none or role.secondary_ability is None):
                self.used_abilities.add(role_data[0])

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        self.ability(user, data)

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        self.ability(user, data)

class instant_death(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 1, p = 2.5, ability_type = ["instant"])
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        data.players[user].remaining_life_counter = 0

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        pass

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        pass

class jackpot(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 0, p = 2.5, ability_type = [], priority = -777)
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        player_role = data.players[user]
        player_role.statuses.blessed = True
        ability: gamble = player_role.ability

        for role in data.evil_aligned.values():
            role.statuses.poisoned = True

        ability.used_abilities = {"instant_death", "jackpot"}

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        self.ability(user, data)

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        self.ability(user, data)

class magnet(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 2, p = 0, ability_type = ["repeat"], priority = 1)
        
    # -- Extra Methods -- #
    @enforce_types
    def poison_consideration(self, role: Role, target: Role) -> None:
        if isinstance(role.ability, poison):
            target.targets[0].poisioned = False # -- If We do Drunk, Change This -- #
            role.poisoned = True

    @enforce_types
    def magnetise(self, data: Game_Data, target_1: str, target_2: str, role: Role) -> None:
        target_role = data.players[target_1]

        if target_role.ability.target_living:
            if role.ability.targets == 1:
                target_role.targets = [target_2]
            elif role.ability.targets == 2:
                target_role.targets = [target_2, target_1]

    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        role: Role = data.players[user]
        targets = role.targets

        self.poison_consideration(role, targets[0])
        self.poison_consideration(role, targets[1])
                        
        self.magnetise(data, role.targets[0], role.targets[1], role)
        self.magnetise(data, role.targets[1], role.targets[0], role)

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        role: Role = data.players[user]
        targets = []

        for target_role in data.alive_players.values():
            if role.ability.target_living and target_role.ability != self:
                targets.append(target_role.name)
                self.poison_consideration(role, target_role)

        self.magnetise(data, user, role, targets)

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        pass

class index(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 0, p = 10, ability_type = ["passive", "investigative"], priority = 9)
        self.seen_roles: set[str] = {"Mafia"}
        self.blind_roles: set[str] = {} # -- Roles That Cannot Be Seen On A Temporary Basis -- #

    # -- Properties -- #
    @property
    @enforce_types
    def count(self) -> int:
        return len(self.seen_roles)

    # -- Methods -- #
    @enforce_types
    def information(self, data: Game_Data, user_role: Role, selected_set: set[str]) -> None:
        if len(selected_set) > 0 and self.count < len(data.players):
            selected_role: str = choice(list(selected_set))

            self.seen_roles.add(selected_role)
            user_role.information.append(f"{selected_role}!")

    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        normal_roles: set[str] = set([role.name for role in data.players.values()])

        user_role: Role = data.players[user]
        self.seen_roles.add(user_role.name)

        selected_set: set[str] = normal_roles - (self.seen_roles.union(self.blind_roles))
        self.information(data, user_role, selected_set)
        self.blind_roles = {}

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        all_roles: set[str] = set(data.roles.keys())
        normal_roles: set[str] = set([role.name for role in data.players.values()])

        user_role: Role = data.players[user]
        self.seen_roles.add(user_role.name)
        selected_set: set[str] = all_roles - normal_roles - self.seen_roles

        self.information(data, user_role, selected_set)

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        all_roles: set[str] = set(data.roles.keys())

        user_role: Role = data.players[user]
        self.seen_roles.add(user_role.name)
        selected_set: set[str] = all_roles - self.seen_roles

        self.information(data, user_role, selected_set)
    
class examine(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 1, p = 12.5, ability_type = ["repeat", "investigative"], priority = 10, can_pick_same_target = True)

    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data, info_reciever: str = None) -> None:
        target: str = data.players[user].targets[0]
        role: Role = data.players[target]

        if info_reciever is None:
            for item in role.statuses.get_data(target):
                data.players[user].information.append(item)
        else:
            for item in role.statuses.get_data(target):
                data.players[info_reciever].information.append(item)

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data, info_reciever: str = None) -> None:
        target: str = data.players[user].targets[0]
        role: Role = data.players[target]

        if info_reciever is None:
            for item in role.statuses.get_data(target, inverse = True):
                data.players[user].information.append(item)
        else:
            for item in role.statuses.get_data(target, inverse = True):
                data.players[info_reciever].information.append(item)

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data, info_reciever: str = None) -> None:
        target: str = data.players[user].targets[0]
        role: Role = data.players[target]

        if info_reciever is None:
            for item in role.statuses.bullshit_data(target, inverse = True):
                data.players[user].information.append(item)
        else:
            for item in role.statuses.bullshit_data(target, inverse = True):
                data.players[info_reciever].information.append(item)

class super_kill(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 1, p = 0, ability_type = ["on_demand", "evil_priority"], priority = -1, can_pick_same_target = True, uses = 1)
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        target: str = data.players[user].targets[0]
        target_role: Role = data.players[target]
        protected: bool = target_role.statuses.protected

        target_role.statuses.protected = False
        target_role.die(data.players)
        target_role.statuses.protected = protected

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        pass

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        pass

class witness_protection(Ability):
    @enforce_types
    def __init__(self):
        # -- A Variant of Protection For Lawyer -- #
        super().__init__(targets = 0, p = 0, ability_type = ["on_demand", "keep_targets", "defensive"], priority = 2, uses = "x-1")

    # -- Extra Methods -- #
    @enforce_types
    def check_for_mayor_case(self, target: str, data: Game_Data) -> bool:
        target_role: Role = data.players[target]
        return not (target_role.name == "Mayor" and target_role.solo_win)
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        target: str = data.players[user].targets[0]

        if self.check_for_mayor_case(target, data): 
            data.players[target].protected = True

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        self.ability(self, user, data)

class evidence_tampering(Ability):
    @enforce_types
    def __init__(self):
        # -- A Variant of Protection For Lawyer -- #
        super().__init__(targets = 0, p = 0, ability_type = ["on_demand", "keep_targets"], priority = -2, uses = "x-1")

    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        # -- Fucks With Any Attempt To Catch Out The Client That Night -- #
        informational_roles: list[tuple[Role, Ability]] = [[role, role.ability] for role in data.good_aligned.values() if "investigative" in  role.ability.ability_type]
        client: str = data.players[user].targets[0]
        client_role_name: str = data.players[client].name

        for role in data.good_aligned.values():
            if role.ability == gamble:
                if "investigative" in role.secondary_ability.ability_type:
                    informational_roles.append((role, role.secondary_ability))

        for role, ability in informational_roles:
            if client in role.targets:
                match ability:
                    case reveal():
                        ability.override = True
                    case stalk():
                        ability.invisible_players.add(client)
                    case _:
                        pass
            else:
                match ability:
                    case index():
                        ability.blind_roles.add(client_role_name)
                    case _:
                        pass

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        self.ability(self, user, data)

class stop_vote(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 1, p = 0, ability_type = ["on_vote", "first_night", "keep_targets"], priority = 10, uses = 1)
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data, first_night: bool = False) -> None:
        user_role = data.players[user]
        target: str = user_role.targets[0]
        target_role: Role = data.players[target]

        if first_night: 
            user_role.information.append(f"{target} is {target_role.name}!")

            if target_role.alignment:
                user_role.ability, user_role.secondary_ability = deepcopy(data.abilities["witness_protection"]), user_role.ability
            else:
                user_role.ability, user_role.secondary_ability = deepcopy(data.abilities["evidence_tampering"]), user_role.ability
        
        user_role.solo_win = not data.players[target].was_voted_out

        if not (target_role.currently_alive or target_role.was_voted_out):
            user_role.solo_win = data.players[user].currently_alive
            
            if user_role.ability != stop_vote:
                user_role.ability, user_role.secondary_ability = user_role.secondary_ability, user_role.ability

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data, first_night: bool = False) -> None:
        self.ability(user, data, first_night)

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        pass

class bless(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 1, p = 0, ability_type = ["on_demand"], uses = 1, priority = 1.1)
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        user_role: Role = data.players[user]
        target: str = user_role.targets[0]
        target_role: Role = data.players[target]

        target_role.statuses.blessed = True

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        pass

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        pass

class vulnerable(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 0, p = 0, ability_type = ["on_death", "no_action_round"])
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        player: Role = data.players[user]

        if player.was_voted_out:
            remaining_good_dict = {name: role for name, role in data.good_aligned.items() if role.true_alignment == True}

            if len(remaining_good_dict) > 0:
                player = choice(list(remaining_good_dict.values()))
                player.remaining_life_counter = 1

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        self.ability(user, data)

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        self.ability(user, data)

class execute(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 1, p = 5, ability_type = ["on_demand"], priority = -1, can_pick_same_target = True, uses = 1)
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        target: str = data.players[user].targets[0]
        target_role: Role = data.players[target]

        if target_role.true_alignment != True:
            target_role.die(data.players)

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        target: str = data.players[user].targets[0]
        target_role: Role = data.players[target]

        if target_role.alignment:
            target_role.die(data.players)

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        pass
    
class silence(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 1, p = 0, ability_type = ["repeat", "on_demand"], priority = 1)
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        target: str = data.players[user].targets[0]
        target_role: Role = data.players[target]
        target_role.statuses.silenced = True

        if target_role.statuses.silenced:
            info: list[str] = deepcopy(target_role.information)

            if len(info) > 0:
                data.players[user].information += [f"You Stole The Following From {target}"] + info
            else:
                data.players[user].information += [f"{target} Learned Nothing Tonight"] + info

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        data.players[user].statuses.silenced = True

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        pass

class sidequest(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 0, p = 0, ability_type = ["repeat", "on_vote", "first_night"], priority = 12)
        self.tasks : list[str] = []
        self.completed_tasks = 0
        self.total_tasks = 0
        self.required_tasks = 0
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data, first_night: bool = False) -> None:
        user_role: Role = data.players[user]

        if first_night:
            self.total_tasks = data.total_evil_count + 3
            self.required_tasks = self.total_tasks - 1
            solo_count = self.total_tasks // 2
            social_count = self.total_tasks - solo_count
            
            with open("crewmate_tasks.json", "r") as file:
                data: dict = json.load(file)
                solo_tasks: list[str] = data["solo_tasks"]
                social_tasks: list[str] = data["social_tasks"]
                shuffle(solo_tasks)
                shuffle(social_tasks)

                self.tasks = solo_tasks[:solo_count] + social_tasks[:social_count]
                self.tasks[-1] += "\n"

            user_role.information.append(f"Your Tasks Are:" + "".join(["\n  " + chr(i + 97) + ") " + self.tasks[i] for i in range(len(self.tasks))]))

        else:
            check = None
            while check is None:
                check = messagebox.askyesnocancel("Ability", f"Has {user}, the {user_role.name} completed a task?", default = "cancel", icon = "question")
                sleep(0.5)

            if check:
                self.completed_tasks += 1
                if self.completed_tasks >= self.required_tasks:
                    user_role.solo_win = True
                    data.playing = False

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data, first_night: bool = False) -> None:
        self.ability(user, data, first_night)

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data, first_night: bool = False) -> None:
        self.ability(user, data, first_night)