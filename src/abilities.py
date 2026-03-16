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
        super().__init__(0, 20, ["passive"], True)
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        pass

class vote(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(1, 0, ["repeat"], True)
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        pass

class reveal(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(1, 5, ["repeat"], True, 9)
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        target: str = data.players[user].targets[0]
        alignment: bool = data.players[user].poisoned ^ data.players[target].alignment

        if alignment: data.players[user].information.append(f"Their target is GOOD!")
        else: data.players[user].information.append(f"Their target is EVIL!")

class endure(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(0, 5, ["passive"], True, 2)
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        if not data.players[user].poisoned:
            data.players[user].protected = True

class protect(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(1, 5, ["repeat"], True, 3)
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        target: str = data.players[user].targets[0]
        if not data.players[user].poisoned: 
            data.players[target].protected = True

class link(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(2, 0, ["singular"], True, 4)
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        link_1: str = data.players[user].targets[0]
        link_2: str = data.players[user].targets[1]
        
        data.players[link_1].linked = True
        data.players[link_2].linked = True

        data.players[link_1].linker = user
        data.players[link_2].linker = user

        data.players[link_1].linked_to = link_2
        data.players[link_2].linked_to = link_1

class jester(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(0, 5, ["on_death"], True)
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        data.players[user].solo_win = data.players[user].was_voted_out

class stop_vote(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(1, 5, ["singular", "on_vote"], True)
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        data.players[user].solo_win = not data.players[data.players[user].targets[0]].was_voted_out

        if not (data.players[data.players[user].targets[0]].currently_alive or data.players[data.players[user].targets[0]].was_voted_out):
            data.players[user].solo_win = data.players[user].currently_alive

class execute(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(1, 5, ["singular", "on_vote"], True)
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        data.players[user].solo_win = data.players[data.players[user].targets[0]].was_voted_out

        if not (data.players[data.players[user].targets[0]].currently_alive or data.players[data.players[user].targets[0]].was_voted_out):
            data.players[user].solo_win = data.players[user].currently_alive

class poison(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(1, 5, ["repeat"], True, 0)
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        if not data.players[user].poisoned:
            target: str = data.players[user].targets[0]
            data.players[target].poisoned = True

            if data.players[target].ability == self:
                # -- Prevents Unfair Poison Clashes -- #
                targets_target: str = data.players[target].targets[0]
                data.players[targets_target].poisoned = False

class kill(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(1, 5, ["repeat"], True, 5)
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        if not data.players[user].poisoned:
            target: str = data.players[user].targets[0]
            data.players[target].die(data.players)

class telepathy(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(1, 5, ["repeat"], True, 4)
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        target: str = data.players[user].targets[0]

        if not data.players[user].poisoned:
            role: Role = data.players[target]
            is_lover: bool = role.linked
        else:
            role: Role = choice(data.roles)
            is_lover: bool = True
        
        data.players[user].information.append(f"{target} is {role.name}, which is {data.get_card_by_role(role)}!")

        if is_lover:
            data.players[user].information.append(f"{target} is linked to another player!")

class stalk(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(1, 5, ["repeat"], True)
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        visitors = []

        if not data.players[user].poisoned:
            target: str = data.players[user].targets[0]
            visitors = data.players[target].visited_by
        else:
            visitors = []

        target_str = f"{target} was visited by "
        count = 0

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

class vengance(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(0, 5, ["on_death"], True)
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        if not data.players[user].was_voted_out:
            data.players[user].ability.targets = 1
            selection_menu(data, data.menu_entries, user)

            target = data.players[user].targets[0]
            role = data.players[target]
            role.protected = False
            role.die(data.players)

        data.players[user].ability.targets = 0

class resurrect(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(1, 5, ["singular", "on_demand"], False, )  
    
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

            if (user_role.poisoned or not user_role.alignment) and target.true_alignment == True:
                target._alignment = False
                target.mafia_alternative = True
                target.information.append("You Are Now Evil!")

                for role in data.evil_aligned.values():
                    role.information.append(f"{user_role.targets[0]} has been resurrected! They are now evil!")

        elif ability_cancel:
           user_role.used_ability = False

class ambush(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(1, 5, ["repeat"], True, 4)
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        target = data.players[user].targets[0]
        visitors = deepcopy(data.players[target].visited_by)

        try:
            visitors.remove(user)
        except:
            pass

        if not data.players[user].poisoned:
            try:
                new_target = visitors[0]
                visitors = visitors[1:]

                data.players[user].targets = [new_target]
                kill()(user, data)
            except:
                pass

        for player in visitors:
            data.players[player].information.append(f"{user} attempted to ambush {new_target}!")


class mayor(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(0, 0, ["passive", "game_end"], True, 10)
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        if data.playing:
            if not data.players[user].solo_win:
                sleep(0.5)
                if messagebox.askyesno("Mayor", "Has The Mayor Revealed Themselves?"):
                    data.players[user].solo_win = True
        else:
            data.players[user].solo_win = len(data.players) == data.players[user].alternative_end_count

class gamble(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(0, 0, ["alternate", "secondary_ability", "passive"], True, 8)
        self.used_abilities: list[Role] = []
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        role: Role = data.players[user]
        if role.ability_cancel:
            role.secondary_ability(user, data)

            if role.secondary_ability != none or role.secondary_ability:
                self.used_abilities.append(role.secondary_ability)

        else:
            role.secondary_ability = data.random_ability(self.used_abilities)
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

class instant_death(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(1, 5, ["late"], True)
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        if not data.players[user].poisoned:
            data.players[user].die(data.players)

class magnet(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(1, 5, ["repeat"], True, 1)
        
    # -- Extra Methods -- #
    @enforce_types
    def poison_consideration(self, role: Role, target: Role) -> None:
        if isinstance(role.ability, poison):
            target.targets[0].poisioned = False # -- If We do Drunk, Change This -- #
            role.poisoned = True

    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        role: Role = data.players[user]
        targets = []

        if not role.poisoned:
            targets.append(role.targets[0])
            target: Role = data.players[targets[0]]
            self.poison_consideration(role, target)

        if role.poisoned:
            targets = []
            for target_role in data.alive_players.values():
                if role.ability.target_living and target_role.ability != self:
                    targets.append(target_role.name)
                    self.poison_consideration(role, target)
                        
        for target in targets:
            target_role = data.players[target]

            if target_role.ability.target_living:
                if role.ability.targets == 1:
                    target_role.targets = [user]
                elif role.ability.targets == 2:
                    target_role.targets = [user, target]

class index(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(0, 5, ["passive"], True, 11)
        self.seen_roles: set[str] = set([])

    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        all_roles: set[str] = set(data.roles.keys())
        normal_roles: set[str] = set([role.name for role in data.players.values()])

        user_role: Role = data.players[user]
        self.seen_roles.add(user_role.name)

        if user_role.poisoned:
            selected_set: set[str] = all_roles - normal_roles - self.seen_roles
        else:
            selected_set: set[str] = normal_roles - self.seen_roles

        selected_role: str = choice(list(selected_set))

        self.seen_roles.add(selected_role)
    
        card = data.get_card_by_role(data.roles[selected_role])
        user_role.information.append(f"{selected_role} is in the game with card {card}!")
        