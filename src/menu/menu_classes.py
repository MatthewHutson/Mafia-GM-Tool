# -- Imports -- #
from utils import *
from typing import Protocol
from classes_and_types import *
from random import randint, shuffle
import tkinter as tk
from tkinter import messagebox

# -- Classes -- #
class Role_Icon:
    # -- Constructors -- #
    @enforce_types
    def __init__(self, roles: list[str], main_font: tuple[str, int], entries: Menu_Entry, size: tuple[int] = (16, 4), padding: tuple[int] = (2, 0), command: Any = None) -> None:
        self.roles = [entries.role_dict[role] for role in roles]
        self.role_names = roles
        self.index = 0
        self.font = main_font
        self.entries = entries
        self.size = size
        self.padding = padding
        self.label = None
        self.frame = None
        self.frames = None

        if command == None: self.command = self.cycle
        else: self.command = command

    @enforce_types
    def re_init(self, roles: list[str]) -> None:
        self.roles = [self.entries.role_dict[role] for role in roles]
        self.index = len(self.roles) - 1
        try:
            self.command()
        except:
            pass

    # -- Property -- #
    @property
    def role(self) -> Role:
        return self.roles[self.index]

    @property
    def name(self) -> str:
        return self.role.name
    
    @property
    def alignment(self) -> bool:
        return self.role.true_alignment
    
    @property
    def bg_colour(self) -> str:
        if self.alignment == None:
            return  "#f5f5f5"
        elif self.alignment:
            return "#48f748"
        else:
            return "#c72e2e"

    @property
    def fg_colour(self) -> str:
        if self.alignment == False:
            return "#ffffff"
        else:
            return "#000000"

    # -- Methods -- #
    @enforce_types
    def __eq__(self, value: str) -> bool:
        return self.name == value
    
    @enforce_types
    def __str__(self) -> str:
        return self.name
        
    @enforce_types
    def pack(self, frame: tk.Frame = None, frames: list[object] = None) -> None:
        if self.frame == None:
            self.frame = frame
        
        if self.frames == None:
            self.frames = frames
        
        self.label = tk.Button(self.frame, text = self.name, font = self.font, bg = self.bg_colour, highlightbackground = self.bg_colour, activebackground = self.bg_colour, fg = self.fg_colour, activeforeground = self.fg_colour, width = self.size[0], height = self.size[1], command = self.command)
        self.label.pack(padx = self.padding[0], pady = self.padding[1], side = tk.LEFT, expand = False)

    @enforce_types
    def delete(self) -> None:
        self.forget()
        del self

    @enforce_types
    def forget(self) -> None:
        if self.label != None:
            self.label.pack_forget()

    @enforce_types
    def cycle(self) -> None:
        self.index += 1
        self.index = self.index % len(self.roles)

        for frame in self.frames:
            frame.forget()

        for frame in self.frames:
            frame.pack(self.frame, self.frames)

    @enforce_types
    def shuffle(self) -> None:
        count = randint(0, len(self.roles))

        for i in range(count):
            self.cycle()

    @enforce_types
    def deepcopy(self) -> object:
        new_icon = Role_Icon(self.role_names, self.font, self.entries)
        return new_icon

