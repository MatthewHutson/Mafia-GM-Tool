# -- Imports -- #
from __future__ import annotations
from utils import *
from typing import Protocol
from classes_and_types import *
from random import randint
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from typing import Union

# -- Classes -- #
class Vertical_Scroll_Frame(tk.Frame):
    @enforce_types
    def __init__(self, master: Union[tk.Tk, tk.Toplevel, tk.Frame], bg: str = "#F0F0F0", bg_2: str = "#d3d3d3", pack: bool = True) -> None:
        # -- Style Given Using Non_Default -- #
        # self.scroll_colour: str = bg_2 #4F4F4F
        # style = ttk.Style()
        # style.theme_use('clam')
        # style.configure(
        #     "Custom.Vertical.TScrollbar",
        #     gripcount = 0,
        #     background = self.scroll_colour,   # Scrollbar slider color
        #     darkcolor = bg,    # Darker edge
        #     lightcolor = bg,   # Lighter edge
        #     troughcolor = bg,  # Background trough
        #     bordercolor = bg,
        #     arrowcolor = bg,
        #     activebackground = bg
        # )
        # style.map(
        #     "Custom.Vertical.TScrollbar",
        #     background=[("disabled", self.scroll_colour)],  # thumb when disabled
        #     arrowcolor=[("disabled", bg)],  # arrows when disabled
        #     troughcolor=[("disabled", bg)]  # trough when disabled
        # )

        # -- Style Given Using Non_Default -- #
        self.scroll_bar = tk.Scrollbar(master, orient = tk.VERTICAL, takefocus = True) #style = "Custom.Vertical.TScrollbar" with ttk Scrollbar Instead
        self.canvas = tk.Canvas(master, yscrollcommand = self.scroll_bar.set, bg = bg_2, highlightthickness = 0, borderwidth = 0)
        self.scroll_bar.configure(command = self.canvas.yview)
        self.root = master
        self.bg = bg

        super().__init__(self.canvas, bg = bg)

        self.scroll_bar.pack(side = tk.RIGHT, fill = "y", ipadx = 4, expand = False)
        self.scroll_bar.update()
        if pack: self.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)

        self.canvas.create_window((0, 0), window = self, anchor = tk.NW)
        self.initialise()
        
    # -- Methods -- #
    @enforce_types
    def scroll_all(self, event = None) -> None:
        self.canvas.config(scrollregion = self.canvas.bbox("all"))

    @enforce_types
    def scroll_event(self, event) -> None:
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    @enforce_types
    def initialise(self) -> None:
        self.canvas.bind("<Configure>", self.scroll_all)
        self.canvas.master.bind("<MouseWheel>", self.scroll_event)

    @enforce_types
    def bind_all_children(self, widget: tk.Widget, sequence: str, func: Any) -> None:
        for child in widget.winfo_children():
            self.bind_all_children(child, sequence, func)

        widget.bind(sequence, func)

    @enforce_types
    def add(self, frame: tk.Widget, height: int = 0) -> None:
        frame.pack(side = tk.TOP, fill = "x", pady = 2, ipady = height, expand = True)
        frame.update()

    @enforce_types
    def add_player_frame(self, frame: Player_Frame) -> None:
        frame.pack()
        self.bind_all_children(frame.frame, "<MouseWheel>", self.scroll_event)
        frame.update()

    @enforce_types
    def add_setting(self, setting: tk.Frame) -> None:
        setting.pack()
        self.bind_all_children(setting.master, "<MouseWheel>", self.scroll_event)
        setting.master.update()

    @enforce_types
    def pack(self, **kwargs) -> None:
        self.canvas.pack(**kwargs)
        self.root.update()
        self.scroll_all()
        self.canvas_size: int = self.canvas.winfo_width()

        tk.Frame(self, width = self.canvas_size, height = 0, bg = self.bg).pack(side = tk.TOP)

