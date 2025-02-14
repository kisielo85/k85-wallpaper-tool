import sys
from PyQt6.QtWidgets import QDialog, QApplication, QFileDialog
from ui_files.scale_setup import Ui_Dialog as Scale_Dialog
from ui_files.gap_setup import Ui_Dialog as Gap_Dialog
from ui_files.main_dialog import Ui_Dialog as Main_Dialog
import scripts.wallpapertools as w


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

    def resolution(self):
        return f"desired resolution: {int(w.data['img_size'][0]+1)} x {int(w.data['img_size'][1]+1)}px"

    # runs every configuration in order
    def start_setup(self):
        w.load_monitors()
        for screens in w.data['setup_order']:
            for i in range(2):
                dialog = ScaleUI(screens) if i == 0 else GapUI(screens)

                if not dialog.exec():
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


class ScaleUI(QDialog):
    def __init__(self, screens):
        super().__init__()
        self.ui = Scale_Dialog()
        self.ui.setupUi(self)
        self.screens = screens
        self.current_line = 0

        self.ui.btn_up.clicked.connect(lambda: self.move_line(-1))
        self.ui.btn_down.clicked.connect(lambda: self.move_line(1))
        self.ui.btn_next.clicked.connect(self.next)

        self.px_step = 1
        self.ui.slider_px_step.valueChanged.connect(self.set_px_step)

        # radio buttons
        self.radiobuttons = [
            self.ui.radio_blue1,
            self.ui.radio_blue2,
            self.ui.radio_red1,
            self.ui.radio_red2,
        ]
        for i, r in enumerate(self.radiobuttons):
            r.toggled.connect(
                lambda checked, i=i: (
                    setattr(self, 'current_line', i) if checked else None
                )
            )

        self.lines = w.draw_scale_setting(self.screens)

    def move_line(self, val):
        self.lines[self.current_line] += val * self.px_step
        w.draw_scale_setting(self.screens, lines=self.lines)

    def set_px_step(self, val):
        self.px_step = val // 10 + 1
        self.ui.label.setText(f'{self.px_step}px')

    def next(self):
        w.calculate_scale(self.screens, self.lines)
        self.accept()


class GapUI(QDialog):
    def __init__(self, screens):
        super().__init__()
        self.ui = Gap_Dialog()
        self.ui.setupUi(self)
        self.screens = screens

        self.ui.btn_left.clicked.connect(lambda: self.set_gap(1))
        self.ui.btn_right.clicked.connect(lambda: self.set_gap(-1))
        self.ui.btn_next.clicked.connect(self.next)

        self.px_step = 1
        self.ui.slider_px_step.valueChanged.connect(self.set_px_step)

        self.gap = w.draw_gap_setting(self.screens)

    def set_gap(self, val):
        self.gap += val * self.px_step
        w.draw_gap_setting(self.screens, self.gap)

    def set_px_step(self, val):
        self.px_step = val // 10 + 1
        self.ui.label.setText(f'{self.px_step}px')

    def next(self):
        w.save_gap(self.screens, self.gap)
        self.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainUI()
    window.show()
    sys.exit(app.exec())
