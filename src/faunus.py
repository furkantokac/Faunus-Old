#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys, mail, view
from hotspotlinux import Hotspot
from config import * # includes : conf, dirs, encrypt, decrypt, save_conf
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import *

os.chdir(dirs['src'])


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

        if conf['faunus']['num_of_mailbox']:
            self.load_mailbox_settings(self.mailbox, 'mailbox0')
            if conf["mailbox0"]['startup']:
                self.ui.chb_startup_automail.setChecked(True)
                self.ui.chb_automail.setChecked(True)
        else:
            self.ui.chb_automail.setDisabled(True)

        # hotspot things
        self.hotspot = Hotspot(conf['hotspot']['name'], conf['hotspot']['password'], conf['hotspot']['ip'],
                               conf['hotspot']['inet'], conf['hotspot']['wlan'], conf['hotspot']['netmask'])
        self.ui.btn_home_settings_save.clicked.connect(self.hotspot_settings_save)
        self.ui.btn_hotspot_on.clicked.connect(self.hotspot_on)
        self.ui.btn_hotspot_off.clicked.connect(self.hotspot_off)
        if conf['faunus']['sudo_pwd']=='':
            self.ui.btn_hotspot_on.setDisabled(True)
            self.ui.btn_hotspot_off.setDisabled(True)
        else:
            self.ui.lne_hotspot_password.setText(conf['hotspot']['password'])
            self.ui.lne_hotspot_name.setText(conf['hotspot']['name'])
            if conf['hotspot']['startup']:
                self.ui.chb_startup_hotspot.setChecked(True)
                self.ui.btn_hotspot_on.click()

    def hotspot_on(self):
        if self.ui.chb_hotspot_advanced_settings.checkState():
            pass

        self.hotspot.ssid = self.ui.lne_hotspot_name.text()+"_Faunus"
        self.hotspot.password = self.ui.lne_hotspot_password.text()
        conf['hotspot']['name'] = self.ui.lne_hotspot_name.text()
        conf['hotspot']['password'] = self.ui.lne_sudo_password.text()
        save_conf()

        if self.hotspot.verify():
            response = self.hotspot.start( decrypt( conf['faunus']['sudo_pwd'] ) )
            print(response)
            if response==True:
                self.ui.lbl_hotspot_status.setText("ON")
                self.ui.btn_hotspot_off.setDisabled(False)
                self.ui.btn_hotspot_on.setDisabled(True)

    def hotspot_off(self):
        self.ui.btn_hotspot_off.setDisabled(True)
        self.ui.btn_hotspot_on.setDisabled(False)
        self.hotspot.stop(decrypt( conf['faunus']['sudo_pwd'] ))
        self.ui.lbl_hotspot_status.setText("OFF")

    def hotspot_settings_save(self):
        sudo_pwd = self.ui.lne_sudo_password.text()
        sudo_pwd.strip()
        hs = Hotspot()

        if hs.check_sudo_password(sudo_pwd):
            conf["faunus"]["sudo_pwd"] = encrypt(sudo_pwd)
            save_conf()
            self.ui.btn_hotspot_on.setDisabled(False)
        else:
            print("Wrong password. Didn't saved.")

    def handle_new_mail(self, new_mail):
        self.ui.statusBar.showMessage("You have "+str(new_mail)+" new message.", 2000)

    def load_mailbox_settings(self, mailbox, mailbox_id="", uname="", pwd="", imapsw="", imapprt="", smtpsw="",
                              smtpprt=""):
        if uname:
            mailbox.username = uname
            mailbox.password = pwd
            mailbox.imap_server = imapsw
            mailbox.imap_port = imapprt
            # mailbox.smtp_server = smtpsw
            # mailbox.smtp_port = smtpprt
        else:
            mailbox.username = conf[mailbox_id]["username"]
            mailbox.password = decrypt(conf[mailbox_id]["password"])
            mailbox.imap_server = conf[mailbox_id]["imap_server"]
            mailbox.imap_port = conf[mailbox_id]["imap_port"]
            # mailbox.smtp_server = data["smtp_server"]
            # mailbox.smtp_port = data["smtp_port"]

    def save_mail(self):
        tmp_mailbox = mail.MailBox()
        tmp_username = self.ui.lne_username.text()
        tmp_password = self.ui.lne_password.text()
        tmp_imap_server = self.ui.lne_imap_server.text()
        tmp_imap_port = self.ui.lne_imap_port.text()
        tmp_smtp_server = self.ui.lne_smtp_server.text()
        tmp_smtp_port = self.ui.lne_smtp_port.text()
        self.load_mailbox_settings(tmp_mailbox, '', tmp_username, tmp_password, tmp_imap_server, tmp_imap_port,
                                   tmp_smtp_server, tmp_smtp_port)
        response = tmp_mailbox.check_server_response()

        if response!="valid":
            QMessageBox.warning(self, "Connection Error", response+" is not valid. Please check your informations.",
                                QMessageBox.Close)
            return

        mailbox_id = 'mailbox'+str(conf["faunus"]["num_of_mailbox"])
        conf[mailbox_id] = {}
        conf[mailbox_id]["username"] = tmp_username
        conf[mailbox_id]["password"] = encrypt(tmp_password)
        conf[mailbox_id]["imap_server"] = tmp_imap_server
        conf[mailbox_id]["imap_port"] = tmp_imap_port
        conf[mailbox_id]["smtp_server"] = tmp_smtp_server
        conf[mailbox_id]["smtp_port"] = tmp_smtp_port
        conf[mailbox_id]["automail"] = bool(self.ui.chb_automail.checkState())
        conf[mailbox_id]["startup"] = bool(self.ui.chb_startup_automail.checkState())
        conf["faunus"]["num_of_mailbox"] += 1
        save_conf()
        self.load_mailbox_settings(self.mailbox, mailbox_id)
        self.ui.chb_automail.setDisabled(False)
        print("[+] Account successfully saved.")

    def handle_automail(self, state):
        if state:
            self.automail_timer.start(self.automail_freq)
            print("[+] Automail checking started.")
        else:
            self.automail_timer.stop()
            print("[-] Automail checking stopped.")

    def handle_startup_automail(self, state):
        if state:
            conf["mailbox0"]["startup"] = True
            print("[+] Startup automail activated.")
        else:
            conf["mailbox0"]["startup"] = False
            print("[-] Startup automail deactivated.")

        save_conf()


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
    myapp.setWindowIcon(QIcon(dirs["app_icon"]))
    myapp.show()
    sys.exit(app.exec_())