class Role_Icon:
    # -- Constructors -- #
    @enforce_types
    def __init__(self, roles: list[str], main_font: tuple[str, int], entries: Menu_Entry, size: tuple[int] = (16, 4), padding: tuple[int] = (2, 0), command: Any = None, data: Game_Data = None) -> None:
        self.font = main_font
        self.entries = entries
        self.data = data
        self.size = size
        self.padding = padding
        self.label = None
        self.frame = None
        self.frames = None

        if command == None: self.command = self.change_role
        else: self.command = command

        self.re_init(roles)

    @enforce_types
    def re_init(self, roles: list[list[str]]) -> None:
        if self.data is None: self.roles = [self.entries.role_dict[role] for role in roles]
        else: self.roles = [self.data.roles[role] for role in roles]
        self.role_names = roles
        self.index = len(self.roles) - 1

        self.entries.current_roles_lists.append(roles)

        if self.command == self.change_role:
            self.cycle()

    # -- Property -- #
    @property
    def role(self) -> Role:
        if self.index < len(self.roles):
            return self.roles[self.index]
        else:
            return self.roles[-1]

    @property
    def name(self) -> str:
        return self.role.name
    
    @property
    def alignment(self) -> bool:
        return self.role.true_alignment
    
    @property
    def bg_colour(self) -> str:
        if self.name == "Testing":
            return  "#36eeee"
        elif self.alignment == None:
            return  "#f5f5f5"
        elif self.alignment:
            return "#48f748"
        else:
            return "#c72e2e"

    @property
    def fg_colour(self) -> str:
        if self.name == "Testing":
            return  "#000000"
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
    def pack(self, frame: tk.Frame = None, frames: list[object] = None, side = tk.LEFT) -> None:
        if self.frame == None:
            self.frame = frame
        
        if self.frames == None:
            self.frames = frames
        
        self.label = tk.Button(self.frame, text = self.name, font = self.font, bg = self.bg_colour, highlightbackground = self.bg_colour, activebackground = self.bg_colour, fg = self.fg_colour, activeforeground = self.fg_colour, width = self.size[0], height = self.size[1], command = self.command)
        self.label.pack(padx = self.padding[0], pady = self.padding[1], side = side, expand = False)

    @enforce_types
    def delete(self) -> None:
        self.forget()
        try: self.entries.current_roles_lists.remove(self.roles)
        except: pass
        del self

    @enforce_types
    def forget(self) -> None:
        if self.label != None:
            self.label.pack_forget()
        
    @enforce_types
    def change_role(self) -> None:
        if self.alignment != False:
            current_role = [role.name for role in self.roles]
            new_roles = self.entries.non_active_non_evil_roles
            self.entries.current_roles_lists.remove(current_role)

            if len(new_roles) > 0:
                new_role_names: list[str] = new_roles[0]
            else:
                new_role_names = current_role

            self.entries.all_roles_lists.remove(new_role_names)

            self.roles = [self.entries.role_dict[role] for role in new_role_names]
            self.role_names = new_role_names

            if len(new_role_names) > 1:
                self.cycle()
            else:
                self.refresh()

            self.entries.current_roles_lists.append(new_role_names)
            self.entries.all_roles_lists.append(new_role_names)

        else:
            self.cycle()

    @enforce_types
    def cycle(self) -> None:
        self.index += 1
        self.index = self.index % len(self.roles)
        self.refresh()

    @enforce_types
    def refresh(self) -> None:
        if self.frames != None:
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
    def __init__(self, frame: tk.Frame, bg: str) -> None:
        self.frames: list[tk.Frame] = []
        self.icons: list[list[Role_Icon]] = []
        self.master_frame = frame
        self.max_row_length = 6
        self.bg = bg

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
        self.frames.append(tk.Frame(self.master_frame, bg = self.bg))
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
    def add_entries(self, entries: Menu_Entry) -> None:
        self.entries = entries

    @enforce_types
    def shuffle(self) -> None:
        for row in self.icons:
            for icon in row:
                icon.shuffle()
        
