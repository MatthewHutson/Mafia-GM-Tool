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

class protect(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 1, p = 7.5, ability_type = ["repeat", "defensive"], priority = 2)

    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        target: str = data.players[user].targets[0]

        data.players[target].protector = user
        data.players[target].statuses.protected = True

    def if_poisoned(self, user: str, data: Game_Data) -> None:
        pass

class link(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 2, p = 0, ability_type = ["on_demand"], priority = 2, uses = "x")

    # -- Extra Methods -- #
    @enforce_types
    def link(self, data: Game_Data, user: str, link_1: str, link_2: str) -> None:
        data.players[link_1].statuses.linked = True
        data.players[link_2].statuses.linked = True

        #data.players[user].ability = heart_break()
        
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

        living = any([data.players[lover].currently_alive for lover in lovers])
        user_role.solo_win = (not living) or user_role.solo_win

        # if len(lovers) > 0:
        #     link_1: str = lovers[0]
        #     link_2: str = lovers[1]

        #     if link_1 in data.previous_deaths:
        #         if link_2 in data.previous_deaths or link_2 in data.second_previous_deaths:
        #             user_role.solo_win = True
            
        #     if link_2 in data.previous_deaths:
        #         if link_1 in data.previous_deaths or link_1 in data.second_previous_deaths:
        #             user_role.solo_win = True

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

class kill(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 1, p = 0, ability_type = ["repeat", "on_death"], priority = 5, can_pick_same_target = True)
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        user_role: Role = data.players[user]

        if not user_role.just_died:
            if "evil_priority" in user_role.secondary_ability.ability_type and user_role.secondary_ability.number_of_uses != 0:
                user_role.secondary_ability(user, data)
            else:
                target: str = data.players[user].targets[0]
                data.players[target].die(data)

                if user_role.secondary_ability == mayor:
                    user_role.secondary_ability(user, data)

        else: # -- Only When Mafia Dies -- #
            starpass().ability(user, data)

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        user_role: Role = data.players[user]
        if "evil_priority" in user_role.secondary_ability.ability_type and user_role.secondary_ability.number_of_uses != 0:
            user_role.secondary_ability(user, data)

        elif user_role.secondary_ability == mayor:
            user_role.secondary_ability(user, data)

        if user_role.just_died:
            starpass().ability(user, data)

class telepathy(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 0, p = 0, ability_type = ["investigative"], priority = 4, uses = 1)
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        user_role: Role = data.players[user]

        for name, role in data.players.items():
            if name != user:
                user_role.information.append(f"{name} is the {role.name}.")

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        self.ability(user, data)

class stalk(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 1, p = 7.5, ability_type = ["repeat", "investigative"], can_pick_same_target = True, priority = 11, uses = "x")
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
            role.statuses.protected = False
            role.die(data)

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
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

class mayor(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 0, p = 0, ability_type = ["passive", "game_end", "on_vote"], priority = 9999)
        self.protected = True
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        user_role: Role = data.players[user]

        if data.playing or data.current_life_count > user_role.alternative_end_count:
            if self.protected:
                user_role.statuses.protected = True
        else:
            data.playing = False
            user_role.solo_win = user_role.currently_alive
            
    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        self.ability(user, data)

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        if data.playing:
            messagebox.showinfo("Info", f"The Mayor Is Drunk Silly, So Nothing Should Happen", icon = "info")
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
        if not data.players[user].statuses.protected:
            data.players[user].remaining_life_counter = 0

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
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
        target_role.die(data)
        target_role.statuses.protected = protected

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
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
    def if_drunk(self, user: str, data: Game_Data, first_night: bool = False) -> None:
        self.ability(user, data, first_night)

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
        self.immune_players: set = {}

    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        target: str = data.players[user].targets[0]
        target_role: Role = data.players[target]

        if target_role.true_alignment != True and target not in self.immune_players:
            target_role.die(data)

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        target: str = data.players[user].targets[0]
        target_role: Role = data.players[target]

        if target_role.alignment and target not in self.immune_players:
            target_role.die(data)
    
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
            target_role.silencer = user

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        data.players[user].statuses.silenced = True

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

