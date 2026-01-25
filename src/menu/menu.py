# -- Imports -- #
from utils import *
from menu.menu_classes import *
import tkinter as tk
from tkinter import messagebox

# -- Global Variables -- #
root: tk.Tk = tk.Tk()

input_frame = tk.Frame(root)
name_entry: tk.Entry = tk.Entry(input_frame)

MAX_PLAYERS: int = 8
players: list[Player_Frame] = []

player_tab = tk.Frame(root, bg = "lightgrey")

main_font = ("Airial", 10)

# -- Functions -- #
@enforce_types
def add_player(players: list[tk.Label]) -> None:
    try: 
        user_input: str = name_entry.get().strip()
        
        if not user_input: 
            raise ValueError
        
        name_entry.delete(0, tk.END)

        if len(players) >= MAX_PLAYERS: 
            messagebox.showwarning("Warning", "You Have Reached The Maximum Number of Players!")
            raise IndexError
        
        for frame in players:
            if frame == capitalise_words(user_input):
                messagebox.showwarning("Warning", "A Player With This Name Already Exists!")
                raise ValueError
        
        player_frame = Player_Select_Frame(user_input, player_tab, main_font, players)
        players.append(player_frame)

    except: pass

@enforce_types
def setup_menu() -> None:
    # -- Menu -- #
    root.geometry("1024x512")
    root.title("Mafia Game")
    tk.Label(root, text = "Player Selection", font = ("Airial", 16), bg = "lightgrey").pack(side = tk.TOP, fill = "x", pady = 4)

    # -- Add Player Input -- #
    tk.Label(input_frame, text = "Name:").pack(side = tk.LEFT, padx = 8, pady = 8)
    add: tk.Button = tk.Button(input_frame, text = "Add", command = lambda: add_player(players), bg = "#00ff00", highlightbackground = "#00cd00", activebackground = "#00aa00").pack(side = tk.RIGHT, padx = 8, pady = 8)
    name_entry.pack(fill = "x", padx = 8, pady = 8, ipady = 12)
    input_frame.pack_propagate(False)
    input_frame.pack(side = tk.TOP, anchor = "w", ipadx = 158, ipady = 20)

    # -- Player Display Tab -- #
    tk.Label(player_tab, text = "Players", font = main_font).pack(side = tk.TOP, padx = 4, pady = 4,  fill = "x")
    player_tab.pack(side = tk.TOP, anchor = "w", padx = 4, pady = 4, ipadx = 128, ipady = 256)
    root.mainloop()