class Role_Row:
    # -- Constructor -- #
    @enforce_types
    def __init__(self, frame: tk.Frame) -> None:
        self.frames: list[tk.Frame] = []
        self.icons: list[list[Role_Icon]] = []
        self.master_frame = frame
        self.max_row_length = 6

    # -- Property -- #
    @property
    def icon_list(self) -> list[Role_Icon]:
        icons = []
        for icon_set in self.icons:
            icons.extend(icon_set)
        return icons
    
    @property
    def icon_single(self) -> list[Role_Icon]:
        output: list[Role_Icon] = []
        for row in self.icons:
            output += row

        return output

    # -- Methods -- #
    @enforce_types
    def get_role_reset_function(self, role_boundary_reset: Any) -> None:
        self.role_boundary_reset: Callable = role_boundary_reset

    @enforce_types
    def add_row(self) -> None:
        self.frames.append(tk.Frame(self.master_frame, bg = "#d3d3d3"))
        self.icons.append([])

    @enforce_types
    def remove_end_row(self) -> None:
        self.disapear()
        del self.frames[-1]
        del self.icons[-1]
        self.pack()

    @enforce_types
    def add_item(self, icon: Role_Icon) -> None:
        if len(self.icons) == 0:
            self.add_row()

        if len(self.icons[-1]) >= self.max_row_length:
            self.add_row()

        self.icons[-1].append(icon)
        self.pack()

            
    @enforce_types
    def remove_item(self, row: int, index: int, reset: bool = True, delete: bool = True) -> None:
        icon = self.icons[row][index]
        del self.icons[row][index]

        if delete:
            icon.delete()

        if reset:
            self.role_boundary_reset()

    @enforce_types
    def remove_end_item(self, reset: bool = False, delete: bool = True) -> None:
        if len(self.icons[-1]) == 0:
            self.remove_end_row()

        self.remove_item(-1, -1, reset, delete)

        if len(self.icons[-1]) == 0:
            self.remove_end_row()

    @enforce_types
    def disapear(self) -> None:
        for icons in self.icons:
            for icon in icons:
                icon.forget()

        for frame in self.frames:
            frame.pack_forget()
 
    @enforce_types
    def pack(self) -> None:
        self.disapear()
        for i in range(len(self.frames)):
            for icon in self.icons[i]:
                icon.pack(self.frames[i], self.icons[i])

        for frame in self.frames:
            frame.pack(side = tk.TOP, padx = 2, fill = "x", pady = 2)

    @enforce_types
    def delete(self) -> None:
        self.disapear()
        del self

    @enforce_types
    def shuffle(self) -> None:
        roles = [icon.roles for icon in self.icon_single]
        shuffle(roles)
        count = 0
        
        for i in range(len(self.icons)):
            for j in range(len(self.icons[i])):
                self.icons[i][j].roles = roles[count]
                role_names = [role.name for role in roles[count]]
                self.icons[i][j].role_names = role_names
                self.icons[i][j].index = 0
                self.icons[i][j].shuffle()
                count += 1
        
class Player_Frame:
    # -- Constructor -- #
    def __init__(self, user_input: str, main_frame: tk.Frame, main_font: tuple[str, int]) -> None:
        self.frame = tk.Frame(main_frame)
        self.name_label = tk.Label(self.frame, text = capitalise_words(user_input), font = main_font).pack(side = tk.LEFT, fill = "x", padx = 4)
        self.frame.pack_propagate(False)
        self.name: str = capitalise_words(user_input)

    # -- Methods -- #
    @enforce_types
    def __eq__(self, value) -> bool:
        return self.name == str(value)
    
    @enforce_types
    def __str__(self) -> str:
        return self.name
        
    @enforce_types
    def pack(self) -> None:
        self.frame.pack(anchor = "n", side = tk.TOP, padx = 4, fill = "x", ipady = 16, pady = 2)

class Player_Select_Frame(Player_Frame):
    # -- Constructor -- #
    @enforce_types
    def __init__(self, user_input: str, main_frame: tk.Frame, main_font: tuple[str, int], players: list[object], icon_frame: Role_Row) -> None:
        super().__init__(user_input, main_frame, main_font)
        self.players = players
        self.icon_frame = icon_frame
        self.delete_button = tk.Button(self.frame, text = "Remove", fg = "#ffffff", bg = "#ff0000", highlightbackground = "#cd0000", activebackground = "#aa0000", font = main_font, command = self.delete).pack(side = tk.RIGHT)
        self.pack()

    # -- Methods -- #
    @enforce_types
    def delete(self) -> None:
        self.frame.pack_forget()
        self.players.remove(self)
        self.icon_frame.remove_end_item()
        del self