class Player_Frame:
    # -- Constructor -- #
    def __init__(self, user_input: str, main_frame: Union[tk.Frame, Vertical_Scroll_Frame], main_font: tuple[str, int], bg: str, fg: str) -> None:
        self.frame = tk.Frame(main_frame, bg = bg)
        self.name_label = tk.Label(self.frame, text = capitalise_words(user_input), font = main_font, bg = bg, fg = fg).pack(side = tk.LEFT, fill = "x", padx = 4)
        self.frame.pack_propagate(False)
        self.name: str = capitalise_words(user_input)
        self.master = main_frame

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

    @enforce_types
    def delete(self) -> None:
        self.frame.pack_forget()
        del self

    @enforce_types
    def forget(self) -> None:
        self.frame.pack_forget()

    @enforce_types
    def configure(self, **kwargs) -> None:
        self.frame.configure(**kwargs)

    @enforce_types
    def pack_propagate(self, value: bool = False) -> None:
        self.frame.pack_propagate(value)

    @enforce_types
    def update(self) -> None:
        self.frame.update()

    @enforce_types
    def winfo_height(self) -> int:
        return self.frame.winfo_height()

class Player_Select_Frame(Player_Frame):
    # -- Constructor -- #
    @enforce_types
    def __init__(self, user_input: str, main_frame: tk.Frame, main_font: tuple[str, int], players: list[object], icon_frame: Role_Row, role_update: Any, bg: str, fg: str) -> None:
        super().__init__(user_input, main_frame, main_font, bg, fg)
        self.players = players
        self.icon_frame = icon_frame
        self.delete_button = tk.Button(self.frame, text = "Remove", fg = "#ffffff", bg = "#ff0000", highlightbackground = "#cd0000", activebackground = "#aa0000", font = main_font, command = self.delete).pack(side = tk.RIGHT, pady = 2)
        self.role_update = role_update

        if type(self.master) == Vertical_Scroll_Frame:
            self.master.add_player_frame(self)
        else:
            self.pack()

    # -- Methods -- #
    @enforce_types
    def delete(self, update: bool = True) -> None:
        self.frame.pack_forget()
        self.players.remove(self)
        self.icon_frame.remove_end_item()
        if update: self.role_update()
        del self

