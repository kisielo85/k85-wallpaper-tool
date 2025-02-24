import sys
import scripts.wallpapertools as w
import scripts.setuptools as s
from tkinter import Tk, Label, Button, mainloop


def start_setup():
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
        # self.ui.btn_set_wallpaper.setEnabled(False)
        # self.ui.label_info.setText("setup canceled\nclick again to retry")
        return

    w.calculate_img_conversion()
    if w.verify_data(w.data):
        w.save_data()
        # self.ui.btn_set_wallpaper.setEnabled(True)
        # self.ui.label_info.setText(f"configuration saved\n{self.resolution()}")

    else:
        pass
        # self.ui.label_info.setText("error: config invalid")
    print("steup done")


def set_wallpaper():
    pass
    # file_dialog = QFileDialog(self)
    # file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)
    # file_dialog.setViewMode(QFileDialog.ViewMode.Detail)
    # file_dialog.setNameFilters(["(*.jpg *.jpeg *.png)"])
    # if file_dialog.exec():
    #    file_path = file_dialog.selectedFiles()[0]
    #    w.set_wallpaper(w.convert_wallpaper(file_path))


master = Tk()
master.geometry("200x200")
master.title("k85 wallpaper tool")

Label(
    master,
    text="info sus amogus sus gus gus suuuuussssss gus amogus",
    pady=10,
    padx=10,
    width=200,
).pack()

setup_btn = Button(master, text="setup", command=start_setup)
setup_btn.pack(pady=10)

wallpaper_btn = Button(master, text="set_wallpaper", command=set_wallpaper)
wallpaper_btn.pack(pady=10)

mainloop()