class Player_Role_Frame(Player_Frame):
    # -- Constructor -- #
    @enforce_types
    def __init__(self, name: str, data: Game_Data, main_frame: tk.Frame, main_font: tuple[str, int], selected_players: list[str], selected_role: Role) -> None:
        super().__init__(name, main_frame, main_font)
        self.data = data
        self.alignment = self.role.true_alignment
        self.selected_players = selected_players
        self.number_of_targets = selected_role.ability.targets
        self.selected_role_name = selected_role.name
        self.selected = False
        self.current_role_icon = None

        # -- Role Colours -- #
        self.role_fg = "#000000"
        
        if self.alignment == None:
            self.role_bg = "#f5f5f5"
        elif self.alignment:
            self.role_bg = "#48f748"
        else:
            self.role_bg = "#c72e2e"
            self.role_fg = "#ffffff"

        # -- Linked Icons -- #
        self.linked_bg = "#ddb3dd"
        self.linked_fg = "#000000"

        if self.role.linked:
            self.linked_bg = "#f94af9"
            self.linked_fg = "#ffffff"

        # -- Solo Win Icons -- #
        if self.role.solo_win:
            self.solo_win_bg = "#48f748"
        else:
            self.solo_win_bg = "#d1d1d1"

        # -- Extra Icons -- #
        self.linked_icon = tk.Button(self.frame, text = "", bg = self.linked_bg, activebackground = self.linked_bg, fg = self.linked_fg, activeforeground = self.linked_fg, width = 2, height = 2)
        self.solo_win_icon = tk.Button(self.frame, text = "", bg = self.solo_win_bg, activebackground = self.solo_win_bg, fg = "#000000", activeforeground = "#000000", width = 2, height = 2)
        self.select_icon = tk.Button(self.frame, text = "Select", bg = "#5D9FF0", activebackground = "#4980C4", fg = "#FFFFFF", activeforeground = "#FFFFFF", width = 6, height = 4, command = self.select)

        self.pack()

    # -- Propterties -- #
    @property
    def selected_bg(self) -> str:
        if self.selected:
            return "#0065E1"
        else:
            return "#5D9FF0"
        
    @property
    def role_icon(self) -> tk.Button:
        self.current_role_icon = tk.Button(self.frame, text = self.role.name, bg = self.role_bg, activebackground = self.role_bg, fg = self.role_fg, activeforeground = self.role_fg, width = 10, height = 4)
        return self.current_role_icon

    @property
    def role(self) -> Role:
        return self.data.players[self.name]

    # -- Methods -- #
    @enforce_types
    def delete(self) -> None:
        self.frame.pack_forget()
        del self

    @enforce_types
    def pack(self) -> None:
        self.role_icon.pack(side = tk.RIGHT, padx = 2, expand = False)
        self.select_icon.pack(side = tk.RIGHT, padx = 2, expand = False)
        self.linked_icon.pack(side = tk.RIGHT, padx = 2, pady = 4, expand = False)
        self.solo_win_icon.pack(side = tk.RIGHT, padx = 2, pady = 4, expand = False)
        super().pack()

    @enforce_types
    def forget(self) -> None:
        self.current_role_icon.pack_forget()
        self.select_icon.pack_forget()
        self.linked_icon.pack_forget()
        self.solo_win_icon.pack_forget()

    @enforce_types
    def select(self) -> None:
        if len(self.selected_players) < self.number_of_targets and not self.selected:
            self.selected_players.append(self.name)
            self.selected = not self.selected

        elif self.selected:
            self.selected_players.remove(self.name)
            self.selected = not self.selected

        elif len(self.selected_players) >= self.number_of_targets:
            messagebox.showwarning("Warning", f"{self.selected_role_name} can only select {self.number_of_targets} target{"s" if self.number_of_targets > 1 else ""}!")
        
        self.forget()
        self.select_icon = tk.Button(self.frame, text = "Select", bg = self.selected_bg, activebackground = "#4980C4", fg = "#FFFFFF", activeforeground = "#FFFFFF", width = 6, height = 4, command = self.select)
        self.pack()

# -- Protocols -- #
class Has_Widget_Children(Protocol):
    def winfo_children():
        ...