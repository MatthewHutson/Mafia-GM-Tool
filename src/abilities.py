# -- Imports -- #
from utils import *
from classes_and_types import Role, Game_Data, Ability
from game_loop_functions import *
from random import choice
from time import sleep
from re import fullmatch

# -- Roles -- #
class none(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 0, p = 22.5, ability_type = ["passive"])
    
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
        super().__init__(targets = 1, p = 5, ability_type = ["repeat"], priority = 9, can_pick_same_target = True)

    # -- Methods -- #
    @enforce_types
    def information(self, data: Game_Data, user: str, result: bool) -> None:
        if result: data.players[user].information.append(f"Your target is GOOD!")
        else: data.players[user].information.append(f"Your target is EVIL!")
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        target: str = data.players[user].targets[0]
        alignment: bool = data.players[target].alignment

        self.information(data, user, alignment)

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        target: str = data.players[user].targets[0]
        alignment: bool = not data.players[target].alignment

        self.information(data, user, alignment)

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        alignment: bool = choice([True, True, False])

        self.information(data, user, alignment)

class endure(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 0, p = 7.5, ability_type = ["passive"], priority = 2)
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        data.players[user].protected = True

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        pass

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        pass

class protect(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 1, p = 5, ability_type = ["repeat"], priority = 3)

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

    def if_poisoned(self, user: str, data: Game_Data) -> None:
        pass

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        pass

class link(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 2, p = 0, ability_type = ["singular", "on_demand"], priority = 4)

    # -- Extra Methods -- #
    @enforce_types
    def link(self, data: Game_Data, user: str, link_1: str, link_2: str) -> None:
        data.players[link_1].linked = True
        data.players[link_2].linked = True

        data.players[link_1].linker = user
        data.players[link_2].linker = user

        data.players[link_1].linked_to = link_2
        data.players[link_2].linked_to = link_1
        
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

class jester(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 0, p = 5, ability_type = ["on_death"])
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        data.players[user].solo_win = data.players[user].was_voted_out

        if data.settings["Early End"] == 1 and data.players[user].solo_win:
            data.playing = False

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        self.ability(user, data)

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        pass
        # data.players[user].solo_win = data.players[user].currently_alive

class stop_vote(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 1, p = 5, ability_type = ["singular", "on_vote"])
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        data.players[user].unemployed = False
        data.players[user].solo_win = not data.players[data.players[user].targets[0]].was_voted_out

        if not (data.players[data.players[user].targets[0]].currently_alive or data.players[data.players[user].targets[0]].was_voted_out):
            data.players[user].unemployed = True
            data.players[user].solo_win = data.players[user].currently_alive

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        self.ability(user, data)

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        pass
        # data.players[user].unemployed = False
        # data.players[user].solo_win = data.players[data.players[user].targets[0]].was_voted_out

        # if not (data.players[data.players[user].targets[0]].currently_alive or data.players[data.players[user].targets[0]].was_voted_out):
        #     data.players[user].unemployed = True
        #     data.players[user].solo_win = data.players[user].was_voted_out

        #     if data.settings["Early End"] == 1 and data.players[user].solo_win:
        #         data.playing = False

class execute(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 1, p = 5, ability_type = ["singular", "on_vote"])
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        data.players[user].unemployed = False
        data.players[user].solo_win = data.players[data.players[user].targets[0]].was_voted_out

        if not (data.players[data.players[user].targets[0]].currently_alive or data.players[data.players[user].targets[0]].was_voted_out):
            data.players[user].unemployed = True
            data.players[user].solo_win = data.players[user].currently_alive

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        self.ability(user, data)

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        pass
        # data.players[user].unemployed = False
        # data.players[user].solo_win = not data.players[data.players[user].targets[0]].was_voted_out

        # if not (data.players[data.players[user].targets[0]].currently_alive or data.players[data.players[user].targets[0]].was_voted_out):
        #     data.players[user].unemployed = True
        #     data.players[user].solo_win = data.players[user].was_voted_out

        #     if data.settings["Early End"] == 1 and data.players[user].solo_win:
        #         data.playing = False

