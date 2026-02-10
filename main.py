import os
import scripts.wallpapertools as w
import scripts.setuptools as s
import scripts.multiplatform as m
from scripts.settings import open_settings
from tkinter import Frame, Label, Button, mainloop, DISABLED, NORMAL, messagebox, PhotoImage, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tktooltip import ToolTip
import sys
import webbrowser


def info_txt(txt, show_resolution=True):
    global info_label
    if show_resolution and w.layout_data:
        txt += f"\ndesired resolution: {int(w.layout_data['img_size'][0]+1)} x {int(w.layout_data['img_size'][1]+1)}px"
    while txt.count("\n") < 2:
        txt += "\n"

    info_label.config(text=txt)
    root.update()


def start_setup():
    global setup_btn, wallpaper_btn, info_label
    w.load_monitors()
    canceled = False

    for screens in w.layout_data['setup_order']:
        lines = s.get_scale(w.layout_data, screens, root)

        if lines:
            w.calculate_scale(screens, lines)
        else:
            canceled = True
            break

        gap = s.get_gap(w.layout_data, screens, root)
        if gap:
            w.save_gap(screens, gap)
        else:
            canceled = True
            break

    if canceled:
        wallpaper_btn.config(state=DISABLED)
        info_txt("setup canceled\nclick again to retry", False)
        return

    w.calculate_img_conversion()
    if w.verify_data(w.data):
        w.save_data()
        wallpaper_btn.config(state=NORMAL)
        info_txt("configuration saved")
    else:
        info_txt("error: config invalid", False)


def set_wallpaper(file_path=False):
    global info_label, root
    if not file_path:
        file_path = m.get_file()
    if not file_path:
        return False

    filename = os.path.basename(file_path)
    if "converted85" in filename:
        if not messagebox.askyesno(
            "k85-wallpaper-tool",
            "This file name suggests it’s already been converted.\nAre you sure you want to use it?",
        ):
            return True

    setup_btn.config(state=DISABLED)
    wallpaper_btn.config(state=DISABLED)
    info_txt("processing..\n" + filename)

    try:
        video, path = w.convert_wallpaper(file_path, info_txt)
        setup_btn.config(state=NORMAL)
        wallpaper_btn.config(state=NORMAL)
    except:
        info_txt("error: can't process image\n" + filename)
        setup_btn.config(state=NORMAL)
        wallpaper_btn.config(state=NORMAL)
        return False

    if video == "no_ffmpeg":
        info_txt("error: ffmpeg not installed\n")
    elif video:
        info_txt("wallpaper converted\n" + filename)
    else:
        m.set_wallpaper_span()

        if m.set_wallpaper(path):
            info_txt("wallpaper set\n" + filename)
        else:
            info_txt("error: can't change wallpaper.\ntry setting wallpaper.png manually")
    return True


# ----- UI -----

# icon
root = TkinterDnD.Tk()
if sys.platform.startswith("win"):
    root.iconbitmap(s.resource_path("assets/icon.ico"))
else:
    root.iconphoto(False, PhotoImage(file=s.resource_path("assets/icon.png")))

TT_font = ("Arial", 11)


# open drag-and-drop file
def on_drop(event):
    if wallpaper_btn.cget("state") == "normal":
        set_wallpaper(root.tk.splitlist(event.data)[0])


root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', on_drop)

# dark / light theme
style = ttk.Style()
style.theme_use("clam")

if m.has_dark_theme():
    w.data['theme'] = 'dark'
    bg = "#262626"
    fg = "#f0f0f0"
    link = "#a377f0"
    style.configure(
        "TCombobox",
        fieldbackground="#2b2b2b",
        background="#2b2b2b",
        bordercolor="#9b9b9b",
    )
else:
    w.data['theme'] = 'light'
    bg = "#f0f0f0"
    fg = "#1a1a1a"
    link = "#4305af"
    style.configure(
        "TCombobox",
        fieldbackground="#f0f0f0",
        background="#f0f0f0",
        bordercolor="#565656",
    )

root.option_add("*Background", bg)
root.option_add("*Foreground", fg)
root.option_add("*activeBackground", bg)
root.option_add("*activeForeground", fg)
root.configure(bg=bg)

root.geometry("400x200")
root.geometry(f"+{root.winfo_screenwidth()//2-200}+{root.winfo_screenheight()//2-200}")

root.title("k85 wallpaper tool")
root.resizable(False, False)
root.option_add("*Font", "Arial 14")
root.option_add("*Button.cursor", "hand2")

# basic buttons
info_label = Label(
    root,
    text="",
    pady=10,
    padx=10,
    width=200,
)
info_label.pack()

btn_frame = Frame(root)
btn_frame.pack(pady=10)

setup_btn = Button(btn_frame, text="setup", command=start_setup)
setup_btn.pack(side="left", padx=5)

wallpaper_btn = Button(btn_frame, text="set wallpaper", command=set_wallpaper, state=DISABLED)
wallpaper_btn.pack(side="right", padx=5)

donate_link = Label(root, text="Donate", fg=link, cursor="hand2", font=("Arial", 12, "underline"))
donate_link.bind("<Button-1>", lambda: webbrowser.open("https://kisielo85.github.io/donate"))
donate_link.place(relx=1.0, rely=1.0, anchor="se", x=-8, y=-10)


settings_icon = PhotoImage(file=s.resource_path(f"assets/icon_settings_{w.data['theme']}_img.png"))
settings_btn = Button(root, image=settings_icon, bd=0, command=lambda: open_settings(root, w.data, w.save_data))
settings_btn.place(relx=1, rely=0, x=-30, y=4)

# tooltips
# fmt: off
ToolTip(donate_link, msg="This project is 100% free and open-source.\nDonating doesn't unlock any perks or features, but it is appreciated :)", delay=0.3, font=TT_font)
ToolTip(settings_btn, msg="Settings", delay=0.3, font=TT_font)
# fmt: on


if len(sys.argv) >= 2:
    file_open = sys.argv[1]
else:
    file_open = False

if w.load_data():
    wallpaper_btn.config(state=NORMAL)
    info_txt(f"config loaded\n{w.data['current_layout']}\n")
    if file_open:
        if set_wallpaper(file_open):
            sys.exit()
else:
    info_txt(
        f"{f"can't open file before setup\n{os.path.basename(file_open)}\n" if file_open else ""}click setup to begin configuration",
        False,
    )


mainloop()
