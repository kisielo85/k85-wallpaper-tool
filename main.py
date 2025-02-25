import os
import scripts.wallpapertools as w
import scripts.setuptools as s
import scripts.multiplatform as m
from tkinter import Tk, Frame, Label, Button, mainloop, DISABLED, NORMAL, filedialog


def info_txt(txt, show_resolution=True):
    global info_label
    if show_resolution:
        txt += f"\ndesired resolution: {int(w.data['img_size'][0]+1)} x {int(w.data['img_size'][1]+1)}px"
    while txt.count("\n") < 2:
        txt += "\n"

    info_label.config(text=txt)


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


def set_wallpaper():
    global info_label, root
    file_path = m.get_file()
    if not file_path:
        return

    filename = os.path.basename(file_path)
    info_txt("processing..\n" + filename)
    root.update_idletasks()

    try:
        img = w.convert_wallpaper(file_path)
    except:
        info_txt("error: can't process image\n" + filename)
        return
    
    m.set_wallpaper_span()

    if m.set_wallpaper(img):
        info_txt("wallpaper set\n" + filename)
    else:
        info_txt("error: can't set wallpaper")


root = Tk()
root.geometry("350x150")
root.title("k85 wallpaper tool")
root.resizable(False, False)
root.option_add("*Font", "Arial 14")

info_label = Label(
    root,
    text="",
    pady=10,
    padx=10,
    width=200,
)
info_label.pack()
info_txt("click setup to begin configuration", False)

btn_frame = Frame(root)
btn_frame.pack(pady=10)

setup_btn = Button(btn_frame, text="setup", command=start_setup)
setup_btn.pack(side="left", padx=5)

wallpaper_btn = Button(
    btn_frame, text="set wallpaper", command=set_wallpaper, state=DISABLED
)
wallpaper_btn.pack(side="right", padx=5)

if w.load_data():
    wallpaper_btn.config(state=NORMAL)
    info_txt("previous config loaded")

mainloop()
