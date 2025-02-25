import sys
import scripts.wallpapertools as w
import scripts.setuptools as s
from tkinter import Tk, Label, Button, mainloop, DISABLED, NORMAL, filedialog

def resolution():
    return f"desired resolution: {int(w.data['img_size'][0]+1)} x {int(w.data['img_size'][1]+1)}px"

def start_setup():
    global setup_btn, wallpaper_btn, info_label
    w.load_monitors()
    canceled = False
    w.data['setup_order'] = [[0, 0]]  # DEBUG
    print("startloop")
    for screens in w.data['setup_order']:
        lines = s.get_scale(w.data, screens, master)

        print("lines:", lines)
        if lines:
            w.calculate_scale(screens, lines)
        else:
            canceled = True
            break

        gap = s.get_gap(w.data, screens, master)
        if gap:
            w.save_gap(screens, gap)
        else:
            canceled = True
            break

    if canceled:
        wallpaper_btn.config(state=DISABLED)
        info_label.config(text="setup canceled\nclick again to retry")
        return

    w.calculate_img_conversion()
    if w.verify_data(w.data):
        w.save_data()
        wallpaper_btn.config(state=NORMAL)
        info_label.config(text=f"configuration saved\n{resolution()}")
    else:
        info_label.config(text="error: config invalid")


def set_wallpaper():
    pass
    # file_dialog = QFileDialog()
    # file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)
    # file_dialog.setViewMode(QFileDialog.ViewMode.Detail)
    # file_dialog.setNameFilters(["(*.jpg *.jpeg *.png)"])
    # if file_dialog.exec():
    #    file_path = file_dialog.selectedFiles()[0]
    #    w.set_wallpaper(w.convert_wallpaper(file_path))


master = Tk()
master.geometry("200x200")
master.title("k85 wallpaper tool")

info_label = Label(
    master,
    text="info sus amogus sus gus gus suuuuussssss gus amogus",
    pady=10,
    padx=10,
    width=200,
)
info_label.pack()

setup_btn = Button(master, text="setup", command=start_setup)
setup_btn.pack(pady=10)

wallpaper_btn = Button(master, text="set_wallpaper", command=set_wallpaper)
wallpaper_btn.pack(pady=10)

mainloop()
