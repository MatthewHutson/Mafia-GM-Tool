# -- Imports -- #
from utils import *
from classes_and_types import *
import tkinter as tk
from tkinter import messagebox

# -- Classes -- #
class Role_Icon:
    # -- Constructor -- #
    @enforce_types
    def __init__(self, roles: list[str], main_font: tuple[str, int], entries: Menu_Entry) -> None:
        self.roles = [entries.role_dict[role] for role in roles]
        self.index = 0
        self.bg_colour = "#000000"
        self.fg_colour = "#000000"
        self.font = main_font
        self.label = None
        self.frame = None
        self.frames = None

        if self.alignment == None:
            self.bg_colour = "#f5f5f5"
        elif self.alignment:
            self.bg_colour = "#48f748"
        else:
            self.bg_colour = "#c72e2e"
            self.fg_colour = "#ffffff"

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

    # -- Methods -- #
    @enforce_types
    def __eq__(self, value: str) -> bool:
        return self.name == value
    
    @enforce_types
    def __str__(self) -> str:
        return self.name
        
    @enforce_types
    def pack(self, frame: tk.Frame, frames: list[object]) -> None:
        self.label = tk.Button(frame, text = self.name, font = self.font, bg = self.bg_colour, highlightbackground = self.bg_colour, activebackground = self.bg_colour, fg = self.fg_colour, activeforeground = self.fg_colour, width = 16, height = 4, command = self.cycle)
        self.frame = frame
        self.frames = frames
        self.label.pack(padx = 2, pady = 0, side = tk.LEFT, expand = False)

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

class Role_Row:
    # -- Constructor -- #
    @enforce_types
    def __init__(self, frame: tk.Frame) -> None:
        self.frames: list[tk.Frame] = []
        self.icons: list[list[Role_Icon]] = []
        self.master_frame = frame
        self.max_row_length = 5

    # -- Property -- #
    @property
    def icon_list(self) -> list[Role_Icon]:
        icons = []
        for icon_set in self.icons:
            icons.extend(icon_set)
        return icons

    # -- Methods -- #
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
    def remove_item(self, row: int, index: int) -> None:
        icon = self.icons[row][index]
        del self.icons[row][index]
        icon.delete()

    @enforce_types
    def remove_end_item(self) -> None:
        if len(self.icons[-1]) == 0:
            self.remove_end_row()

        self.remove_item(-1, -1)

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
        self.icon_frame.remove_end_item()
        self.players.remove(self)
        del self

class Player_Role_Frame(Player_Frame):
    # -- Constructor -- #
    @enforce_types
    def __init__(self, name: str, role: Role, main_frame: tk.Frame, main_font: tuple[str, int], selected_players: list[str], selected_role: Role) -> None:
        super().__init__(name, main_frame, main_font)
        self.role = role
        self.alignment = role.true_alignment
        self.selected_players = selected_players
        self.number_of_targets = selected_role.ability.targets
        self.selected_role_name = selected_role.name
        self.selected = False

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
        self.linked_bg = "#d1d1d1"
        self.linked_text = "Single"

        if self.role.linked:
            self.linked_bg = "#cf6bf7"
            self.linked_text = "Linked"

        # -- Extra Icons -- #
        self.role_icon = tk.Button(self.frame, text = role.name, bg = self.role_bg, activebackground = self.role_bg, fg = self.role_fg, activeforeground = self.role_fg, width = 6, height = 4)
        self.linked_icon = tk.Button(self.frame, text = self.linked_text, bg = self.linked_bg, activebackground = self.linked_bg, fg = "#000000", activeforeground = "#000000", width = 6, height = 4)
        self.select_icon = tk.Button(self.frame, text = "Select", bg = "#5D9FF0", activebackground = "#4980C4", fg = "#FFFFFF", activeforeground = "#FFFFFF", width = 6, height = 4, command = self.select)

        self.pack()

    # -- Propterties -- #
    @property
    def selected_bg(self) -> str:
        if self.selected:
            return "#0065E1"
        else:
            return "#5D9FF0"

    # -- Methods -- #
    @enforce_types
    def delete(self) -> None:
        self.frame.pack_forget()
        del self

    @enforce_types
    def pack(self) -> None:
        self.role_icon.pack(side = tk.RIGHT, padx = 2, expand = False)
        self.linked_icon.pack(side = tk.RIGHT, padx = 2, expand = False)
        self.select_icon.pack(side = tk.RIGHT, padx = 2, expand = False)
        super().pack()

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
        
        self.select_icon.pack_forget()
        self.select_icon = tk.Button(self.frame, text = "Select", bg = self.selected_bg, activebackground = "#4980C4", fg = "#FFFFFF", activeforeground = "#FFFFFF", width = 6, height = 4, command = self.select)
        self.select_icon.pack(side = tk.RIGHT, padx = 2, expand = False)