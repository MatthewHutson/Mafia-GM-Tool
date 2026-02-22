# -- Imports -- #
from utils import *
from classes_and_types import Role, Game_Data
from game_loop_functions import *
from time import sleep

# -- Base Class -- #
class Ability():
    @enforce_types
    def __init__(self, targets: int, p: Union[int, float], ability_type: list[str], target_living: bool) -> None:
        self.targets = targets
        self.p = p
        self.ability_type = ability_type
        self.target_living = target_living
    
    @property
    @enforce_types
    def __name__(self) -> str:
        return capitalise_words(type(self).__name__, "_")

    # -- Methods -- #
    def ability(self, user: str, data: Game_Data) -> None:
        ...

    @enforce_types
    def __call__(self, user: str, data: Game_Data) -> None:
        self.ability(user, data)

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
        super().__init__(1, 5, ["repeat"], True)
    
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
        super().__init__(0, 10, ["passive"], True)
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        if not data.players[user].poisoned: 
            data.players[user].protected = True

class protect(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(1, 5, ["repeat"], True)
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        target: str = data.players[user].targets[0]
        if not data.players[user].poisoned: 
            data.players[target].protected = True

class link(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(2, 0, ["singular"], True)
        
    
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
        super().__init__(1, 5, ["repeat"], True)
        
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        if not data.players[user].poisoned:
            target: str = data.players[user].targets[0]
            data.players[target].poisoned = True

class kill(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(1, 5, ["repeat"], True)
        
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        if not data.players[user].poisoned:
            target: str = data.players[user].targets[0]
            data.players[target].die(data.players)

class telepathy(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(1, 5, ["repeat"], True)
        
    
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

        target_str = f"{target} was visited by "
            
        for player in visitors:
            if player != user:
                target_str += player + ", "

        if len(visitors) > 0:
            target_str = target_str[:-2]
        else:
            target_str += " nobody"

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
        super().__init__(1, 5, ["singular", "on_demand"], False)
        
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        if len(data.players[user].targets) > 0 and not data.players[user].poisoned:
            target = data.players[data.players[user].targets[0]]
            target.revive()

class ambush(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(1, 5, ["repeat"], True)
        
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        if not data.players[user].poisoned:
            target = data.players[user].targets[0]
            try:
                new_target = data.players[target].visited_by[0]
                bystanders = deepcopy(data.players[target].visited_by[1:])

                bystanders.remove(user)

                data.players[user].targets = [new_target]
                kill(user, data)

                for player in bystanders:
                    data.players[player].information.append(f"{user} attempted to ambush {new_target}!")
            except:
                pass

class mayor(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(0, 5, ["passive", "game_end"], True)
        
    
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
        super().__init__(0, 0, ["on_demand", "secondary_ability"], True)
        
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        user: Role = data.players[user]
        if user.ability_cancel:
            user.secondary_ability(user, data)

        else:
            user.secondary_ability = data.random_ability

            if "instant" in user.secondary_ability.ability_type:
                user.secondary_ability(user, data)

class instant_death(Ability):
    @enforce_types
    def __init__(self) -> None:
        super().__init__(1, 5, ["instant"], True)
        
    
    # -- Ability -- #
    @enforce_types
    def ability(self, user: str, data: Game_Data) -> None:
        if not data.players[user].poisoned:
            data.players[user].die()
