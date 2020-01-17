from PyQt5.QtWidgets import QTabWidget, QMainWindow, QDesktopWidget, QApplication
import sys
from ui_basic import Ui_basic
from ui_userDefine import Ui_userDefine

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1200, 750)
        self.center()
        self.setWindowTitle('Maze')

        self.tabW = QTabWidget(parent=self)
        ui_userD = Ui_userDefine()
        ui_basic = Ui_basic()

        self.tabW.addTab(ui_basic, "已有迷宫")
        self.tabW.addTab(ui_userD, "用户自定义")
        self.tabW.resize(1200,750)
        ui_basic.initUI()
        ui_userD.initUI()

        self.show()

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
                  (screen.height() - size.height()) / 2)

if __name__ == "__main__":
    app = QApplication([])
    ui = MainWindow()
    sys.exit(app.exec_())