class Player_Role_Frame(Player_Frame):
    # -- Constructor -- #
    @enforce_types
    def __init__(self, name: str, data: Game_Data, main_frame: Union[tk.Frame, Vertical_Scroll_Frame], main_font: tuple[str, int], selected_players: list[str], selected_role: Role, number_of_targets: int, pack_alive_and_dead: Any, bg: str, fg: str) -> None:
        super().__init__(name, main_frame, main_font, bg, fg)
        self.data = data
        self.alignment = self.role.true_alignment
        self.selected_players = selected_players
        self.number_of_targets = number_of_targets
        self.selected_role = selected_role
        self.selected_role_name = selected_role.name
        self.selected = False
        self.current_role_icon = None
        self.pack_alive_and_dead: Callable = pack_alive_and_dead

        # -- Role Colours -- #
        self.role_fg = "#000000"


        if self.role.name == "Testing":
            self.role_bg = "#36eeee"
        elif self.alignment == None:
            self.role_bg = "#f5f5f5"
        elif self.alignment:
            self.role_bg = "#48f748"
        else:
            self.role_bg = "#c72e2e"
            self.role_fg = "#ffffff"

        # -- Linked Icons -- #
        if self.role.linked:
            self.linked_bg = "#f94af9"
            self.linked_fg = "#ffffff"
        else:
            self.linked_bg = "#a0ddbe"
            self.linked_fg = "#000000"

        if self.role.drunk:
            self.drunk_bg = "#e69138"
        else:
            self.drunk_bg = "#DBC1FC"

        # -- Solo Win Icons -- #
        if self.role.solo_win:
            self.solo_win_bg = "#48f748"
        else:
            self.solo_win_bg = "#d1d1d1"

        # -- Extra Icons -- #
        self.linked_icon = tk.Button(self.frame, text = "", bg = self.linked_bg, activebackground = self.linked_bg, fg = self.linked_fg, activeforeground = self.linked_fg, width = 2, height = 2)
        self.drunk_icon = tk.Button(self.frame, text = "", bg = self.drunk_bg, activebackground = self.drunk_bg, fg = "#000000", activeforeground = "#000000", width = 2, height = 2)
        self.solo_win_icon = tk.Button(self.frame, text = "", bg = self.solo_win_bg, activebackground = self.solo_win_bg, fg = "#000000", activeforeground = "#000000", width = 2, height = 2)
        self.select_icon = tk.Button(self.frame, text = "Select", bg = "#5D9FF0", activebackground = "#4980C4", fg = "#FFFFFF", activeforeground = "#FFFFFF", width = 6, height = 4, command = self.select)


        if type(self.master) == Vertical_Scroll_Frame:
            self.master.add_player_frame(self)
        else:
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
    
    @property
    def kill_icon(self) -> tk.Button:
        if self.role.currently_alive:
            self._kill_icon = tk.Button(self.frame, text = "Kill", bg = "#F05D5D", activebackground = "#C44949", fg = "#FFFFFF", activeforeground = "#FFFFFF", width = 6, height = 4, command = self.kill)
        else:
            self._kill_icon = tk.Button(self.frame, text = "Revive", bg = "#474747", activebackground = "#2B2B2B", fg = "#FFFFFF", activeforeground = "#FFFFFF", width = 6, height = 4, command = self.revive)

        return self._kill_icon

    # -- Methods -- #
    @enforce_types
    def pack(self) -> None:
        self.role_icon.pack(side = tk.RIGHT, padx = 2, expand = False)
        self.select_icon.pack(side = tk.RIGHT, padx = 2, expand = False)
        self.kill_icon.pack(side = tk.RIGHT, padx = 2, expand = False)
        self.linked_icon.pack(side = tk.RIGHT, padx = 2, pady = 4, expand = False)
        self.drunk_icon.pack(side = tk.RIGHT, padx = 2, pady = 4, expand = False)
        self.solo_win_icon.pack(side = tk.RIGHT, padx = 2, pady = 4, expand = False)
        super().pack()

    @enforce_types
    def forget(self) -> None:
        self.current_role_icon.pack_forget()
        self.select_icon.pack_forget()
        try: self._kill_icon.pack_forget()
        except: pass

        self.linked_icon.pack_forget()
        self.drunk_icon.pack_forget()
        self.solo_win_icon.pack_forget()
        super().forget()

    @enforce_types
    def select(self) -> None:
        if len(self.selected_players) < self.number_of_targets and not self.selected:
            self.selected_players.append(self.name)
            self.selected = not self.selected

        elif self.selected:
            self.selected_players.remove(self.name)
            self.selected = not self.selected

        elif len(self.selected_players) >= self.number_of_targets:
            messagebox.showwarning("Warning", f"{self.selected_role_name} can only select {self.number_of_targets} target{"s" if self.number_of_targets != 1 else ""}!", icon = "warning")
        
        self.select_icon.configure(bg = self.selected_bg, activebackground = "#4980C4") 
        self.select_icon.update()
        self.select_icon.configure()

    @enforce_types
    def kill(self) -> None: 
        if messagebox.askyesno("Game Intervention", f"Are you sure you mean to dev kill {self.name}?", default = "no", icon = "question"):
            self.role.currently_alive = False

            del self.data.alive_players[self.name]
            self.data.dead_players[self.name] = self.role

            if self.role.alignment:
                del self.data.good_aligned[self.name]
            else:
                del self.data.evil_aligned[self.name]


            self.pack_alive_and_dead(self.data, self.selected_role, self.number_of_targets)

    @enforce_types
    def revive(self) -> None:
        if messagebox.askyesno("Game Intervention", f"Are you sure you mean to dev ressurect {self.name}?", default = "no", icon = "question"):
            self.role.currently_alive = True

            del self.data.dead_players[self.name]
            self.data.alive_players[self.name] = self.role

            if self.role.alignment:
                self.data.good_aligned[self.name] = self.role
            else:
                self.data.evil_aligned[self.name] = self.role

            self.pack_alive_and_dead(self.data, self.selected_role, self.number_of_targets)

# -- Protocols -- #
class Has_Widget_Children(Protocol):
    def winfo_children():
        ...
    def pack_forget():
        ...