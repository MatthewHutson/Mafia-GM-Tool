# -- Imports -- #
from utils import *
from classes_and_types import Role, Game_Data, Ability
from game_loop_functions import *
from time import sleep
from re import fullmatch

# -- Roles -- #
class none(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(0, 25, ["passive"], True)
    
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

        if alignment: data.players[user].information.append(f"{target} is GOOD!")
        else: data.players[user].information.append(f"{target} is EVIL!")

class endure(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(0, 10, ["passive"], True, 2)
    
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
        if data.players[user].was_voted_out: 
            data.players[user].solo_win = True

class stop_vote(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(1, 5, ["singular", "on_vote"], True)
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        if not data.players[user].solo_win:
            data.players[user].solo_win = True
            if data.players[data.players[user].targets[0]].was_voted_out:
                data.players[user].solo_win = False

            if not data.players[data.players[user].targets[0]].currently_alive and data.players[user].solo_win:
                role_switch(data, user, Role("Villager", none, True, False, 999, 999, "passive", [], [], []))

class execute(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(1, 5, ["singular", "on_vote"], True)
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        if not data.players[user].solo_win:
            if data.players[data.players[user].targets[0]].was_voted_out:
                data.players[user].solo_win = True

            if not (data.players[data.players[user].targets[0]].currently_alive or data.players[user].solo_win):
                role_switch(data, user, Role("Villager", none, True, False, 999, 999, "passive", [], [], []))

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
        if not data.players[user].poisoned:
            target: str = data.players[user].targets[0]
            role: Role = data.players[target]
            is_lover: bool = role.linked

            data.players[user].information.append(f"{target} is {role.name}!")
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

        print(visitors)
            
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
            selection_menu(data, user)

            target = data.players[user].targets[0]
            role = data.players[target]
            role.protected = False
            role.die(data.players)

        data.players[user].ability.targets = 0

class resurrect(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(1, 5, ["singular", "on_demand"], False, 1)  
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        if len(data.players[user].targets) > 0 and not data.players[user].poisoned and not data.players[user].ability_cancel:
            target = data.players[data.players[user].targets[0]]
            target.revive()

        elif data.players[user].ability_cancel:
            data.players[user].used_ability = False

class ambush(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(1, 5, ["repeat"], True, 4)
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        if not data.players[user].poisoned:
            target = data.players[user].targets[0]
            visitors = deepcopy(data.players[target].visited_by)

            try:
                visitors.remove(user)
            except:
                pass

            try:
                new_target = visitors[0]
                bystanders = deepcopy(visitors)

                bystanders.remove(new_target)

                data.players[user].targets = [new_target]
                kill()(user, data)
            except:
                pass

            try:
                bystanders.remove(user)
            except:
                pass

            for player in bystanders:
                data.players[player].information.append(f"{user} attempted to ambush {new_target}!")


class mayor(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(0, 5, ["passive", "game_end"], True, 10)
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        if data.playing:
            if not data.players[user].solo_win:
                sleep(1)
                if messagebox.askyesno("Mayor", "Has The Mayor Revealed Themselves?"):
                    data.players[user].solo_win = True
        else:
            data.players[user].solo_win = len(data.players) == data.players[user].alternative_end_count

class gamble(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(0, 0, ["on_demand", "secondary_ability"], True, 8)
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        role: Role = data.players[user]
        if role.ability_cancel:
            role.secondary_ability(user, data)

        else:
            role.secondary_ability = data.random_ability
            role.information.append(f"Show {user} that they got {role.secondary_ability.__name__}")
            role.ability.priority = role.secondary_ability.priority

            if "instant" in role.secondary_ability.ability_type:
                role.secondary_ability(user, data)

class instant_death(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(1, 5, ["instant"], True)
        
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        if not data.players[user].poisoned:
            data.players[user].die()
