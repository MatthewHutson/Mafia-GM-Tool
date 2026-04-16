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
    def __init__(self, master: Vertical_Scroll_Frame, name: str, settings: dict, bg2: str, fg:str) -> None:
        # -- Internal Data -- #
        self.settings = settings
        self.name: str = name
        self.master: Vertical_Scroll_Frame = master
        self.bg = bg2

        # -- Tkinter Objects -- #
        self.frame = tk.Frame(master, bg = bg2)
        self.nameplate = tk.Label(self.frame, text = self.name, bg = bg2, fg = fg)
        self.description_button = tk.Button(self.frame, text = "Info", command = self.description_popup, bg = "#5D9FF0", activebackground = "#4980C4", fg = "#FFFFFF", activeforeground= "#FFFFFF")
        self.gen_choice_widget()

    # -- Properties -- #
    @property
    @enforce_types
    def description(self) -> str:
        return self.data["description"]
    
    @property
    @enforce_types
    def data(self) -> dict[str, Any]:
        return self.settings[self.name]
    
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
                self.choice_widget = tk.Checkbutton(self.frame, variable = self.widget_value, bg = self.bg, activebackground = self.bg)
            case _:
                self.widget_value = "N/A"
                self.choice_widget = tk.Label(self.frame, text = "N/A")

    @enforce_types
    def pack(self) -> None:
        self.nameplate.pack(side = tk.LEFT, padx = 2, fill = "both", expand = True)
        self.choice_widget.pack(side = tk.RIGHT, padx = 2, fill = "y", ipadx = 4)
        self.description_button.pack(side = tk.RIGHT, padx = 2, fill = "y", ipadx = 12)
        self.master.add(self.frame, 8)

    @enforce_types
    def update(self) -> None:
        self.data["value"] = self.widget_value.get()

    @enforce_types
    def close(self) -> None:
        self.update()
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

    for setting_data in data.values():
        if setting_data["type"] == "checkbox" and setting_data["value"] == "random":
            setting_data["value"] = choice([0, 1])

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
def update_settings() -> None:
    # -- Updates All Settings When Called By Menu -- #
    global frames
    for setting in frames:
        setting.update()

@enforce_types
def display_settings(root: tk.Tk, bg: str, bg_2: str, text_colour: str, entries: Menu_Entry) -> None:
    # -- Initialisation -- #
    global instances, frames
    settings: dict = entries.settings
    root = tk.Toplevel()
    root.resizable(False, True)
    root.geometry("318x384")
    root.title("Game Settings")
    root.config(bg = bg)

    root.protocol("WM_DELETE_WINDOW", remove_instances())

    remove_instances()
    instances.append(root)

    main_frame = Vertical_Scroll_Frame(master = root, bg = bg, bg_2 = bg_2)

    # -- Card Index-- #
    for name in settings.keys():
        frames.append(Setting(main_frame, name, settings, bg_2, text_colour))

    for setting in frames:
        setting.pack()
    
    main_frame.update()
    main_frame.scroll_all()
        