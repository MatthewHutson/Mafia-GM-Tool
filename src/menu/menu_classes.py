# -- Imports -- #
from utils import *
from classes_and_types import *
import tkinter as tk
from tkinter import messagebox
from copy import deepcopy

# -- Classes -- #
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
    def __init__(self, user_input: str, main_frame: tk.Frame, main_font: tuple[str, int], players: list[object]) -> None:
        super().__init__(user_input, main_frame, main_font)
        self.players = players
        self.delete_button = tk.Button(self.frame, text = "Remove", fg = "#ffffff", bg = "#ff0000", highlightbackground = "#cd0000", activebackground = "#aa0000", font = main_font, command = lambda: self.delete()).pack(side = tk.RIGHT)
        self.pack()

    # -- Methods -- #
    @enforce_types
    def delete(self) -> None:
        self.frame.pack_forget()
        self.players.remove(self)
        del self
    
class Role_Icon:
    # -- Constructor -- #
    @enforce_types
    def __init__(self, role: Role, main_font: tuple[str, int]) -> None:
        self.name = role.name
        self.alignment = role.alignment
        self.bg_colour = "#000000"
        self.fg_colour = "#000000"
        self.font = main_font

        if self.alignment == None:
            self.bg_colour = "#d3d3d3"
        elif self.alignment:
            self.bg_colour = "#00ff00"
        else:
            self.bg_colour = "#ff0000"
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
        self.label = tk.Label(frame, text = self.name, font = self.font, bg = self.bg_colour, fg = self.fg_colour)
        self.label.pack(side = tk.LEFT, ipadx = 16, ipady = 16)

    @enforce_types
    def delete(self) -> None:
        self.label.pack_forget()
        del self

class Role_Row:
    # -- Constructor -- #
    @enforce_types
    def __init__(self, frame: tk.Frame) -> None:
        self.data: list[dict[tk.Frame, tk.Label]] = [{}]
        self.master_frame = frame
        self.max_row_length = 8

    # -- Methods -- #
    @enforce_types
    def add_row(self) -> None:
        self.data.append({tk.Frame(self.master_frame, bg = "#d3d3d3"): []})

    @enforce_types
    def remove_end_row(self) -> None:
        del self.data[-1]

    @enforce_types
    def add_item(self, icon: Role_Icon) -> None:
        key: tk.Frame = self.data[-1].keys()[0]
        lst: list[Role_Icon] = self.data[-1][key]
        if len(lst) < self.max_row_length:
            list.append(icon)
            icon.pack(key)
        else:
            self.add_row()
            self.add_item(icon)

    @enforce_types
    def remove_item(self, row: int, index: int) -> None:
        row: dict = self.data[row]
        key: tk.Frame = row.keys()[0]
        lst: list[Role_Icon] = self.data[row][key]
        item = lst[index]
        del list[index]
        item.delete()

    @enforce_types
    def disapear(self) -> None:
        for row in self.data:
            row.keys()[0].pack_forget()
 
    @enforce_types
    def pack(self) -> None:
        self.disapear()
        for row in self.data:
            row.keys()[0].pack(side = tk.TOP, padx = 2, fill = "x", ipady = 16, pady = 2, expand = True)
