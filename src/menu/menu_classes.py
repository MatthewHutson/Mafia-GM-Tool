# -- Imports -- #
from utils import *
from classes_and_types import *
import tkinter as tk
from tkinter import messagebox
from copy import deepcopy

# -- Classes -- #
class Role_Icon:
    # -- Constructor -- #
    @enforce_types
    def __init__(self, role: Role, main_font: tuple[str, int]) -> None:
        self.name = role.name
        self.alignment = role.true_alignment
        self.bg_colour = "#000000"
        self.fg_colour = "#000000"
        self.font = main_font
        self.label = None

        if self.alignment == None:
            self.bg_colour = "#f5f5f5"
        elif self.alignment:
            self.bg_colour = "#48f748"
        else:
            self.bg_colour = "#c72e2e"
            self.fg_colour = "#ffffff"

    # -- Methods -- #
    @enforce_types
    def __eq__(self, value: str) -> bool:
        return self.name == value
    
    @enforce_types
    def __str__(self) -> str:
        return self.name
        
    @enforce_types
    def pack(self, frame: tk.Frame) -> None:
        self.label = tk.Label(frame, text = self.name, font = self.font, bg = self.bg_colour, fg = self.fg_colour, width = 16, height = 4)
        self.label.pack(padx = 2, pady = 0, side = tk.LEFT, expand = False)

    @enforce_types
    def delete(self) -> None:
        self.forget()
        del self

    @enforce_types
    def forget(self) -> None:
        if self.label != None:
            self.label.pack_forget()

class Role_Row:
    # -- Constructor -- #
    @enforce_types
    def __init__(self, frame: tk.Frame) -> None:
        self.frames: list[tk.Frame] = []
        self.icons: list[list[tk.Label]] = []
        self.master_frame = frame
        self.max_row_length = 5
        self.add_row()

    # -- Methods -- #
    @enforce_types
    def add_row(self) -> None:
        self.frames.append(tk.Frame(self.master_frame, bg = "#d3d3d3"))
        self.icons.append([])

    @enforce_types
    def remove_end_row(self) -> None:
        del self.frames[-1]
        del self.icons[-1]

    @enforce_types
    def add_item(self, icon: Role_Icon) -> None:
        if len(self.icons[-1]) < self.max_row_length:
            self.icons[-1].append(icon)
            self.pack()
        else:
            self.add_row()
            self.add_item(icon)
            
    @enforce_types
    def remove_item(self, row: int, index: int) -> None:
        lst: list[Role_Icon] = self.icons[row]
        item = lst[index]
        del list[index]
        item.delete()

    @enforce_types
    def remove_end_item(self) -> None:
        if len(self.icons[-1]) == 0:
            self.remove_end_row()
            self.remove_end_item()
        else:
            icon = self.icons[-1][-1]
            del self.icons[-1][-1]
            icon.delete()

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
                icon.pack(self.frames[i])

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
    def __eq__(self, value: str) -> bool:
        return self.name == value
    
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
        self.delete_button = tk.Button(self.frame, text = "Remove", fg = "#ffffff", bg = "#ff0000", highlightbackground = "#cd0000", activebackground = "#aa0000", font = main_font, command = lambda: self.delete(self.icon_frame)).pack(side = tk.RIGHT)
        self.pack()

    # -- Methods -- #
    @enforce_types
    def delete(self, role_icon_frame: Role_Row) -> None:
        self.frame.pack_forget()
        role_icon_frame.remove_end_item()
        self.players.remove(self)
        del self