class calculated_risk(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = [0, 1, 1, 1, 0, 1], p = 0, ability_type = ["repeat", "selection"], priority = 3)

    # -- Backfires -- #
    @enforce_types
    def backfire(self, user: str, data: Game_Data) -> None:
        user_role: Role = data.players[user]
        target: str = user_role.targets[0] if len(user_role.targets) > 0 else None
        target_role: Role = data.players[target] if target is not None else None

        match self.selection_index:
            case 0: pass
            case 1: 
                target_role.statuses.protected = True
                target_role.statuses.silenced = True

            case 2: 
                target_role.information.append("The Thrillseeker Visited You!")

            case 3: 
                if not user_role.statuses.protected: user_role.remaining_life_counter = 2
                ability: Ability = poison()
                ability.ability(user, data)
            case 4: 
                valid_players: list[Role] = [role for role in data.dead_players.values() if role.true_alignment == True]
                
                ability: Ability = resurrect()
                ability.ability(user, data)

            case 5: user_role.remaining_life_counter = 1

    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        backfired: bool = False
        
        if not backfired:
            match self.selection_index:
                case 0: 
                    for role in data.players.values():
                        if user in role.targets:
                            match role.name:
                                case "Sheriff":
                                    if user in role.targets: 
                                        role.ability.override = True
                                case "Creep": role.ability.invisible_players.add(user)
                                case "Vigilantee": role.ability.immune_players.add(user)

                case 1:
                    ability: Ability = silence()
                    ability.ability(user, data)

                case 2: pass
                case 3: 
                    ability: Ability = poison()
                    ability.ability(user, data)

                case 4:
                    valid_players: list[Role] = [role for role in data.dead_players.values() if role.true_alignment == True]
                    
                    if len(valid_players) > 0:
                        target_role: Role = choice(valid_players)
                        target_role.revive()
                        target_role.true_alignment = False
                        target_role.information.append("You Have Been Revived & Are Now Evil!")

                case 5:
                    ability: Ability = super_kill()
                    ability.ability(user, data)

        else:
            self.backfire(user, data) 

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        self.backfire(user, data)

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        self.backfire(user, data)

class sabotage(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = [0, 0], p = 0, ability_type = ["repeat", "selection", "on_demand"], priority = -2)
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        match self.selection_index:
            case 0:
                for role in data.good_aligned.values():
                    if "investigative" in role.ability.ability_type or "investigative" in role.secondary_ability.ability_type:
                        role.statuses.poisoned = True
            case 1:
                for role in data.good_aligned.values():
                    if "defensive" in role.ability.ability_type or "defensive" in role.secondary_ability.ability_type:
                        role.statuses.poisoned = True

        if "selection" in self.ability_type:
            self.ability_type.remove("selection")
        else:
            self.number_of_uses = 0

        data.announcements.append("The Saboteur Used Their Ability Last Night!")

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        for role in data.evil_aligned.values():
            role.statuses.poisoned = True

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        for role in data.evil_aligned.values():
            role.statuses.poisoned = True

class sacrificial_protection(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 1, p = 0, ability_type = ["repeat"])

    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        user_role: Role = data.players[user]
        target_role: Role = data.players[user_role.targets[0]]
        protected: bool = user_role.statuses.protected

        if not target_role.currently_alive or target_role.doom_count == 0:
            target_role.currently_alive = True
            target_role.doom_count = None
            user_role.statuses.protected = False
            user_role.die(data)
            user_role.statuses.protected = protected
            target_role.information.append("You successfully protected your target!")

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        pass

class role_replicate(Ability):
    def __init__(self) -> None:
        super().__init__(targets = 0, p = 0, ability_type = ["on_vote", "no_action_round"])
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        user_role: Role = data.players[user]
        target_role: Role = user_role
        target: str = user
  
        for name, role in data.players.items():
            if role.was_voted_out and role.true_alignment == True:
                target_role = role
                target = name
        
        if target != user:
            user_role.ability = deepcopy(target_role.ability)
            user_role.secondary_ability = deepcopy(target_role.secondary_ability)

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        self.ability(user, data)
        data.players[user].statuses.drunk = True

class douse(Ability):
    def __init__(self) -> None:
        super().__init__(targets = 1, p = 0, ability_type = ["repeat", "alternate"])
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        user_role: Role = data.players[user]
        if not user_role.ability_cancel:
            target_role: Role = data.players[user_role.targets[0]]
            target_role.statuses.doused = True
        else:
            user_role.secondary_ability(user, data)

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        self.ability(user, data)

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        self.ability(user, data)

