# -- Import -- #
from utils import *
import tkinter as tk
from tkinter import messagebox

# -- Global Variables -- #
root: tk.Tk = tk.Tk()
name_entry: tk.Entry = tk.Entry(root)#
MAX_PLAYERS: int = 8
players: list[tk.Label] = []
player_tab = tk.Frame(root, bg = "lightgrey")
main_font = ("Airial", 10)

# -- Menu Classes -- #
class PlayerFrame:
    # -- Attributes -- #
    frame: tk.Frame
    name: tk.Label
    delete: tk.Button

    # -- Constructor -- #
    @enforce_types
    def __init__(self, user_input: str) -> None:
        self.frame = tk.Frame(player_tab)

        self.delete_button = tk.Button(self.frame, text = "delete", bg = "red", fg = "white", font = main_font, command = lambda: self.delete()).pack(side = tk.RIGHT)
        self.name = tk.Label(self.frame, text = user_input.lower().capitalize(), font = main_font).pack(side = tk.LEFT, fill = "x", padx = 4)

        self.frame.pack_propagate(False)
        self.frame.pack(anchor = "n", side = tk.TOP, padx = 4, fill = "x", ipady = 16)

        self.name: str = user_input.lower().capitalize()

    # -- Methods -- #
    @enforce_types
    def delete(self) -> None:
        self.frame.pack_forget()
        players.remove(self)
        del self
    
    @enforce_types
    def __eq__(self, value):
        return self.name == str(value)


# -- Functions -- #
@enforce_types
def add_player(players: list[tk.Label]) -> None:
    try: 
        user_input: str = name_entry.get().strip()
        
        if not user_input: 
            raise ValueError
        
        name_entry.delete(0, tk.END)

        if len(players) >= MAX_PLAYERS: 
            messagebox.showwarning("Warning", "You Have Reached The Maximum Number Of Players!")
            raise IndexError
        
        for frame in players:
            if frame == user_input.lower().capitalize():
                messagebox.showwarning("Warning", "A Player With This Name Already Exists!")
                raise ValueError
        
        player_frame = PlayerFrame(user_input)
        players.append(player_frame)

    except: pass

@enforce_types
def setup_menu() -> None:
    # -- Menu -- #
    root.geometry("1024x512")
    root.title("Mafia Game")
    tk.Label(root, text = "Player Selection", font = ("Airial", 16), bg = "lightgrey").pack(side = tk.TOP, fill = "x", pady = 4)

    tk.Label(root, text = "Name:").pack(side = tk.LEFT, anchor = "nw", padx = 8, pady = 8)
    name_entry.pack(side = tk.LEFT, ipadx = 64, anchor = "nw", padx = 8, pady = 8)
    add: tk.Button = tk.Button(root, text = "Add", command = lambda: add_player(players)).pack(side = tk.LEFT, anchor = "nw", padx = 8, pady = 8)

    tk.Label(player_tab, text = "Players", font = main_font).pack(side = tk.TOP, padx = 4, pady = 4,  fill = "x")
    player_tab.pack(side = tk.TOP, anchor = "e", padx = 4, pady = 4, ipadx = 128, ipady = 256)
    root.mainloop()