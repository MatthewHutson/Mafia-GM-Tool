# -- Imports -- #
from utils import *
from classes_and_types import *
import tkinter as tk
from tkinter import messagebox

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
    def __init__(self, user_input: str, main_frame: tk.Frame, main_font: tuple[str, int], players: list[object]) -> None:
        super().__init__(user_input, main_frame, main_font)
        self.players = players
        self.delete_button = tk.Button(self.frame, text = "delete", fg = "#ffffff", bg = "#ff0000", highlightbackground = "#cd0000", activebackground = "#aa0000", font = main_font, command = lambda: self.delete()).pack(side = tk.RIGHT)
        self.pack()

    # -- Methods -- #
    @enforce_types
    def delete(self) -> None:
        self.frame.pack_forget()
        self.players.remove(self)
        del self
    