class poison(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 1, p = 2.5, ability_type = ["repeat"], priority = 0)
    
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
        super().__init__(targets = 1, p = 2.5, ability_type = ["repeat"], priority = 5, can_pick_same_target = True)
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        target: str = data.players[user].targets[0]
        data.players[target].die(data.players)

        if data.players[user].secondary_ability == mayor:
            data.players[user].secondary_ability(user, data)

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        if data.players[user].secondary_ability == mayor:
            data.players[user].secondary_ability(user, data)

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        pass

class telepathy(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 1, p = 2.5, ability_type = ["repeat"], priority = 4, can_pick_same_target = True)
        self.examine: Ability = examine()

    # -- Methods -- #
    def show_info(self, user: str, data: Game_Data, user_role: Role, target: str, role: Role, is_lover: bool) -> None:
        user_role.information.append(f"{target} is {role.name}, which is {data.get_card_by_role(role)}!")
        self.examine(user, data)

        if user_role.name == "Psychic":
            mafia_roles: dict[str, Role] = {name: role for name, role in data.evil_aligned.items() if role.name != "Psychic"}

            for name, evil_role in mafia_roles.items():
                evil_role.information.append(f"{target} is {role.name}, which is {data.get_card_by_role(role)}!")
                self.examine(name, data)
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        target: str = data.players[user].targets[0]
        user_role = data.players[user]

        role: Role = data.players[target]
        is_lover: bool = role.linked
        
        self.show_info(data, user_role, target, role, is_lover)

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        target: str = data.players[user].targets[0]
        user_role = data.players[user]

        if user_role.name == "Psychic":
            roles = [role for role in data.roles.values() if role.alignment]
        else:
            roles = list(data.roles.values())

        role: Role = choice(roles)
        is_lover: bool = False

        self.show_info(data, user_role, target, role, is_lover)

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        pass

class stalk(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 1, p = 5, ability_type = ["repeat"], can_pick_same_target = True)

    # -- Methods -- #
    @enforce_types
    def information(self, data: Game_Data, user: str, target: str, visitors: list[str]) -> None:
        target_str: str = f"{target} was visited by "
        count: int = 0

        # -- Filtering For " " and Self Cases -- #
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
    def if_poisoned(self, user: str, data: Game_Data, can_include_self: bool = True) -> None:
        target: str = data.players[user].targets[0]

        random_num: int = randint(0, len(data.players))
        selected_players = set([]) 

        for i in range(random_num): selected_players.add(choice(list(data.players.keys())))

        if not can_include_self:
            try:
                selected_players.remove(user)
            except:
                pass

        visitors = list(selected_players)

        self.information(data, user, target, visitors)

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        target: str = data.players[user].targets[0]
        self.ability(user, data, target)

class resurrect(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 1, p = 5, ability_type = ["singular", "on_demand"], target_living = False)  
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data, evil: bool = False) -> None:
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

            if evil and target.true_alignment == True:
                target._alignment = False
                target.mafia_alternative = True
                target.information.append("You Are Now Evil!")

                for role in data.evil_aligned.values():
                    role.information.append(f"{user_role.targets[0]} has been resurrected! They are now evil!")

        elif ability_cancel:
           user_role.used_ability = False

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        self.ability(user, data, True)

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        pass

class vengance(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 1, p = 7.5, ability_type = ["on_death"], can_pick_same_target = True)
    
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
        super().__init__(targets = 1, p = 2.5, ability_type = ["repeat", "on_demand"], priority = 4, can_pick_same_target = True)
        
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
            data.players[player].information.append(f"{user} attempted to ambush {new_target}!")

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        self.ability(user, data, False)

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        pass

