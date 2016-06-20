#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys, mail, config, view
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import *


class Faunus(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = view.Ui_Faunus()
        self.ui.setupUi(self)
        self.init_faunus()

    def init_faunus(self):
        # init mail
        self.mailbox = mail.MailBox()
        self.automail_thread = MailThread(self.mailbox)
        self.automail_thread.mailsignal.connect(self.handle_new_mail)
        self.automail_timer = QTimer()
        self.automail_freq = 5000 # check mail once in X second
        self.automail_timer.timeout.connect(self.automail_thread.start)

        self.ui.chb_automail.stateChanged.connect(self.handle_automail)
        self.ui.chb_startup_automail.stateChanged.connect(self.handle_startup_automail)
        self.ui.btn_save_mail.clicked.connect(self.save_mail)

        if config.settings["loged_in"]:
            self.load_mailbox_settings(self.mailbox)
            if config.settings["startup_automail"]:
                self.ui.chb_startup_automail.setChecked(True)
                self.ui.chb_automail.setChecked(True)
        else:
            self.ui.chb_automail.setDisabled(True)

    def handle_new_mail(self, new_mail):
        self.ui.statusBar.showMessage("You have "+str(new_mail)+" new message.", 2000)

    def load_mailbox_settings(self, mailbox):
        mailbox.username = config.data["username"]
        mailbox.password = config.get_encypted_data("password")
        mailbox.imap_server= config.data["imap_server"]
        mailbox.imap_port = config.data["imap_port"]

    def save_mail(self):
        self.ui.chb_automail.setChecked(False)
        self.ui.chb_automail.setDisabled(True)
        config.data["username"] = self.ui.lne_username.text()
        config.set_encrypted_data("password", self.ui.lne_password.text())
        config.data["imap_server"] = self.ui.lne_imap_server.text()
        config.data["imap_port"] = self.ui.lne_imap_port.text()
        config.data["pop3_server"] = self.ui.lne_pop3_server.text()
        config.data["pop3_port"] = self.ui.lne_pop3_port.text()
        self.load_mailbox_settings(self.mailbox)
        response = self.mailbox.check_server_response()

        if response!="valid":
            QMessageBox.warning(self, "Connection Error",
                                response+" is not valid. Please check your informations.",
                                QMessageBox.Close)
            return

        config.settings["loged_in"] = True
        config.settings["automail"] = bool(self.ui.chb_automail.checkState())
        config.settings["startup_automail"] = bool(self.ui.chb_startup_automail.checkState())
        config.save_data()
        config.save_settings()
        self.load_mailbox_settings(self.mailbox)
        self.ui.chb_automail.setDisabled(False)
        print("Account successfully saved.")

    def handle_automail(self, state):
        if state:
            self.automail_timer.start(self.automail_freq)
            print("Automail checking started.")
        else:
            self.automail_timer.stop()
            print("Automail checking stopped.")

    def handle_startup_automail(self, state):
        if state:
            config.settings["startup_automail"] = True
            print("Startup automail activated.")
        else:
            config.settings["startup_automail"] = False
            print("Startup automail deactivated.")

        config.save_settings()


class MailThread(QThread):
    mailsignal = pyqtSignal(int)

    def __init__(self, mailbox):
        QThread.__init__(self)

        self.mailbox = mailbox

    def run(self):
        self.check_mail()

    def check_mail(self):
        new_mail = self.mailbox.check_new_mail()
        self.mailsignal.emit(new_mail)


if __name__=="__main__":
    app = QApplication(sys.argv)
    myapp = Faunus()
    myapp.setWindowIcon(QIcon(config.dirs["faunus_icon"]))
    myapp.show()
    sys.exit(app.exec_())
