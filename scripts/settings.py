from tkinter import Frame, Label, PhotoImage, Toplevel, messagebox
from tktooltip import ToolTip
import scripts.setuptools as s
import sys

TT_font = ("Arial", 11)
data = {}


class Toggle(Frame):
    def __init__(self, parent, name, state, command=None, tooltip=None, confirm_yes=None, confirm_no=None):
        super().__init__(parent)

        self.img_off = PhotoImage(file=s.resource_path(f"assets/icon_switch_off_{data['theme']}_img.png"))
        self.img_on = PhotoImage(file=s.resource_path(f"assets/icon_switch_on_{data['theme']}_img.png"))
        self.name = name
        self.command = command
        self.state = state
        self.confirm_yes = confirm_yes
        self.confirm_no = confirm_no

        self.label = Label(self, text=name)
        self.label.pack(side="left")

        self.switch = Label(self, image=self.img_on if state else self.img_off, cursor="hand2")
        self.switch.pack(side="right")

        ToolTip(self.switch, msg=lambda: f"current state: {"ON" if self.state else "OFF"}", delay=0.3, font=TT_font)

        if tooltip:
            ToolTip(self.label, msg=tooltip, delay=0.3, font=TT_font)

        self.switch.bind("<Button-1>", self.toggle)

    def toggle(self, event=None):
        # confirmation
        ok = True
        if self.state and self.confirm_no:
            ok = messagebox.askokcancel(f"Disable {self.name}?", self.confirm_no, parent=self.winfo_toplevel())
        elif not self.state and self.confirm_yes:
            ok = messagebox.askokcancel(f"Enable {self.name}?", self.confirm_yes, parent=self.winfo_toplevel())
        if not ok:
            return

        self.state = not self.state
        self.switch.config(image=self.img_on if self.state else self.img_off)
        if self.command:
            self.command(self.state)


def set_multi_layout(val):
    data['multiple_layouts'] = val

    if not val:
        current = data['current_layout']
        data['layouts'] = {current: data['layouts'][current]}


def open_settings(root, d, save_data):
    global data
    data = d
    settings = Toplevel(root)
    settings.geometry("300x200")
    settings.geometry(f"+{root.winfo_x()+50}+{root.winfo_y()+50}")
    settings.title("Settings")
    settings.transient(root)
    settings.grab_set()
    if sys.platform.startswith("win"):
        settings.iconbitmap(s.resource_path("assets/icon.ico"))
    else:
        settings.iconphoto(False, PhotoImage(file=s.resource_path("assets/icon.png")))

    multi_switch = Toggle(
        settings,
        "Multiple layouts",
        data['multiple_layouts'],
        command=set_multi_layout,
        tooltip="[Experimental feature]\nAllow wallpaper-tool to remember multiple layouts.\nUse this if you frequently plug/unplug displays",
        confirm_no="This will delete all saved layouts, except the current one",
    )
    multi_switch.pack()

    settings.wait_window()
    save_data()
