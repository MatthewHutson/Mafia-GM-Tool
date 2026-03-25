# -- Imports -- #
from utils import *
import typing as tp
from menu.menu_classes import *
import tkinter as tk
import json

# -- Classes -- #
class Setting:
    # -- Constructor -- #
    @enforce_types
    def __init__(self, master: Vertical_Scroll_Frame, name: str, data: dict, bg2: str) -> None:
        # -- Internal Data -- #
        self.name: str = name
        self.data: dict = data

        # -- Tkinter Objects -- #
        self.frame = tk.Frame(master.canvas)
        self.nameplate = tk.Label(self.frame, text = self.name, bg = bg2)
        self.description_button = tk.Button(self.frame, text = "Info", command = self.description_popup, bg = "#5D9FF0", activebackground = "#4980C4", fg = "#FFFFFF", activeforeground= "#FFFFFF")
        self.gen_choice_widget()

    # -- Properties -- #
    @property
    @enforce_types
    def description(self) -> str:
        return self.data["description"]
    
    @property
    @enforce_types
    def type(self) -> str:
        return self.data["type"]
    
    @property
    @enforce_types
    def value(self) -> Any:
        self.data["value"] = self.widget_value.get()
        return self.data["value"] 

    # -- Methods -- #
    @enforce_types
    def description_popup(self) -> None:
        messagebox.showinfo("Description", self.description)

    @enforce_types
    def gen_choice_widget(self) -> None:
        match self.type:
            case "checkbox":
                self.widget_value = tk.IntVar(value = self.data["value"])
                self.choice_widget = tk.Checkbutton(self.frame, variable = self.widget_value)
            case _:
                self.choice_widget = tk.Label(self.frame, text = "N/A")

    @enforce_types
    def pack(self) -> None:
        self.frame.pack(side = tk.TOP, padx = 2, pady = 2, anchor = "ne", ipady = 8, fill = "x")
        self.nameplate.pack(side = tk.LEFT, padx = 2, fill = "both", expand = True)
        self.choice_widget.pack(side = tk.RIGHT, padx = 2, fill = "y", ipadx = 4)
        self.description_button.pack(side = tk.RIGHT, padx = 2, fill = "y", ipadx = 12)

    @enforce_types
    def close(self) -> None:
        self.data["value"] = self.widget_value.get()
        self.frame.pack_forget()

# -- Global Vars -- #
instances: list[tk.Toplevel] = []
frames: list[Setting] = []

# -- Functions -- #
@enforce_types
def load_settings() -> dict:
    try:
        with open("settings.json", 'r') as file:
            data: dict = json.load(file)
    except:
        data: dict = {}

    return data  

@enforce_types
def remove_instances() -> None:
    global instances, frames

    for i in range(len(frames)):
        setting = frames.pop(0)
        setting.close()

    for i in range(len(instances)):
        instance = instances.pop(0)
        instance.destroy()

@enforce_types
def display_settings(root: tk.Tk, bg: str, font: tuple[str, int], entries: Menu_Entry) -> None:
    # -- Initialisation - #
    global instances, frames
    settings: dict = entries.settings
    root = tk.Toplevel()
    root.resizable(False, True)
    root.geometry("318x384")
    root.title("Game Settings")

    root.protocol("WM_DELETE_WINDOW", remove_instances())

    remove_instances()
    instances.append(root)

    main_frame = Vertical_Scroll_Frame(master = root)

    # -- Card Index-- #
    for name, data in settings.items():
        frames.append(Setting(main_frame, name, data, bg))

    for setting in frames:
        setting.pack()
        