import sys
from PyQt6.QtWidgets import QDialog, QApplication
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

        if w.load_data():
            self.ui.btn_set_wallpaper.setEnabled(True)
            self.ui.label_info.setText("previous config\nloaded")
            print(w.data)
            w.modify_img()

    # runs every configuration in order
    def start_setup(self):
        for screens in w.data['setup_order']:
            for i in range(2):
                dialog = ScaleUI(screens) if i == 0 else GapUI(screens)

                if not dialog.exec():
                    self.ui.btn_set_wallpaper.setEnabled(False)
                    self.ui.btn_save_png.setEnabled(False)
                    self.ui.label_info.setText("setup canceled\nclick again to retry")
                    return
        
        if w.verify_data(w.data):
            w.save_data()
            self.ui.btn_set_wallpaper.setEnabled(True)
            self.ui.label_info.setText("configuration\nsaved")
            
        else:
            self.ui.label_info.setText("error\nconfig invalid")
        
        
        


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