class mayor(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 0, p = 0, ability_type = ["passive", "game_end"], priority = 10)
    
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
        super().__init__(targets = 0, p = 0, ability_type = ["alternate", "secondary_ability", "passive", "game_start"], priority = 8)
        self.used_abilities: set[str] = set([])
        self.non_starting_abilities: set[str] = set([])
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data, early_start: bool = False) -> None:
        if early_start:
            self.non_starting_abilities: set[str] = {role.ability.true_name for role in data.roles.values()} - {role.ability.true_name for role in data.roles.values() if role.true_alignment == True}
            self.non_starting_abilities = self.non_starting_abilities.union({"none", "vote", "instant_death"})
            role_data: list[str, Ability] = data.random_ability(self.non_starting_abilities)
            
            self.used_abilities.add(role_data[0])
            data.players[user].secondary_ability = role_data[1]

            if data.settings["Instant Death"] == 0:
                self.used_abilities.add("instant_death")
        else:
            role: Role = data.players[user]
            
            if role.ability_cancel:
                role.secondary_ability(user, data)

            else:
                role_data: list[str, Ability] = data.random_ability(self.used_abilities)
                role.secondary_ability = role_data[1]
                role.secondary_ability.used_ability = False
                self.used_ability = False

                if role.secondary_ability == instant_death:
                    role.information.append(f"They rolled {role.secondary_ability.__name__}!")
                else:
                    new_role: Role = data.get_role_by_ability(role.secondary_ability)
                    new_card: str = data.get_card_by_role(new_role)

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
        super().__init__(targets = 1, p = 2.5, ability_type = ["late"])
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        data.players[user].die(data.players)

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        pass

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        pass

class magnet(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(targets = 2, p = 2.5, ability_type = ["repeat"], priority = 1)
        
    # -- Extra Methods -- #
    @enforce_types
    def poison_consideration(self, role: Role, target: Role) -> None:
        if isinstance(role.ability, poison):
            target.targets[0].poisioned = False # -- If We do Drunk, Change This -- #
            role.poisoned = True

    @enforce_types
    def magnetise(self, data: Game_Data, second_target: str, role: Role, targets: list[str]) -> None:
        for target in targets:
            target_role = data.players[target]

            if target_role.ability.target_living:
                if role.ability.targets == 1:
                    target_role.targets = [second_target]
                elif role.ability.targets == 2:
                    target_role.targets = [second_target, target]

    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        role: Role = data.players[user]
        targets = []

        targets.append(role.targets[0])
        target: Role = data.players[targets[0]]
        self.poison_consideration(role, target)
                        
        self.magnetise(data, role.targets[1], role, targets)

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
        super().__init__(targets = 0, p = 5, ability_type = ["passive"], priority = 11)
        self.seen_roles: set[str] = set(["Doctor", "Mafia", "Sheriff"])

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
        
            card = data.get_card_by_role(data.roles[selected_role])
            user_role.information.append(f"{selected_role} is in the game with card {card}!")

    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        normal_roles: set[str] = set([role.name for role in data.players.values()])

        user_role: Role = data.players[user]
        self.seen_roles.add(user_role.name)

        selected_set: set[str] = normal_roles - self.seen_roles

        self.information(data, user_role, selected_set)

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
        super().__init__(targets = 1, p = 7.5, ability_type = ["repeat"], priority = 11, can_pick_same_target = True)

    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        target: str = data.players[user].targets[0]
        role: Role = data.players[target]

        for item in role.statuses.get_data(target):
            data.players[user].information.append(item)

    @enforce_types
    def if_poisoned(self, user: str, data: Game_Data) -> None:
        target: str = data.players[user].targets[0]
        role: Role = data.players[target]

        for item in role.statuses.get_data(target):
            data.players[user].information.append(not item)

    @enforce_types
    def if_drunk(self, user: str, data: Game_Data) -> None:
        target: str = data.players[user].targets[0]
        role: Role = data.players[target]

        for item in role.statuses.bullshit_data(target):
            data.players[user].information.append(item)