import os
import scripts.wallpapertools as w
import scripts.setuptools as s
import scripts.multiplatform as m
from tkinter import (
    Frame,
    Label,
    Button,
    mainloop,
    DISABLED,
    NORMAL,
    messagebox,
    PhotoImage,
    ttk,
    StringVar,
)
from tkinterdnd2 import DND_FILES, TkinterDnD
from tktooltip import ToolTip
import sys
import webbrowser


def info_txt(txt, show_resolution=True):
    global info_label
    if show_resolution:
        txt += f"\ndesired resolution: {int(w.data['img_size'][0]+1)} x {int(w.data['img_size'][1]+1)}px"
    while txt.count("\n") < 2:
        txt += "\n"

    info_label.config(text=txt)
    root.update()


def start_setup():
    global setup_btn, wallpaper_btn, info_label
    w.load_monitors()
    canceled = False

    for screens in w.data['setup_order']:
        lines = s.get_scale(w.data, screens, root)

        if lines:
            w.calculate_scale(screens, lines)
        else:
            canceled = True
            break

        gap = s.get_gap(w.data, screens, root)
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
    theme = "dark"
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
    theme = "light"
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

root.geometry("400x250")
root.title("k85 wallpaper tool")
root.resizable(False, False)
root.option_add("*Font", "Arial 14")

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
donate_link.bind("<Button-1>", lambda e: webbrowser.open("https://kisielo85.github.io/donate"))
donate_link.place(relx=1.0, rely=1.0, anchor="se", x=-8, y=-10)

# layout selection
layouts_frame = Frame(root)
layouts_frame.pack(pady=10)

current_var = StringVar()
combobox = ttk.Combobox(layouts_frame, textvariable=current_var)
combobox['values'] = ('value1', 'value2', 'value3')
combobox.pack(side="left", padx=3)
combobox.option_add("*Foreground", fg)
combobox.set('erm')

rename_icon = PhotoImage(file=f"assets/icon_rename_{theme}_img.png")
delete_icon = PhotoImage(file=f"assets/icon_delete_{theme}_img.png")
add_icon = PhotoImage(file=f"assets/icon_add_{theme}_img.png")

root.option_add("*Foreground", bg)
rename_btn = Button(layouts_frame, image=rename_icon)
rename_btn.pack(side="left", padx=3)

delete_btn = Button(layouts_frame, image=delete_icon)
delete_btn.pack(side="left", padx=3)

add_btn = Button(layouts_frame, image=add_icon)
add_btn.pack(side="left", padx=3)
root.option_add("*Foreground", fg)

# tooltips
TT_font = ("Arial", 11)
# fmt: off
ToolTip(donate_link, msg="This project is 100% free and open-source.\nDonating doesn't unlock any perks or features, but it is appreciated :)", delay=0.3, font=TT_font)
ToolTip(rename_btn, msg="rename", delay=0.3, font=TT_font)
ToolTip(delete_btn, msg="delete", delay=0.3, font=TT_font)
ToolTip(add_btn, msg="add", delay=0.3, font=TT_font)
# fmt: on


if len(sys.argv) >= 2:
    file_open = sys.argv[1]
else:
    file_open = False

if w.load_data():
    wallpaper_btn.config(state=NORMAL)
    info_txt("previous config loaded")
    if file_open:
        if set_wallpaper(file_open):
            sys.exit()
else:
    info_txt(
        f"{f"can't open file before setup\n{os.path.basename(file_open)}\n" if file_open else ""}click setup to begin configuration",
        False,
    )

mainloop()