class incinerate(Ability):
    def __init__(self) -> None:
        super().__init__(targets = 0, p = 0, ability_type = [], uses = 1)
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        user_role: Role = data.players[user]

        for role in data.players.values():
            if role.statuses.doused:
                protected: bool = role.statuses.protected
                role.statuses.protected = False
                role.die(data)
                role.statuses.protected = protected
            
        alive_count: int = 0

        for name, role in data.players.items():
            if name != user:
                if role.currently_alive:
                    alive_count += 1

        user_role.solo_win = alive_count == 0
        data.win_steal = user_role.solo_win or data.win_steal
        user_role.ability = none()
        user_role.secondary_ability = none()

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        self.ability(user, data)

class jail(Ability):
    def __init__(self) -> None:
        super().__init__(targets = 1, p = 0, ability_type = [], priority = -3, can_pick_same_target = True)
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        user_role: Role = data.players[user]
        target_role: Role = data.players[user_role.targets[0]]

        target_role.statuses.protected = True
        target_role.ability_blocked = True

        target_role.information.append("Your ability Failed Last Night.")

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        pass

class rewind(Ability):
    def __init__(self) -> None:
        super().__init__(targets = 0, p = 0, ability_type = ["on_demand"], priority = 9, can_pick_same_target = True, uses = 1)

    # -- Methods -- #
    @enforce_types
    def count_visits(self, data: Game_Data) -> int:
        sum = 0
        
        for role in data.players.values():
            sum += int(role.picked_targets_tonight)

        return sum

    @enforce_types
    def information(self, role: Role, good: int, neutral: int, evil: int) -> None:
        role.information.append(f"There are {good} good players, {neutral} neutral players and {evil} evil players alive.")

    @enforce_types
    def fake_numbers(self, data: Game_Data) -> tuple[int]:
        good_count, evil_count, neutral_count = 0, 0, 0

        actual_good_count: int = len([role for role in data.alive_players.values() if role.true_alignment == True])
        actual_evil_count: int = len(data.evil_aligned)
        actual_neutral_count: int = len(data.good_aligned) - good_count

        total_evils: int = len([role for role in data.players.values() if role.true_alignment == False])
        alive_players = len(data.alive_players)
        possible_good: int = alive_players - 1

        while (good_count + evil_count + neutral_count == alive_players) and (good_count + neutral_count >= evil_count) and (good_count >= neutral_count) and (good_count != actual_good_count and evil_count != actual_evil_count and neutral_count != actual_neutral_count):
            good_count = randint(1, possible_good)
            evil_count = randint(1, min(total_evils, alive_players - 1))
            neutral_count = alive_players - good_count - evil_count

        return good_count, neutral_count, evil_count
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        user_role: Role = data.players[user]
        good_count: int = len([role for role in data.alive_players.values() if role.true_alignment == True])
        evil_count: int = len(data.evil_aligned)
        neutral_count: int = len(data.good_aligned) - good_count

        self.information(user_role, good_count, neutral_count, evil_count)

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        user_role: Role = data.players[user]

        good_count, evil_count, neutral_count = self.fake_numbers(data)
        self.information(user_role, good_count, neutral_count, evil_count)

class starpass(Ability):
    def __init__(self) -> None:
        super().__init__(targets = 0, p = 0, ability_type = ["on_death"], can_pick_same_target = True)
     
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        minion: str = data.next_evil_player

        if minion is not None:
            minion_role: Role = data.players[minion]
            minion_copy: Role = deepcopy(minion_role)
            user_role: Role = data.players[user]
            user_copy: Role = deepcopy(user_role)

            user_role = minion_copy.name
            user_role.ability = minion_copy.ability
            user_role.secondary_ability = minion_role.secondary_ability

            user_role.information.append(f"You Are Now The {user_role.name}!")

            minion_role.name = user_copy.name
            minion_role.ability = user_copy.ability
            minion_role.secondary_ability = minion_copy.ability

            minion_role.information.append(f"You have been promoted to the {minion_role.name}!")
 
    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        self.ability(user, data)

class chancellor(mayor):
    def __init__(self) -> None:
        super().__init__()

    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        if self.protected:
            fake_out: bool = messagebox.askyesno("Mayor Fake Out", f"Does {user} want to fake a mayor hit?", icon = "question", default = "no")

            if fake_out:
                self.protected = False
                data.announcements.append("Someone Attempted To Kill The Mayor")

        super().ability(user, data)
