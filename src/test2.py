#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import sys, config
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import *

class SystemTrayIcon(QSystemTrayIcon):

    def __init__(self, icon, parent=None):
        super(SystemTrayIcon, self).__init__(icon, parent)
        menu = QMenu(parent)
        exitAction = menu.addAction("Exit")
        exitAction.triggered.connect(parent.close)
        self.setContextMenu(menu)


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Icon')
        print( config.dirs["faunus_icon"] )
        self.tray_icon = SystemTrayIcon(QIcon(config.dirs["faunus_icon"]), self)
        self.tray_icon.show()
        self.show()
        self.tray_icon.showMessage("New Mail!", "You have 1 new mail from aaa", 1)


if __name__ == '__main__':
    app = QApplication([])
    w = MainWindow()
    sys.exit(app.exec_())