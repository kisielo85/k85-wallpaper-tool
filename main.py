import sys
from PyQt6.QtWidgets import QDialog, QApplication, QFileDialog
from ui_files.main_dialog import Ui_Dialog as Main_Dialog
import scripts.wallpapertools as w
import scripts.setuptools as s


class MainUI(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Main_Dialog()
        self.ui.setupUi(self)

        self.ui.btn_setup.clicked.connect(self.start_setup)
        self.ui.btn_set_wallpaper.clicked.connect(self.set_wallpaper)

        if w.load_data():
            self.ui.btn_set_wallpaper.setEnabled(True)
            self.ui.label_info.setText(f"previous config loaded\n{self.resolution()}")
        # self.start_setup()

    def resolution(self):
        return f"desired resolution: {int(w.data['img_size'][0]+1)} x {int(w.data['img_size'][1]+1)}px"

    # runs every configuration in order
    def start_setup(self):
        w.load_monitors()
        canceled = False
        for screens in w.data['setup_order']:
            lines = s.get_scale(w.data, screens)

            if lines:
                w.calculate_scale(screens, lines)
            else:
                canceled = True
                break

            gap = s.get_gap(w.data, screens)
            if gap:
                w.save_gap(screens, gap)
            else:
                canceled = True
                break

        if canceled:
            self.ui.btn_set_wallpaper.setEnabled(False)
            self.ui.label_info.setText("setup canceled\nclick again to retry")
            return

        w.calculate_img_conversion()
        if w.verify_data(w.data):
            w.save_data()
            self.ui.btn_set_wallpaper.setEnabled(True)
            self.ui.label_info.setText(f"configuration saved\n{self.resolution()}")

        else:
            self.ui.label_info.setText("error: config invalid")

    def set_wallpaper(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        file_dialog.setViewMode(QFileDialog.ViewMode.Detail)
        file_dialog.setNameFilters(["(*.jpg *.jpeg *.png)"])
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            w.set_wallpaper(w.convert_wallpaper(file_path))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainUI()
    window.show()
    sys.exit(app.exec())
