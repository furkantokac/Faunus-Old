#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys, mail, config, time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class MailChecker(QThread):

    trg = pyqtSignal(str)

    def __init__(self):
        QThread.__init__(self)
        self.mailbox = ""

    def run(self):
        self.check_mail()

    def check_mail(self):
        time.sleep(2)
        new_mail = self.mailbox.check_new_mail()
        self.trg.emit(str(new_mail))

class Example(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        QSystemTrayIcon.showMessage()
        self.mailcheck = MailChecker()
        self.mailcheck.mailbox = mail.MailBox()
        self.mailcheck.mailbox.username = config.get_encypted_data("username")
        self.mailcheck.mailbox.password = config.get_encypted_data("password")
        self.mailcheck.mailbox.server_address = "imap.metu.edu.tr"
        self.mailcheck.mailbox.server_port = "993"
        #QMessageBox.warning(self, "Connection Error",
        #                    "username/password"+" is not valid. Please check your informations and save again.", QMessageBox.Close)
        self.cb = QCheckBox("halo")
        self.cb.stateChanged.connect(self.cb_checked)
        self.mailcheck.trg.connect(self.set_label)

        self.vbl = QVBoxLayout(self)

        self.maillbl = QLabel(self)

        self.mail_timer = QTimer()
        self.freq = 2000

        self.mail_timer.timeout.connect(self.mailcheck.start)
        self.mail_timer.start(self.freq)

        self.setGeometry(300, 300, 280, 170)
        self.setWindowTitle('Tester')

        self.btn = QPushButton("basme")
        self.btn.clicked.connect(self.basildi)

        self.btn.setDisabled(False)

        self.vbl.addWidget(self.maillbl)
        self.vbl.addWidget(self.btn)
        self.vbl.addWidget(self.cb)
        self.cb.setChecked(True)
        print(self.cb.checkState())

    def cb_checked(self):
        current_state= 99
        print(current_state)
        '''if current_state:
            print("po checked")
        else:
            print("wtf no check")'''

    def set_label(self, new_mail):
        self.maillbl.setText("You have, "+str(new_mail)+" new email.")

    def basildi(self):
        print("basildi la")


    def timerEvent(self, e):
        pass


if __name__=='__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec_())
